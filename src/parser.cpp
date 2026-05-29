#include "parser.h"
#include <cassert>

void read_signal(const char *file_path, CsvParser *p) { 
  assert(file_path != nullptr);
  assert(p != nullptr);
  p->g.load(file_path, arma::csv_ascii);
}

void read_model(const char *file_path, CsvParser *p) {
  assert(file_path != nullptr);
  assert(p != nullptr);
  p->H.load(file_path, arma::csv_ascii);
}
