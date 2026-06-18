#include "signal_gain.h"
#include <cmath>

arma::vec apply_signal_gain(const arma::vec& g) {
    int S = g.n_elem;
    arma::vec g_with_gain = g;
    
    for (int l = 1; l <= S; l++) {  // l = 1 .. S (1-based)
        double gamma_l = 100.0 + (1.0/20.0) * l * std::sqrt(l);
        g_with_gain(l - 1) *= gamma_l;  // Converter para índice 0-based
    }
    
    return g_with_gain;
}

arma::vec compute_gain_vector(int S) {
    arma::vec gamma(S);
    
    for (int l = 1; l <= S; l++) {  // l = 1 .. S (1-based)
        gamma(l - 1) = 100.0 + (1.0/20.0) * l * std::sqrt(l);
    }
    
    return gamma;
}
