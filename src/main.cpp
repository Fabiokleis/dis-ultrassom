#include <iostream>
#include <cmath>
#include <armadillo>
#include "result.h"
#include "cgne.h"
#include "parser.h"
#include "generate_image.h"

#define CSV_SIGNAL_FILE "G-1.csv"
#define CSV_MODEL_FILE "H-1.csv"

int main() {
  CsvParser p;
  read_signal(CSV_SIGNAL_FILE, &p);
  read_model(CSV_MODEL_FILE, &p);

  std::cout << p.g.n_rows << std::endl;
  std::cout << p.H.n_rows << "x" << p.H.n_cols << std::endl;

  AlgResult r = cgne(p.H, p.g, 1e-4, 10);
  arma::vec f_calculado = r.f;
  arma::vec saida = arma::abs(f_calculado);
  
  saida.save("saida.csv", arma::csv_ascii);

  int side = (int)std::sqrt((double)saida.n_elem);
  save_png(saida, side, side, "saida.png");
  
  
  std::cout << "Imagem salva: saida.png (" << side << "x" << side << ")" << std::endl;

  return 0;
}

int main2() {
    int N = 30; // tamamho da imagem
    int S = 20; // numero de amostras do sinal g

    arma::mat H = arma::randu<arma::mat>(S, N);

    arma::vec f_real = arma::randu<arma::vec>(N) * 10.0; 

    arma::vec g_simulado = H * f_real;

    std::cout << "CGNE..." << std::endl;
    AlgResult r = cgne(H, g_simulado, 1e-4, 10);
    arma::vec f_calculado = r.f;

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
