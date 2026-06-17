#include <doctest/doctest.h>
#include "cgnr.h"

TEST_CASE("CGNR deve minimizar o erro nas equacoes normais") {
    int N = 10; 
    int S = 20; 
    arma::mat H = arma::randu<arma::mat>(S, N);
    arma::vec f_real = arma::randu<arma::vec>(N) * 10.0; 
    arma::vec g_simulado = H * f_real;

    AlgResult r = cgnr(H, g_simulado, 1e-4, 11);
    arma::vec f_calculado = r.f;

    double erro_reconstrucao = arma::norm(f_real - f_calculado, 2);

    CHECK(erro_reconstrucao < 1e-4);
}
