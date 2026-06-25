#include "model_matrix.h"

#include <filesystem>
#include <stdexcept>

namespace fs = std::filesystem;


std::string ModelMatrix::getMatrixName(
    const std::string& signal_id
){

    if(signal_id=="G-1" ||
       signal_id=="G-2" ||
       signal_id=="G-3")
        return "H-1";


    if(signal_id=="G-4" ||
       signal_id=="G-5" ||
       signal_id=="G-6")
        return "H-2";


    throw std::invalid_argument(
        "Sinal inválido: " + signal_id
    );
}



arma::mat ModelMatrix::load(
    const std::string& signal_id
){

    auto name = getMatrixName(signal_id);


    fs::path file =
        name + ".csv";


    if(!fs::exists(file))
        throw std::runtime_error(
            "Matriz não encontrada"
        );


    arma::mat H;


    H.load(
        file.string(),
        arma::csv_ascii
    );


    return H;
}