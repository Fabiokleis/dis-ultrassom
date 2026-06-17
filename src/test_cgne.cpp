#include <doctest/doctest.h>
#include "cgne.h"

TEST_CASE("CGNE deve convergir e reconstruir a imagem corretamente") {

    int N = 10; 
    int S = 20; 
    arma::mat H = arma::randu<arma::mat>(S, N);
    arma::vec f_real = arma::randu<arma::vec>(N) * 10.0; 
    arma::vec g_simulado = H * f_real;

    AlgResult r = cgne(H, g_simulado, 1e-4, 11);
    arma::vec f_calculado = r.f;
    double erro_reconstrucao = arma::norm(f_real - f_calculado, 2);
    
    CHECK(erro_reconstrucao < 1e-4);
}
