from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

from server.models import (
    AlgorithmModel,
    SignalModel,
    ScaleModel,
    JobResponse,
    JobStatus,
    JobResult
)
from server.queue import ReconstructionDispatcher 
import numpy as np

np.show_config()

dispatcher = ReconstructionDispatcher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting worker pool...")
    dispatcher.start()
    yield
    print("stopping worker pool...")
    dispatcher.stop_all()

app = FastAPI(
    title="Ultrassom Image Reconstruction API",
    description="API para reconstrução de imagens de ultrassom usando CGNE/CGNR",
    version="1.0.0",
    lifespan=lifespan
)

IMAGES_DIR = Path("imagens")

@app.get("/opa")
def opa():
    return {"message": "opa"}

@app.post("/ultrassom", response_model=JobResponse)
async def submit_reconstruction(
    signal_id: SignalModel = Query(..., description="ID do sinal"),
    scale: ScaleModel = Query(..., description="Escala 30 ou 60"),
    algorithm: AlgorithmModel = Query(..., description="Algoritmo de reconstrução"),
    gain: bool = Query(False, description="Aplicar ganho de sinal (gamma)"),
    signal: UploadFile = File(..., description="Arquivo CSV com vetor de sinais G")
):
    """Submete o sinal para processamento na fila e retorna o ID do Job."""
    signal_data = await signal.read()
    
    job_id = dispatcher.submit_job(signal_id, algorithm, scale, gain, signal_data)
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Trabalho de reconstrução enviado para a fila."
    )

@app.get("/jobs/{job_id}", response_model=JobResult)
def get_job_status(job_id: int):
    """Consulta o status no Dispatcher."""
    job = dispatcher.job_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return job

@app.get("/imagens")
def list_images():
    """Lista todas as imagens processadas."""
    try:
        image_files = sorted(IMAGES_DIR.glob("*.png"))
        
        images_info = []
        for img_path in image_files:
            stat = img_path.stat()
            images_info.append({
                "filename": img_path.name,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "url": f"/imagens/{img_path.name}"
            })
        
        return {
            "total": len(images_info),
            "images": images_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar imagens: {str(e)}")

@app.get("/imagens/{filename}")
def download_image(filename: str):
    """Faz download de uma imagem específica."""
    image_path = IMAGES_DIR / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Imagem não encontrada: {filename}")
    
    return FileResponse(
        path=image_path,
        media_type="image/png",
        filename=filename
    )
