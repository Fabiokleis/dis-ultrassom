"""Testes unitários para o algoritmo CGNE"""
import pytest
import numpy as np
from server.cgne import cgne


def test_cgne_deve_convergir_e_reconstruir_imagem_corretamente():
    """
    CGNE deve convergir e reconstruir a imagem corretamente
    Equivalente ao teste C++ em test_cgne.cpp linha 4-17
    """
    N = 10
    S = 20
    
    np.random.seed(42)
    H = np.random.rand(S, N)
    f_real = np.random.rand(N) * 10.0
    g_simulado = H @ f_real
    
    f_calculado, iterations = cgne(H, g_simulado, tol=1e-4, max_iter=11)
    
    erro_reconstrucao = np.linalg.norm(f_real - f_calculado, 2)
    
    # Mesmo threshold do teste C++
    assert erro_reconstrucao < 1e-4, f"Erro: {erro_reconstrucao} (esperado < 1e-4)"
