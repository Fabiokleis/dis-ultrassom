#include "cgne.h"
#include <iostream>
#include <cmath>

/*
 Algoritmo: CGNE (Conjugate Gradient Method Normal Error)
 Versão Estabilizada para Ganho de Sinal (Escala Unitária)
*/
AlgResult cgne(const arma::mat& H, const arma::vec& g, double tol, size_t max_iter) { 
    size_t n = H.n_cols;
    
    // 1. ESTABILIZAÇÃO NUMÉRICA: Calcula a norma original para isolar o efeito do ganho
    double norm_g_original = arma::norm(g, 2);
    if (norm_g_original < 1e-15) {
        return {arma::zeros<arma::vec>(n), 0};
    }
    
    // Cria uma cópia com escala protegida (norma idêntica a 1.0)
    arma::vec g_norm = g / norm_g_original;
    
    // Inicialização do CGNE usando o vetor estabilizado
    arma::vec f = arma::zeros<arma::vec>(n);
    arma::vec r = g_norm - H * f;
    arma::vec p = H.t() * r;
    
    double r_norm_sq = arma::dot(r, r);
    size_t iterations_done = 0;
   
    for (size_t i = 0; i < max_iter; ++i) {
        iterations_done = i + 1;
        
        // Pré-calcula Hp (Denominador correto: ||Hp||^2)
        arma::vec hp = H * p;
        double hp_norm_sq = arma::dot(hp, hp);
        
        if (hp_norm_sq < 1e-15) {
            std::cout << "CGNE: Parada por denominador nulo na iteracao: " << i << std::endl;
            break;
        }
        
        // Passo alpha
        double alpha = r_norm_sq / hp_norm_sq;
       
        // Atualização da solução e do resíduo
        f = f + alpha * p;
        arma::vec r_next = r - alpha * hp;

        double norma_r_novo = arma::norm(r_next, 2);

        // Como g_norm está escalonado em 1.0, a tolerância absoluta volta a ser segura
        if (norma_r_novo < tol) {
            std::cout << "CGNE: Convergência atingida na iteração: " << i << std::endl;
            break;
        }
        
        double r_next_norm_sq = arma::dot(r_next, r_next);
        
        // Salvaguarda caso as frequências do ganho tentem explodir numericamente
        if (r_next_norm_sq > 1e4) {
            std::cout << "CGNE: Parada preventiva por divergência na iteração: " << i << std::endl;
            break;
        }

        // Coeficiente beta e atualização do vetor de direção p
        double beta = r_next_norm_sq / r_norm_sq;
        p = H.t() * r_next + beta * p;
        
        r = r_next;
        r_norm_sq = r_next_norm_sq;
    }
    
    // 2. REESCALONAMENTO: Devolve à imagem a amplitude física real do sinal original
    f = f * norm_g_original;
    
    return {f, iterations_done};
}