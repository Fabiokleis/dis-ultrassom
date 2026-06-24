import os
import time
import numpy as np
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Thread

from server.models import (
    JobResult, JobStatus, ReconstructionMetadata, 
    AlgorithmModel, SignalModel, ScaleModel
)
from server.cgne import cgne
from server.cgnr import cgnr
from server.image_generator import save_png
from server.signal_gain import apply_signal_gain

DATA_DIR = Path(".")
IMAGES_DIR = Path("imagens")
IMAGES_DIR.mkdir(exist_ok=True)

def load_model_matrix(scale: ScaleModel) -> np.ndarray:
    """Carrega a matriz modelo H correspondente ao signal_id"""
    matrix_name = scale.get_model_matrix()
    matrix_path = DATA_DIR / f"{matrix_name}.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Arquivo de matriz modelo não encontrado: {matrix_name}.csv")
    return np.loadtxt(matrix_path, delimiter=",")


class JobDB:
    def __init__(self):
        self._jobs: dict[int, JobResult] = {}
        self._counter: int = 0

    def create_job(self) -> int:
        self._counter += 1
        job_id = self._counter
        self._jobs[job_id] = JobResult(job_id=job_id, status=JobStatus.PENDING)
        return job_id

    def get_job(self, job_id: int) -> JobResult | None:
        return self._jobs.get(job_id)

    def update_job(self, job_id: int, status: JobStatus, 
                   metadata: ReconstructionMetadata | None = None, 
                   error: str | None = None):
        if job_id in self._jobs:
            self._jobs[job_id].status = status
            if metadata:
                self._jobs[job_id].metadata = metadata
            if error:
                self._jobs[job_id].error = error

class ReconstructionWorker:
    def __init__(self, worker_id: int, jobs_queue: Queue, job_db: JobDB):
        self.worker_id = worker_id
        self.jobs_queue = jobs_queue
        self.job_db = job_db
        self.running = True
        self.thread = Thread(target=self.exec, daemon=True)
        self.thread.start()

    def exec(self):
        print(f"[Worker {self.worker_id}] waiting...")
        while self.running:
            job_data = self.jobs_queue.get()
            
            if job_data is None:
                self.jobs_queue.task_done()
                break

            print(f"[Worker {self.worker_id} ]")
            job_id, signal_id, scale, algorithm, gain, file_content = job_data
            
            try:
                self.job_db.update_job(job_id, JobStatus.PROCESSING)
                start_time = datetime.now()
                start_ms = time.time()
                
                text_data = file_content.decode("utf-8").replace('\n', ',')
                g = np.fromstring(text_data, sep=',')
                
                if gain:
                    g = apply_signal_gain(g)
                    
                H = load_model_matrix(scale)
                
                if H.shape[0] != g.shape[0]:
                    raise ValueError(f"Dimensões incompatíveis: H tem {H.shape[0]} linhas mas g tem {g.shape[0]} elementos")
                    
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
                    image_path=str(image_path)
                )
                self.job_db.update_job(job_id, JobStatus.COMPLETED, metadata=metadata)
                print(f"[Worker {self.worker_id}] completed image reconstruction")
                
            except Exception as e:
                print(f"[Worker {self.worker_id}] failed {job_id}: {e}")
                self.job_db.update_job(job_id, JobStatus.FAILED, error=str(e))
            finally:
                self.jobs_queue.task_done()
                
        print(f"[Worker {self.worker_id}] stopped.")


class ReconstructionDispatcher:
    def __init__(self):
        self.jobs_queue: Queue = Queue()
        self.job_db = JobDB()
        self.workers: list[ReconstructionWorker] = []

    def start(self):
        num_workers = os.cpu_count() or 4
        for i in range(num_workers):
            self.workers.append(ReconstructionWorker(i, self.jobs_queue, self.job_db))
            
    def submit_job(self, signal_id: SignalModel, algorithm: AlgorithmModel, scale: ScaleModel, gain: bool, file_content: bytes) -> int:
        job_id = self.job_db.create_job()
        self.jobs_queue.put((job_id, signal_id, scale, algorithm, gain, file_content))
        return job_id
    
    def stop_all(self):
        for _ in self.workers:
            self.jobs_queue.put(None)
        for worker in self.workers:
            worker.thread.join()
