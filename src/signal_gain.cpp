#include "signal_gain.h"
#include <cmath>

arma::vec apply_signal_gain(const arma::vec& g, int S, int N) {
    int total_elem = g.n_elem;
    arma::vec g_with_gain = g;

    // Se não foram passados parâmetros válidos, detecta automaticamente
    if (S <= 0 || N <= 0) {
        if (total_elem == 50816) {
            S = 794;
            N = 64;
        } else if (total_elem == 27904) {
            S = 436;
            N = 64;
        } else {
            N = 1;
            S = total_elem;
        }
    }

    // Aplica o ganho elemento a elemento por canal
    for (int canal = 0; canal < N; canal++) {
        for (int l = 1; l <= S; l++) {
            double gamma_l = 100.0 + (1.0 / 20.0) * l * std::sqrt(l);
            int indice_global = (canal * S) + (l - 1);
            
            if (indice_global < total_elem) {
                g_with_gain(indice_global) *= gamma_l;
            }
        }
    }
    
    return g_with_gain;
}

arma::vec compute_gain_vector(int S) {
    arma::vec gamma(S);
    for (int l = 1; l <= S; l++) {
        gamma(l - 1) = 100.0 + (1.0 / 20.0) * l * std::sqrt(l);
    }
    return gamma;
}