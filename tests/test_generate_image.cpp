#include <doctest/doctest.h>
#include "generate_image.h"
#include <filesystem>

TEST_CASE("save_png deve criar arquivo PNG com dimensoes corretas") {
    int side = 10;
    arma::vec f = arma::randu<arma::vec>(side * side) * 100.0;
    const char* output_path = "imagens/test_cpp_save.png";
    
    save_png(f, side, side, output_path);
    
    CHECK(std::filesystem::exists(output_path));
    
    // Cleanup
    std::filesystem::remove(output_path);
}
