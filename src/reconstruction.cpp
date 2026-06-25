#include "reconstruction.h"

#include "cgne.h"
#include "cgnr.h"

#include <stdexcept>



AlgResult Reconstruction::execute(
    arma::mat H,
    arma::vec g,
    const std::string& algorithm
){


if(algorithm=="cgne"){

    return cgne(
        H,
        g,
        1e-4,
        10
    );

}



if(algorithm=="cgnr"){

    return cgnr(
        H,
        g,
        1e-4,
        10
    );

}



throw std::invalid_argument(
    "Algoritmo inválido"
);


}