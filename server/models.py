"""Modelos de dados e tipos para a API"""
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Algorithm(str, Enum):
    """Algoritmos de reconstrução disponíveis"""
    CGNE = "cgne"
    CGNR = "cgnr"


class SignalModel(str, Enum):
    """
    Enumeração de sinais disponíveis e suas matrizes modelo correspondentes.
    
    Nomenclatura: G{n} → H{m}
    - G-1, G-2, G-3 → H-1
    - G-4, G-5, G-6 → H-2
    """
    G1 = "G-1"
    G2 = "G-2"
    G3 = "G-3"
    G4 = "G-4"
    G5 = "G-5"
    G6 = "G-6"
    
    def get_model_matrix(self) -> str:
        """Retorna o nome da matriz modelo correspondente"""
        if self in (SignalModel.G1, SignalModel.G2, SignalModel.G3):
            return "H-1"
        else:
            return "H-2"


class JobStatus(str, Enum):
    """Status de processamento de um job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReconstructionRequest(BaseModel):
    """Requisição de reconstrução de imagem"""
    signal_id: SignalModel = Field(..., description="ID do sinal (G-1 a G-6)")
    algorithm: Algorithm = Field(..., description="Algoritmo de reconstrução (cgne ou cgnr)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "signal_id": "G-1",
                "algorithm": "cgne"
            }
        }


class ReconstructionMetadata(BaseModel):
    """Metadados de uma reconstrução"""
    job_id: str
    signal_id: str
    model_matrix: str
    algorithm: str
    iterations: int
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None
    image_width: int
    image_height: int
    image_path: str


class JobResponse(BaseModel):
    """Resposta ao submeter um job"""
    job_id: str
    status: JobStatus
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "message": "Job criado e aguardando processamento"
            }
        }


class JobResult(BaseModel):
    """Resultado de um job de reconstrução"""
    job_id: str
    status: JobStatus
    metadata: ReconstructionMetadata | None = None
    error: str | None = None
