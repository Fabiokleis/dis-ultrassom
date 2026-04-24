#include <doctest/doctest.h>
#include "cgnr.h"

TEST_CASE("Matriz vezes a Transposta") {
    int N = 2; 
    int S = 4;
    arma::mat H = arma::randu<arma::mat>(S, N);

    arma::mat R = H * H.t();


    std::cout << R << std::endl;    
}


TEST_CASE("Matriz Transposta vezes a matriz") {
    int N = 2; 
    int S = 4;
    arma::mat H = arma::randu<arma::mat>(S, N);

    arma::mat R = H.t() * H;


    std::cout << R << std::endl;    
}


TEST_CASE("Matriz vezes a matriz") {
    int N = 2; 
    int S = 4;
    arma::mat H = arma::randu<arma::mat>(S, N);

    arma::mat R = H * H;


    std::cout << R << std::endl;    
}
