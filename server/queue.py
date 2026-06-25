import os
import time
from datetime import datetime
from multiprocessing import Lock, Manager, Process, Queue as MPQueue
from multiprocessing import shared_memory
from pathlib import Path

import numpy as np

from server.cgne import cgne
from server.cgnr import cgnr
from server.image_generator import save_png
from server.metrics import MetricsCollector
from server.models import (
    AlgorithmModel,
    JobResult,
    JobStatus,
    ReconstructionMetadata,
    ScaleModel,
    SignalModel,
)
from server.report import ReportRow, ReportWriter
from server.signal_gain import apply_signal_gain

DATA_DIR = Path(".")
IMAGES_DIR = Path("imagens")
IMAGES_DIR.mkdir(exist_ok=True)


def load_model_matrix(scale: ScaleModel) -> np.ndarray:
    """Carrega a matriz modelo H correspondente ao signal_id"""
    matrix_name = scale.get_model_matrix()
    matrix_path = DATA_DIR / f"{matrix_name}.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(
            f"Arquivo de matriz modelo não encontrado: {matrix_name}.csv"
        )
    return np.loadtxt(matrix_path, delimiter=",")


class JobDB:
    def __init__(self, manager=None):
        if manager:
            self._jobs = manager.dict()
            self._lock = manager.Lock()
            self._counter = 0
        else:
            self._jobs = {}
            self._lock = None
            self._counter = 0

    def create_job(self) -> int:
        if self._lock:
            with self._lock:
                self._counter += 1
                job_id = self._counter
        else:
            self._counter += 1
            job_id = self._counter
        
        self._jobs[job_id] = JobResult(job_id=job_id, status=JobStatus.PENDING)
        return job_id

    def get_job(self, job_id: int) -> JobResult | None:
        return self._jobs.get(job_id)

    def update_job(
        self,
        job_id: int,
        status: JobStatus,
        metadata: ReconstructionMetadata | None = None,
        error: str | None = None,
    ):
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.status = status
            if metadata:
                job.metadata = metadata
            if error:
                job.error = error
            self._jobs[job_id] = job


def worker_process(
    worker_id: int,
    jobs_queue: MPQueue,
    job_db: JobDB,
    report_path: str,
    num_workers: int,
    shm_info: dict,
):
    """Funcao executada por cada processo worker"""
    import signal
    
    # Ignora SIGINT no worker (deixa o processo pai lidar)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    report_writer = ReportWriter(report_path)
    metrics_collector = MetricsCollector()
    
    # Abre shared memory e cria arrays numpy apontando para ela
    shm_30 = shared_memory.SharedMemory(name=shm_info['shm_name_30'])
    shm_60 = shared_memory.SharedMemory(name=shm_info['shm_name_60'])
    
    H_30 = np.ndarray(
        shm_info['shape_30'], 
        dtype=np.float64, 
        buffer=shm_30.buf
    )
    H_60 = np.ndarray(
        shm_info['shape_60'], 
        dtype=np.float64, 
        buffer=shm_60.buf
    )
    
    print(f"[Worker {worker_id}] attached to shared memory")
    
    while True:
        try:
            job_data = jobs_queue.get(timeout=1)
        except:
            # Timeout ou erro - verifica se deve continuar
            continue

        if job_data is None:
            break

        print(f"[Worker {worker_id} ]")
        job_id, signal_id, scale, algorithm, gain, file_content = job_data

        try:
            job_db.update_job(job_id, JobStatus.PROCESSING)
            start_time = datetime.now()
            start_ms = time.time()

            metrics = metrics_collector.collect(num_workers)

            text_data = file_content.decode("utf-8").replace("\n", ",")
            g = np.fromstring(text_data, sep=",")

            if gain:
                g = apply_signal_gain(g)

            # Usa matriz H do shared memory (zero cópia!)
            if scale.value == 30:
                H = H_30
            else:
                H = H_60

            if H.shape[0] != g.shape[0]:
                raise ValueError(
                    f"Dimensões incompatíveis: H tem {H.shape[0]} linhas mas g tem {g.shape[0]} elementos"
                )

            if algorithm == AlgorithmModel.CGNE:
                f, iterations = cgne(H, g, tol=1e-4, max_iter=10)
            else:
                f, iterations = cgnr(H, g, tol=1e-4, max_iter=10)

            side = int(np.sqrt(f.shape[0]))
            timestamp = start_time.strftime("%Y%m%d_%H%M%S_%f")
            image_filename = f"{signal_id.value}_{algorithm.value}_{timestamp}.png"
            image_path = IMAGES_DIR / image_filename

            save_png(f, side, side, str(image_path))

            end_time = datetime.now()
            end_ms = time.time()
            duration_ms = (end_ms - start_ms) * 1000

            metadata = ReconstructionMetadata(
                job_id=job_id,
                signal_id=signal_id,
                scale=scale,
                model_matrix=scale.get_model_matrix(),
                algorithm=algorithm,
                iterations=iterations,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                image_width=side,
                image_height=side,
                image_path=str(image_path),
            )
            job_db.update_job(job_id, JobStatus.COMPLETED, metadata=metadata)
            print(f"[Worker {worker_id}] completed image reconstruction")

            row = ReportRow.from_job(metadata, metrics, JobStatus.COMPLETED, gain)
            report_writer.write_row(row)

        except Exception as e:
            print(f"[Worker {worker_id}] failed {job_id}: {e}")
            job_db.update_job(job_id, JobStatus.FAILED, error=str(e))

            row = ReportRow.from_error(job_id, str(e), metrics, start_time)
            report_writer.write_row(row)

    # Cleanup shared memory (apenas close, não unlink)
    shm_30.close()
    shm_60.close()
    print(f"[Worker {worker_id}] stopped.")


