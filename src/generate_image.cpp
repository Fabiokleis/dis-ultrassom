#include "generate_image.h"
#include "lodepng.h"
#include <iostream>
#include <vector>

void save_png(const arma::vec& f, int width, int height, const char* path) {
  double mn = f.min();
  double mx = f.max();
  arma::vec norm = (mx != mn) ? arma::vec((f - mn) / (mx - mn) * 255.0) : arma::zeros<arma::vec>(f.n_elem);
  
  std::vector<unsigned char> pixels(f.n_elem);
  for (size_t i = 0; i < f.n_elem; i++)
    pixels[i] = (unsigned char)norm(i);

  unsigned error = lodepng::encode(path, pixels, width, height, LCT_GREY, 8);
  if (error)
    std::cerr << "PNG error: " << lodepng_error_text(error) << std::endl;
}
