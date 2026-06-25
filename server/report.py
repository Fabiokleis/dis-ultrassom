"""Writer de relatórios CSV com métricas de reconstrução"""

import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from multiprocessing import Lock

from server.metrics import SystemMetrics
from server.models import JobStatus, ReconstructionMetadata


@dataclass
class ReportRow:
    """Representa uma linha do relatório CSV"""

    job_id: int
    signal_id: int
    scale: int
    model_matrix: str
    algorithm: int
    gain: bool
    iterations: int
    duration_ms: float
    start_time: str
    end_time: str
    cpu_percent: float
    ram_mb: float
    num_workers: int
    status: str
    error: str
    image_path: str

    @classmethod
    def from_job(
        cls,
        metadata: ReconstructionMetadata,
        metrics: SystemMetrics,
        status: JobStatus,
        gain: bool,
        error: str | None = None,
    ) -> "ReportRow":
        """Cria ReportRow a partir dos dados do job"""
        return cls(
            job_id=metadata.job_id,
            signal_id=metadata.signal_id,
            scale=metadata.scale,
            model_matrix=metadata.model_matrix,
            algorithm=metadata.algorithm,
            gain=gain,
            iterations=metadata.iterations,
            duration_ms=metadata.duration_ms or 0.0,
            start_time=metadata.start_time.isoformat(),
            end_time=metadata.end_time.isoformat() if metadata.end_time else "",
            cpu_percent=metrics.cpu_percent,
            ram_mb=metrics.ram_mb,
            num_workers=metrics.num_workers,
            status=status.value,
            error=error or "",
            image_path=metadata.image_path,
        )

    @classmethod
    def from_error(
        cls,
        job_id: int,
        error: str,
        metrics: SystemMetrics,
        start_time: datetime | None = None,
    ) -> "ReportRow":
        """Cria ReportRow para job que falhou"""
        now = datetime.now()
        return cls(
            job_id=job_id,
            signal_id=0,
            scale=0,
            model_matrix="",
            algorithm=0,
            gain=False,
            iterations=0,
            duration_ms=0.0,
            start_time=start_time.isoformat()
            if start_time
            else now.isoformat(),
            end_time=now.isoformat(),
            cpu_percent=metrics.cpu_percent,
            ram_mb=metrics.ram_mb,
            num_workers=metrics.num_workers,
            status=JobStatus.FAILED.value,
            error=error,
            image_path="",
        )


class ReportWriter:
    """Writer thread-safe para relatórios CSV de reconstrução"""

    def __init__(self, filepath: str = "reconstruction_report.csv"):
        self.filepath = Path(filepath)
        self.lock = Lock()
        self.fieldnames = [f.name for f in fields(ReportRow)]
        self._initialize_file()

    def _initialize_file(self):
        """Cria arquivo CSV com header se não existir"""
        if not self.filepath.exists():
            with open(self.filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def write_row(self, row: ReportRow):
        """Escreve uma linha no CSV (thread-safe)"""
        with self.lock:
            with open(self.filepath, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(asdict(row))
