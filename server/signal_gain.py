"""Cálculo do ganho de sinal para reconstrução de imagens"""
import numpy as np


def apply_signal_gain(g: np.ndarray) -> np.ndarray:
    """
    Aplica ganho de sinal γ ao vetor g.
    
    Fórmula:
        γ_l = 100 + (1/20) * l * sqrt(l)
        g_l = g_l * γ_l
    
    onde l é o índice do sinal (1-based: 1 .. S)
    
    Args:
        g: Vetor de sinais (shape: (S,))
    
    Returns:
        Vetor com ganho aplicado
    """
    if g.ndim != 1:
        raise ValueError(f"g deve ser um vetor 1D, recebido: {g.ndim}D")
    
    S = g.shape[0]
    g_with_gain = g.copy()
    
    for l in range(1, S + 1):  # l = 1 .. S (1-based)
        gamma_l = 100 + (1.0/20.0) * l * np.sqrt(l)
        g_with_gain[l - 1] *= gamma_l  # Converter para índice 0-based
    
    return g_with_gain


def compute_gain_vector(S: int) -> np.ndarray:
    """
    Calcula apenas o vetor de ganhos γ para debug/análise.
    
    Args:
        S: Número de sinais (tamanho do vetor)
    
    Returns:
        Vetor de ganhos γ (shape: (S,))
    """
    gamma = np.zeros(S)
    
    for l in range(1, S + 1):  # l = 1 .. S (1-based)
        gamma[l - 1] = 100 + (1.0/20.0) * l * np.sqrt(l)
    
    return gamma
