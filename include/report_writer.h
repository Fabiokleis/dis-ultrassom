#ifndef REPORT_WRITER_H
#define REPORT_WRITER_H

#include <fstream>
#include <mutex>
#include <string>

class ReportWriter {
private:
    std::string filepath_;
    std::ofstream file_;
    std::mutex mutex_;
    bool initialized_;

    void initialize_file();
    std::string escape_csv(const std::string& value);

public:
    explicit ReportWriter(const std::string& filepath = "reconstruction_report_cpp.csv");
    ~ReportWriter();

    // Desabilita cópia (file stream não é copiável)
    ReportWriter(const ReportWriter&) = delete;
    ReportWriter& operator=(const ReportWriter&) = delete;

    void write_row(
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
    );
};

#endif // REPORT_WRITER_H
