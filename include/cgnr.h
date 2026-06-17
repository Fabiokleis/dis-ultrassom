#ifndef CGNR_H
#define CGNR_H
#include "result.h" 
#include <armadillo>

AlgResult cgnr(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter);

#endif // CGNR_H
