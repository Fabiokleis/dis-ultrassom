"""
Algoritmo CGNR (Conjugate Gradient Normal Residual)
Implementado com NumPy (usa BLAS/LAPACK como Armadillo)
"""
import numpy as np
from typing import Tuple


def cgnr(H: np.ndarray, g: np.ndarray, tol: float = 1e-4, max_iter: int = 10) -> Tuple[np.ndarray, int]:
    """
    Algoritmo CGNR (Conjugate Gradient Normal Residual)
    
    Pseudocódigo:
    f0 = 0
    r0 = g − H*f0
    z0 = H^T * r0
    p0 = z0
    
    for i=0,1,...,until convergence
      wi = H * pi
      αi = ||zi||^2_2 / ||wi||^2_2
      fi+1 = fi + αi * pi
      ri+1 = ri − αi * wi
      zi+1 = H^T * ri+1
      βi = ||zi+1||^2_2 / ||zi||^2_2
      pi+1 = zi+1 + βi * pi
    
    Args:
        H: Matriz modelo (m x n) - representa o sistema de aquisição
        g: Vetor de sinal (m,) - sinais medidos
        tol: Tolerância para convergência (default: 1e-4)
        max_iter: Número máximo de iterações (default: 10)
    
    Returns:
        Tuple[np.ndarray, int]: (vetor reconstruído f, número de iterações executadas)
    """
    n = H.shape[1]
    f = np.zeros(n)  # Vetor solução inicial
    r = g - H @ f    # Resíduo inicial
    z = H.T @ r      # Gradiente
    p = z.copy()     # Direção de busca inicial
    
    norma_r_atual = np.linalg.norm(r, 2)
    iterations_done = 0
    
    for i in range(max_iter):
        iterations_done = i + 1
        
        w = H @ p
        
        z_norm_sq = np.dot(z, z)
        w_norm_sq = np.dot(w, w)
        
        alpha = z_norm_sq / w_norm_sq
        
        f = f + alpha * p  # Atualiza solução
        
        r_next = r - alpha * w  # Atualiza resíduo
        
        norma_r_novo = np.linalg.norm(r_next, 2)
        epsilon = norma_r_novo - norma_r_atual  # Mudança no resíduo
        
        # Critério de parada: estagnação
        if abs(epsilon) < tol:
            print(f"CGNR: Convergência (estagnação) na iteração: {i}")
            break
        
        z_next = H.T @ r_next  # Novo gradiente
        
        z_next_norm_sq = np.dot(z_next, z_next)
        beta = z_next_norm_sq / z_norm_sq
        
        p = z_next + beta * p  # Nova direção de busca
        
        r = r_next
        z = z_next
        norma_r_atual = norma_r_novo
    
    return f, iterations_done
