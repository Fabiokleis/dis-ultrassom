#ifndef SIGNAL_GAIN_H
#define SIGNAL_GAIN_H

#include <armadillo>

// Aplica ganho de sinal γ ao vetor g
// γ_l = 100 + (1/20) * l * sqrt(l)
// g_l = g_l * γ_l
// onde l = 1 .. S (1-based)
arma::vec apply_signal_gain(const arma::vec& g);

// Calcula apenas o vetor de ganhos γ para debug/análise
arma::vec compute_gain_vector(int S);

#endif
