#include "cgne.h"
#include <iostream>
#include <cmath>

/*
 Algoritmo 1: CGNE (Conjugate Gradient Method Normal Error)
 
f0 = 0
r0 = g − H * f0
p0 = HT * r0

for i = 0, 1,..., until convergence

  αi = rTi * ri / pTi * pi
  
  fi+1 = fi + αipi
  
  ri+1 = ri − αi * Hpi
  
  βi = rTi+1 * ri+1 / rT * iri
  
  pi+1 = HT * ri+1 + βi * pi

*/
AlgResult cgne(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter) { 
    size_t n = H.n_cols;
    arma::vec f = arma::zeros<arma::vec>(n);
    arma::vec r = g - H * f;
    arma::vec p = H.t() * r;
    
    double r_norm_sq = arma::dot(r, r);
    double norma_r_atual = arma::norm(r, 2);
    size_t iterations_done = 0;
   
    for (size_t i = 0; i < max_iter; ++i) {
        iterations_done = i + 1;
        
        double p_norm_sq = arma::dot(p, p);
        double alpha = r_norm_sq / p_norm_sq;
       
        f = f + alpha * p;
        
        arma::vec r_next = r - alpha * (H * p);

	double norma_r_novo = arma::norm(r_next, 2);

	double epsilon = norma_r_novo - norma_r_atual;
	if (std::abs(epsilon) < tol) {
	    std::cout << "Parada por estagnacao na iteracao: " << i << std::endl;
	    break;
	}
        
        double r_next_norm_sq = arma::dot(r_next, r_next);
        double beta = r_next_norm_sq / r_norm_sq;

        p = H.t() * r_next + beta * p;
        
        r = r_next;
        r_norm_sq = r_next_norm_sq;
	norma_r_atual = norma_r_novo;
    }
    
    return {f, iterations_done};
}

