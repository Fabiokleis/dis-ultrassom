from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import FileResponse
from pathlib import Path
import numpy as np
from datetime import datetime
import time

from server.models import (
    Algorithm,
    SignalModel,
    ReconstructionMetadata,
)
from server.cgne import cgne
from server.cgnr import cgnr
from server.image_generator import save_png
from server.signal_gain import apply_signal_gain

app = FastAPI(
    title="Ultrassom Image Reconstruction API",
    description="API para reconstrução de imagens de ultrassom usando CGNE/CGNR",
    version="1.0.0"
)

# Diretório de dados
DATA_DIR = Path(".")
IMAGES_DIR = Path("imagens")
IMAGES_DIR.mkdir(exist_ok=True)


def load_model_matrix(signal_id: SignalModel) -> np.ndarray:
    """Carrega a matriz modelo H correspondente ao signal_id"""
    matrix_name = signal_id.get_model_matrix()
    matrix_path = DATA_DIR / f"{matrix_name}.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Arquivo de matriz modelo não encontrado: {matrix_name}.csv")
    return np.loadtxt(matrix_path, delimiter=",")


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Ultrassom Image Reconstruction API"}


@app.get("/opa")
def opa():
    return {"message": "opa"}


@app.post("/ultrassom", response_model=ReconstructionMetadata)
def reconstruct_image(
    signal_id: SignalModel = Query(..., description="ID do sinal para determinar qual matriz H usar"),
    algorithm: Algorithm = Query(..., alias="alg", description="Algoritmo de reconstrução"),
    gain: bool = Query(False, description="Aplicar ganho de sinal (gamma)"),
    signal: list[float] = Body(..., description="Vetor de sinais G (CSV no body)")
):
    """
    Processa uma reconstrução de imagem de forma síncrona.
    
    Args:
        signal_id: ID do sinal (G-1 a G-6) para determinar qual modelo H usar
        algorithm: Algoritmo (cgne ou cgnr)
        gain: Se True, aplica ganho γ_l = 100 + (1/20) * l * sqrt(l) ao sinal
        signal: Vetor de sinais G enviado no body como array JSON
    
    Returns:
        ReconstructionMetadata com metadados da reconstrução
    """
    start_time = datetime.now()
    start_ms = time.time()
    
    try:
        # Converter signal para numpy array
        g = np.array(signal)
        
        # Aplicar ganho se solicitado
        if gain:
            g = apply_signal_gain(g)
        
        # Carregar matriz modelo H correspondente ao signal_id
        H = load_model_matrix(signal_id)
        
        # Validar dimensões
        if H.shape[0] != g.shape[0]:
            raise ValueError(
                f"Dimensões incompatíveis: H tem {H.shape[0]} linhas mas g tem {g.shape[0]} elementos"
            )
        
        # Executar algoritmo
        if algorithm == Algorithm.CGNE:
            f, iterations = cgne(H, g, tol=1e-4, max_iter=10)
        else:
            f, iterations = cgnr(H, g, tol=1e-4, max_iter=10)
        
        # Calcular dimensões da imagem (assumindo quadrada)
        side = int(np.sqrt(f.shape[0]))
        
        # Gerar nome único para imagem usando timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        image_filename = f"{signal_id.value}_{algorithm.value}_{timestamp}.png"
        image_path = IMAGES_DIR / image_filename
        save_png(f, side, side, str(image_path))
        
        end_time = datetime.now()
        end_ms = time.time()
        duration_ms = (end_ms - start_ms) * 1000
        
        return ReconstructionMetadata(
            job_id=timestamp,
            signal_id=signal_id.value,
            model_matrix=signal_id.get_model_matrix(),
            algorithm=algorithm.value,
            iterations=iterations,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            image_width=side,
            image_height=side,
            image_path=str(image_path)
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar reconstrução: {str(e)}")


@app.get("/imagens")
def list_images():
    """
    Lista todas as imagens processadas.
    
    Returns:
        Dict com total de imagens e lista de nomes de arquivos
    """
    try:
        # Listar todos arquivos PNG no diretório de imagens
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
    """
    Faz download de uma imagem específica.
    
    Args:
        filename: Nome do arquivo PNG (ex: G-1_cgne_20260617_012345_123456.png)
    
    Returns:
        FileResponse com o arquivo PNG
    """
    # Validar que o filename é apenas o nome do arquivo (sem path traversal)
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
    
    # Verificar extensão
    if not filename.endswith(".png"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PNG são permitidos")
    
    image_path = IMAGES_DIR / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Imagem não encontrada: {filename}")
    
    return FileResponse(
        path=image_path,
        media_type="image/png",
        filename=filename
    )

