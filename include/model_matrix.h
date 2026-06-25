#ifndef MODEL_MATRIX_H
#define MODEL_MATRIX_H

#include <armadillo>
#include <string>

class ModelMatrix {
public:

    static std::string getMatrixName(
        const std::string& signal_id
    );

    static arma::mat load(
        const std::string& signal_id
    );
};

#endif