class ReconstructionDispatcher:
    def __init__(self, report_path: str = None):
        self.manager = Manager()
        self.jobs_queue = MPQueue()  # Queue nativo, não do Manager
        self.job_db = JobDB(manager=self.manager)
        self.workers: list[Process] = []
        
        if report_path is None:
            report_path = os.environ.get("REPORT_FILE", "reconstruction_report.csv")
        self.report_path = report_path
        self.report_writer = ReportWriter(report_path)
        
        # Inicializa shared memory para matrizes H
        self.shm_30 = None
        self.shm_60 = None
        self.shm_info = None

    def start(self):
        # Carrega matrizes H e cria shared memory
        print("loading model matrices into shared memory...")
        H_30 = load_model_matrix(ScaleModel(30))
        H_60 = load_model_matrix(ScaleModel(60))
        
        # Cria shared memory
        self.shm_30 = shared_memory.SharedMemory(
            create=True, 
            size=H_30.nbytes
        )
        self.shm_60 = shared_memory.SharedMemory(
            create=True, 
            size=H_60.nbytes
        )
        
        # Copia dados para shared memory
        shm_H_30 = np.ndarray(H_30.shape, dtype=H_30.dtype, buffer=self.shm_30.buf)
        shm_H_30[:] = H_30[:]
        shm_H_60 = np.ndarray(H_60.shape, dtype=H_60.dtype, buffer=self.shm_60.buf)
        shm_H_60[:] = H_60[:]
        
        # Informações para passar aos workers
        self.shm_info = {
            'shm_name_30': self.shm_30.name,
            'shm_name_60': self.shm_60.name,
            'shape_30': H_30.shape,
            'shape_60': H_60.shape,
        }
        
        print(f"  H(30): {H_30.shape} = {H_30.nbytes / 1024 / 1024:.2f} MB")
        print(f"  H(60): {H_60.shape} = {H_60.nbytes / 1024 / 1024:.2f} MB")
        
        num_workers = int(os.environ.get("NUM_WORKERS", os.cpu_count() or 4))
        print(f"starting worker pool with {num_workers} workers...")
        for i in range(num_workers):
            worker = Process(
                target=worker_process,
                args=(i, self.jobs_queue, self.job_db, self.report_path, num_workers, self.shm_info),
                daemon=True,
            )
            worker.start()
            self.workers.append(worker)

    def submit_job(
        self,
        signal_id: SignalModel,
        algorithm: AlgorithmModel,
        scale: ScaleModel,
        gain: bool,
        file_content: bytes,
    ) -> int:
        job_id = self.job_db.create_job()
        self.jobs_queue.put(
            (job_id, signal_id, scale, algorithm, gain, file_content)
        )
        return job_id

    def stop_all(self):
        # Envia sinal de parada para todos workers
        for _ in self.workers:
            try:
                self.jobs_queue.put(None, timeout=1)
            except:
                pass
        
        # Aguarda finalização com timeout
        for worker in self.workers:
            worker.join(timeout=2)
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=1)
        
        # Cleanup shared memory
        if self.shm_30:
            try:
                self.shm_30.close()
                self.shm_30.unlink()
            except:
                pass
        
        if self.shm_60:
            try:
                self.shm_60.close()
                self.shm_60.unlink()
            except:
                pass
        
        # Limpa o manager
        try:
            self.manager.shutdown()
        except:
            pass
