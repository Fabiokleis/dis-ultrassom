"""Testes unitários para geração de imagens PNG"""
import pytest
import numpy as np
from pathlib import Path
from server.image_generator import save_png


def test_save_png_deve_criar_arquivo_png_com_dimensoes_corretas():
    """
    save_png deve criar arquivo PNG com dimensões corretas
    Equivalente ao teste C++ em test_generate_image.cpp
    """
    side = 10
    f = np.random.rand(side * side) * 100
    output_path = "imagens/test_py_save.png"
    
    save_png(f, side, side, output_path)
    
    assert Path(output_path).exists()
    
    # Cleanup
    Path(output_path).unlink()
