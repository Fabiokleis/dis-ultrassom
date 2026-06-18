#include <doctest/doctest.h>
#include "signal_gain.h"

TEST_CASE("apply_signal_gain deve aplicar ganho corretamente") {
    arma::vec g = {1.0, 2.0, 3.0, 4.0, 5.0};
    arma::vec g_with_gain = apply_signal_gain(g);
    
    CHECK(g_with_gain.n_elem == g.n_elem);
    
    // Verificar que ganho foi aplicado (valores maiores)
    for (size_t i = 0; i < g.n_elem; i++) {
        CHECK(g_with_gain(i) > g(i));
    }
}

TEST_CASE("compute_gain_vector deve calcular ganhos corretamente") {
    int S = 5;
    arma::vec gamma = compute_gain_vector(S);
    
    CHECK(gamma.n_elem == S);
    
    // γ_1 = 100 + (1/20) * 1 * sqrt(1) = 100.05
    CHECK(std::abs(gamma(0) - 100.05) < 1e-10);
    
    // γ_2 = 100 + (1/20) * 2 * sqrt(2) ≈ 100.14142
    double expected_2 = 100.0 + (1.0/20.0) * 2.0 * std::sqrt(2.0);
    CHECK(std::abs(gamma(1) - expected_2) < 1e-5);
    
    // Todos valores >= 100
    for (size_t i = 0; i < gamma.n_elem; i++) {
        CHECK(gamma(i) >= 100.0);
    }
}

TEST_CASE("apply_signal_gain deve preservar zeros") {
    arma::vec g = {0.0, 1.0, 0.0, 2.0, 0.0};
    arma::vec g_with_gain = apply_signal_gain(g);
    
    // Zeros devem permanecer zeros
    CHECK(g_with_gain(0) == 0.0);
    CHECK(g_with_gain(2) == 0.0);
    CHECK(g_with_gain(4) == 0.0);
    
    // Não-zeros devem ter ganho aplicado
    CHECK(g_with_gain(1) > g(1));
    CHECK(g_with_gain(3) > g(3));
}
