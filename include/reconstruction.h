#ifndef RECONSTRUCTION_H
#define RECONSTRUCTION_H


#include <armadillo>
#include "result.h"


class Reconstruction {


public:


static AlgResult execute(
    arma::mat H,
    arma::vec g,
    const std::string& algorithm
);


};


#endif