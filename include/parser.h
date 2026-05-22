#ifndef PARSER_H
#define PARSER_H

#include <armadillo>

struct CsvParser {
  arma::mat H; // matrix modelo
  arma::vec g; // vetor sinal
};

void read_signal(const char *file_path, CsvParser *p);
void read_model(const char *file_path, CsvParser *p);

#endif // PARSER_H
