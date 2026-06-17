"""
Algoritmo CGNE (Conjugate Gradient Normal Error)
Implementado com NumPy (usa BLAS/LAPACK como Armadillo)
"""
import numpy as np
from typing import Tuple


def cgne(H: np.ndarray, g: np.ndarray, tol: float = 1e-4, max_iter: int = 10) -> Tuple[np.ndarray, int]:
    """
    Algoritmo CGNE (Conjugate Gradient Normal Error)
    
    Pseudocódigo:
    f0 = 0
    r0 = g − H * f0
    p0 = H^T * r0
    
    for i = 0, 1,..., until convergence
      αi = r^T_i * ri / p^T_i * pi
      fi+1 = fi + αi*pi
      ri+1 = ri − αi * H*pi
      βi = r^T_i+1 * ri+1 / r^T_i * ri
      pi+1 = H^T * ri+1 + βi * pi
    
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
    p = H.T @ r      # Direção de busca inicial
    
    r_norm_sq = np.dot(r, r)
    norma_r_atual = np.linalg.norm(r, 2)
    iterations_done = 0
    
    for i in range(max_iter):
        iterations_done = i + 1
        
        p_norm_sq = np.dot(p, p)
        alpha = r_norm_sq / p_norm_sq
        
        f = f + alpha * p  # Atualiza solução
        
        r_next = r - alpha * (H @ p)  # Atualiza resíduo
        
        norma_r_novo = np.linalg.norm(r_next, 2)
        epsilon = norma_r_novo - norma_r_atual  # Mudança no resíduo
        
        # Critério de parada: estagnação
        if abs(epsilon) < tol:
            print(f"CGNE: Parada por estagnação na iteração: {i}")
            break
        
        r_next_norm_sq = np.dot(r_next, r_next)
        beta = r_next_norm_sq / r_norm_sq
        
        p = H.T @ r_next + beta * p  # Nova direção de busca
        
        r = r_next
        r_norm_sq = r_next_norm_sq
        norma_r_atual = norma_r_novo
    
    return f, iterations_done
