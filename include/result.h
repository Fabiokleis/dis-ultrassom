#ifndef ALG_RESULT_H
#define ALG_RESULT_H
#include <armadillo>

struct AlgResult {
    arma::vec f;
    size_t iterations;
};

#endif // ALG_RESULT_H
