#ifndef GENERATE_IMAGE_H
#define GENERATE_IMAGE_H

#include <armadillo>

void save_png(const arma::vec& f, int width, int height, const char* path);

#endif
