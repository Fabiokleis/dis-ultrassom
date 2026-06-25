"""Coleta de métricas de sistema para análise de performance"""

from dataclasses import dataclass

import psutil


@dataclass
class SystemMetrics:
    """Métricas de sistema capturadas durante processamento"""

    cpu_percent: float
    ram_mb: float
    num_workers: int

    def __repr__(self) -> str:
        return f"CPU: {self.cpu_percent:.1f}%, RAM: {self.ram_mb:.1f}MB, Workers: {self.num_workers}"


class MetricsCollector:
    """Coletor de métricas de sistema"""

    def __init__(self, process: psutil.Process | None = None):
        self.process = process or psutil.Process()

    def collect(self, num_workers: int) -> SystemMetrics:
        cpu_percent = self.process.cpu_percent(interval=0.1)
        memory_info = self.process.memory_info()
        ram_mb = memory_info.rss / (1024 * 1024)

        return SystemMetrics(
            cpu_percent=cpu_percent, ram_mb=ram_mb, num_workers=num_workers
        )
