#include "parser.h"
#include <iostream>
#include <string>
#include <cassert>

void read_signal(const char *file_path, CsvParser *p) { 
  assert(file_path != nullptr);
  assert(p != nullptr);
 
  std::string line; 
  std::ifstream signal(file_path);
  size_t i = 0;

  while (std::getline(signal, line)) {
    std::cout << "nova linha:" << std::endl;
    std::cout << line;
    double value = std::stod(line);
    std::cout << value << std::endl;

    p->g.insert_rows(2, 1);
  }

  signal.close();
}

void read_model(const char *file_path, CsvParser *p) {
  assert(file_path != nullptr);
  assert(p != nullptr);

  std::string v;
  std::ifstream model(file_path);
  
  while (std::getline(model, value, ',')) {
    double value = std::stod(value);
    
    std::cout << "Value: " << value << std::endl;
  }

  model.close()
}
