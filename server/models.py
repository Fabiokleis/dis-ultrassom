"""Modelos de dados e tipos para a API"""
import random
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlgorithmModel(int, Enum):
    """Algoritmos de reconstrução disponíveis"""
    CGNE = 1
    CGNR = 2

    @classmethod
    def random_choice(cls):
        return random.choice(list(cls))

class ScaleModel(int, Enum):
    """
    Enumeraação das Escalas suportadas 30 e 60

    Nomenclatura: S{n} → H{m}
    - S-1 → H-1
    - S-2 → H-2
    """
    S1 = 30
    S2 = 60

    @classmethod
    def random_choice(cls):
        return random.choice(list(cls))
    
    def get_model_matrix(self) -> str:
        """Retorna o nome da matriz modelo correspondente"""
        if self == ScaleModel.S1:
            return "H-1"
        else:
            return "H-2"
    
class SignalModel(int, Enum):
    """
    Enumeração de sinais disponíveis.
    """
    G1 = 1
    G2 = 2
    G3 = 3
    
    @classmethod
    def random_choice(cls):
        return random.choice(list(cls))


class JobStatus(str, Enum):
    """Status de processamento de um job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReconstructionRequest(BaseModel):
    """Requisição de reconstrução de imagem"""
    signal_id: SignalModel = Field(..., description="ID do sinal (1-2-3)")
    algorithm: AlgorithmModel = Field(..., description="Algoritmo de reconstrução (cgne ou cgnr)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "signal_id": 1,
                "algorithm": "cgne"
            }
        }


class ReconstructionMetadata(BaseModel):
    """Metadados de uma reconstrução"""
    job_id: int
    signal_id: int
    scale: int
    model_matrix: str
    algorithm: int
    iterations: int
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None
    image_width: int
    image_height: int
    image_path: str
    
class JobResponse(BaseModel):
    """Resposta ao submeter um job"""
    job_id: int
    status: JobStatus
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": 1,
                "status": "pending",
                "message": "Job criado e aguardando processamento"
            }
        }


class JobResult(BaseModel):
    """Resultado de um job de reconstrução"""
    job_id: int
    status: JobStatus
    metadata: ReconstructionMetadata | None = None
    error: str | None = None
