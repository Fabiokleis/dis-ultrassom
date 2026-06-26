#include "report_writer.h"
#include <iostream>
#include <sstream>
#include <filesystem>

namespace fs = std::filesystem;

ReportWriter::ReportWriter(const std::string& filepath)
    : filepath_(filepath), initialized_(false) {
    initialize_file();
}

ReportWriter::~ReportWriter() {
    if (file_.is_open()) {
        file_.close();
    }
}

void ReportWriter::initialize_file() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    bool file_exists = fs::exists(filepath_);
    
    if (!file_exists) {
        // Cria arquivo com header
        file_.open(filepath_, std::ios::out);
        if (!file_.is_open()) {
            throw std::runtime_error("Não foi possível criar arquivo: " + filepath_);
        }
        
        // Escreve header (formato idêntico ao Python)
        file_ << "job_id,signal_id,scale,model_matrix,algorithm,gain,iterations,"
              << "duration_ms,start_time,end_time,cpu_percent,ram_mb,num_workers,"
              << "status,error,image_path\n";
        
        file_.close();
    }
    
    initialized_ = true;
}

std::string ReportWriter::escape_csv(const std::string& value) {
    // Se contém vírgula, aspas ou quebra de linha, precisa escapar
    if (value.find(',') != std::string::npos ||
        value.find('"') != std::string::npos ||
        value.find('\n') != std::string::npos) {
        
        std::string escaped = "\"";
        for (char c : value) {
            if (c == '"') {
                escaped += "\"\"";  // Duplica aspas
            } else {
                escaped += c;
            }
        }
        escaped += "\"";
        return escaped;
    }
    return value;
}

void ReportWriter::write_row(
    int job_id,
    int signal_id,
    int scale,
    const std::string& model_matrix,
    int algorithm,
    bool gain,
    int iterations,
    float duration_ms,
    const std::string& start_time,
    const std::string& end_time,
    float cpu_percent,
    float ram_mb,
    int num_workers,
    const std::string& status,
    const std::string& error,
    const std::string& image_path
) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // Abre em modo append
    file_.open(filepath_, std::ios::app);
    if (!file_.is_open()) {
        std::cerr << "Erro ao abrir arquivo para escrita: " << filepath_ << std::endl;
        return;
    }
    
    // Escreve linha CSV
    file_ << job_id << ","
          << signal_id << ","
          << scale << ","
          << escape_csv(model_matrix) << ","
          << algorithm << ","
          << (gain ? "True" : "False") << ","
          << iterations << ","
          << duration_ms << ","
          << escape_csv(start_time) << ","
          << escape_csv(end_time) << ","
          << cpu_percent << ","
          << ram_mb << ","
          << num_workers << ","
          << escape_csv(status) << ","
          << escape_csv(error) << ","
          << escape_csv(image_path) << "\n";
    
    file_.flush();
    file_.close();
}
