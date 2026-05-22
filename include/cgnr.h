#ifndef CGNR_H
#define CGNR_H
#include <armadillo>

struct CsvParser {
  arma::mat H; // matrix modelo
  arma::vec g; // vetor sinal
};

arma::vec cgnr(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter);

#endif // CGNR_H
