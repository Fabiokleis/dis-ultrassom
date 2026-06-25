from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from server.models import (
    AlgorithmModel,
    JobResponse,
    JobResult,
    JobStatus,
    ScaleModel,
    SignalModel,
)
from server.queue import ReconstructionDispatcher

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


app.mount("/static", StaticFiles(directory="static"), name="static")

IMAGES_DIR = Path("imagens")
REPORT_CSV = Path("reconstruction_report.csv")

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

@app.get("/report", response_class=HTMLResponse)
def get_report_page():
    """Serve a página HTML do relatório."""
    html_path = Path("static/index.html")
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Página de relatório não encontrada")
    
    return FileResponse(html_path)

@app.get("/report/data")
def get_report_data():
    """Retorna dados das reconstruções do arquivo reconstruction_report.csv."""
    try:
        if not REPORT_CSV.exists():
            return {"reconstructions": []}
        
        # Lê o CSV de relatório
        df = pd.read_csv(REPORT_CSV)
        
        # Filtra apenas completados
        df_completed = df[df['status'] == 'completed'].copy()
        
        if len(df_completed) == 0:
            return {"reconstructions": []}
        
        # Prepara dados
        df_completed['duration_s'] = df_completed['duration_ms'] / 1000
        df_completed['image_filename'] = df_completed['image_path'].apply(
            lambda x: Path(x).name if pd.notna(x) else None
        )
        
        # Dados das reconstruções
        reconstructions = []
        for _, row in df_completed.iterrows():
            reconstructions.append({
                "job_id": int(row['job_id']),
                "signal_id": int(row['signal_id']),
                "scale": int(row['scale']),
                "algorithm": int(row['algorithm']),
                "gain": bool(row['gain']),
                "iterations": int(row['iterations']),
                "duration_s": float(row['duration_s']),
                "num_workers": int(row['num_workers']),
                "image_filename": row['image_filename']
            })
        
        return {"reconstructions": reconstructions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler relatório: {str(e)}")
