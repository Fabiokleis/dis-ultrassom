"""
Geração de imagem PNG a partir de vetor reconstruído
"""
from pathlib import Path

import numpy as np
from PIL import Image


def save_png(f: np.ndarray, width: int, height: int, path: str) -> None:
    """
    Salva vetor reconstruído como imagem PNG em escala de cinza
    
    Args:
        f: Vetor de imagem reconstruída (deve ter width * height elementos)
        width: Largura da imagem em pixels
        height: Altura da imagem em pixels
        path: Caminho do arquivo PNG a ser salvo
    """
    f_abs = np.abs(f)
    
    f_min = f_abs.min()
    f_max = f_abs.max()
    
    if f_max != f_min:
        normalized = (f_abs - f_min) / (f_max - f_min) * 255.0
    else:
        normalized = np.zeros_like(f_abs)
    
    pixels = normalized.astype(np.uint8)
    
    img_array = pixels.reshape(height, width)
    
    img = Image.fromarray(img_array, mode='L')  # 'L' = grayscale
    
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    img.save(path)
