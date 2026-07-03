#include "generate_image.h"
#include "lodepng.h"
#include <iostream>
#include <vector>

void save_png(const arma::vec& f, int width, int height, const char* path) {
  // 1. Extrai o absoluto para evitar intensidades negativas
  arma::vec f_abs = arma::abs(f);
  double mn = f_abs.min();
  double mx = f_abs.max();
  
  // Normalização básica de contraste [0, 255]
  arma::vec norm = (mx != mn) ? arma::vec((f_abs - mn) / (mx - mn) * 255.0) : arma::zeros<arma::vec>(f.n_elem);
  
  // 2. CORREÇÃO GEOMÉTRICA (Deixa equivalente ao .reshape(height, width) do Python)
  arma::mat mat_geometric = arma::reshape(norm, width, height);
  mat_geometric = mat_geometric.t(); // Transpõe para converter Column-Major para Row-Major do PNG
  arma::vec norm_row_major = arma::vectorise(mat_geometric);

  // 3. Prepara o buffer para o lodepng
  std::vector<unsigned char> pixels(f.n_elem);
  for (size_t i = 0; i < f.n_elem; i++) {
    pixels[i] = (unsigned char)norm_row_major(i);
  }

  unsigned error = lodepng::encode(path, pixels, width, height, LCT_GREY, 8);
  if (error) {
    std::cerr << "PNG error: " << lodepng_error_text(error) << std::endl;
  }
}