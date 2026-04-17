#include "cgnr.h"
#include <iostream>
#include <cmath>

/*
  Algoritmo 1: CGNR (Conjugate Gradient Normal Residual) (Saad2003, p. 266)

f0 = 0
r0 = g − Hf0
z0 = HT * r0
p0 = z0

for i=0,1,...,until convergence

  wi = H * pi

  αi = ||zi||22 / ||wi||22
  
  fi+1 = fi + αi * pi
  
  ri+1 = ri − αi * wi
  
  zi+1 = HT * ri+1
  
  βi = ||zi+1||22 / ||zi||22
  
  pi+1 = zi+1 + βi * pi

*/
arma::vec cgnr(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter) {
    size_t n = H.n_cols;
    arma::vec f = arma::zeros<arma::vec>(n);
    arma::vec r = g - H * f;
    arma::vec z = H.t() * r;
    arma::vec p = z;

    double norma_r_atual = arma::norm(r, 2);

    for (size_t i = 0; i < max_iter; ++i) {
	arma::vec w = H * p;
       
        double z_norm_sq = arma::dot(z, z);
        double w_norm_sq = arma::dot(w, w);
        
        double alpha = z_norm_sq / w_norm_sq;
        
        f = f + alpha * p;
        
        arma::vec r_next = r - alpha * w;
        
        double norma_r_novo = arma::norm(r_next, 2);
        double epsilon = norma_r_novo - norma_r_atual;
        
        if (std::abs(epsilon) < tol) {
            std::cout << ">>> CGNR: Convergencia (estagnacao) na iteracao: " << i << std::endl;
            break;
        }
        
        arma::vec z_next = H.t() * r_next;
        
        double z_next_norm_sq = arma::dot(z_next, z_next);
        double beta = z_next_norm_sq / z_norm_sq;
        
        p = z_next + beta * p;

        r = r_next;
        z = z_next;
        norma_r_atual = norma_r_novo;
    }
    

    return f;
}
