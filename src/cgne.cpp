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
arma::vec cgne(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter) { 
    size_t n = H.n_cols;
    arma::vec f = arma::zeros<arma::vec>(n); // vetor unitario 0
    arma::vec r = g - H * f; // residuo (g sinal - martriz modelo * imagem f )
    arma::vec p = H.t() * r; // p direcao
    
    double r_norm_sq = arma::dot(r, r); // produto interno
    double norma_r_atual = arma::norm(r, 2);
   
    for (size_t i = 0; i < max_iter; ++i) {
        
        double p_norm_sq = arma::dot(p, p); // produto interno
        double alpha = r_norm_sq / p_norm_sq; // divisao do produto interno dos dois vetores unitarios
       
        f = f + alpha * p; // atualiza imagem reconstruida f 
        
        arma::vec r_next = r - alpha * (H * p); // recalcula residuo ao passo alpha

	double norma_r_novo = arma::norm(r_next, 2);

	double epsilon = norma_r_novo - norma_r_atual; // diferenca de residuo (grau de estagnacao)
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
    
    return f;
}

