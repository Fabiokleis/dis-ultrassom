#include <iostream>
#include <armadillo>
#include "cgne.h"

int main() {
    int N = 10; // tamamho da imagem
    int S = 20; // numero de amostras do sinal g

    arma::mat H = arma::randu<arma::mat>(S, N);

    arma::vec f_real = arma::randu<arma::vec>(N) * 10.0; 

    arma::vec g_simulado = H * f_real;

    std::cout << "CGNE..." << std::endl;
    arma::vec f_calculado = cgne(H, g_simulado, 1e-4, 10);

    std::cout << "  f_real  |  f_calculado" << std::endl;
    std::cout << "--------------------------" << std::endl;
    
    for (int i = 0; i < N; ++i) {
        printf("%d %9.4f | %9.4f\n", i, f_real(i), f_calculado(i));
    }

    double erro_reconstrucao = arma::norm(f_real - f_calculado, 2);
    
    std::cout << "--------------------------" << std::endl;
    std::cout << "Erro total da reconstrucao: " << erro_reconstrucao << std::endl;

    if (erro_reconstrucao < 1e-4) {
        std::cout << "Taxa de erro < 1e-4"  << std::endl;
    } else {
        std::cout << "Taxa de erro > 1e-4" << std::endl;
    }

    return 0;
}
