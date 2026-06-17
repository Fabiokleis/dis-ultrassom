#ifndef CGNE_H
#define CGNE_H
#include "result.h"
#include <armadillo>

AlgResult cgne(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter);

#endif // CGNE_H
