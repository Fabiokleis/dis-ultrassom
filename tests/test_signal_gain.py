"""Testes unitários para cálculo de ganho de sinal"""
import pytest
import numpy as np
from server.signal_gain import apply_signal_gain, compute_gain_vector


def test_compute_gain_vector():
    """Testa cálculo do vetor de ganhos γ"""
    S = 5
    gamma = compute_gain_vector(S)
    
    assert gamma.shape == (S,)
    
    # Verificar valores manualmente
    # γ_1 = 100 + (1/20) * 1 * sqrt(1) = 100 + 0.05 * 1 = 100.05
    assert np.isclose(gamma[0], 100.05)
    
    # γ_2 = 100 + (1/20) * 2 * sqrt(2) = 100 + 0.1 * sqrt(2) ≈ 100.14142
    expected_2 = 100 + (1.0/20.0) * 2 * np.sqrt(2)
    assert np.isclose(gamma[1], expected_2, rtol=1e-5)
    
    # Todos os valores devem ser >= 100
    assert np.all(gamma >= 100)


def test_apply_signal_gain_increases_values():
    """Testa que ganho aumenta os valores do sinal"""
    g = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    g_with_gain = apply_signal_gain(g)
    
    assert g_with_gain.shape == g.shape
    
    # Verificar que o ganho foi aplicado (valores devem ser maiores)
    assert np.all(g_with_gain > g)


def test_apply_signal_gain_correct_calculation():
    """Testa cálculo correto do ganho"""
    g = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    g_with_gain = apply_signal_gain(g)
    
    # Calcular esperado manualmente
    gamma = compute_gain_vector(len(g))
    expected = g * gamma
    
    np.testing.assert_allclose(g_with_gain, expected, rtol=1e-10)


def test_apply_signal_gain_preserves_zeros():
    """Testa que zeros permanecem zeros após aplicar ganho"""
    g = np.array([0.0, 1.0, 0.0, 2.0, 0.0])
    g_with_gain = apply_signal_gain(g)
    
    # Zeros devem permanecer zeros (0 * γ = 0)
    assert g_with_gain[0] == 0.0
    assert g_with_gain[2] == 0.0
    assert g_with_gain[4] == 0.0
    
    # Não-zeros devem ter ganho aplicado
    assert g_with_gain[1] > g[1]
    assert g_with_gain[3] > g[3]


def test_apply_signal_gain_invalid_dimension():
    """Testa erro com dimensão inválida"""
    g = np.random.rand(2, 3)  # 2D
    
    with pytest.raises(ValueError, match="deve ser um vetor 1D"):
        apply_signal_gain(g)
