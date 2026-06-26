#ifndef MODELS_H
#define MODELS_H

#include <string>
#include <json.hpp>
#include <mutex>
#include <fstream>

enum class Algorithm {
    CGNE = 1,
    CGNR = 2
};

enum class ScaleModel {
    S1 = 30,
    S2 = 60
};

enum class SignalModel {
    G1 = 1,
    G2 = 2,
    G3 = 3
};

enum class JobStatus {
    PENDING = 0,
    PROCESSING = 1,
    COMPLETED = 2,
    FAILED = 3
};

class ReconstructionMetadata {
public:
    int job_id;
    int signal_id;
    int scale_id;
    int model_matrix;
    int algorithm;
    bool gain;
    int iterations;
    std::string starttime;
    std::string endtime;
    float duration_ms;
    float cpu_percent;
    float ram_mb;
    int num_workers;
    std::string status;
    std::string error;
    int image_width;
    int image_height;
    std::string image_path;
    std::ofstream report;
    std::mutex report_mutex;

    ReconstructionMetadata()
    {
        report.open("reconstruction_report_cpp.csv", std::ios::app);
        report << "job_id,signal_id,scale,model_matrix,algorithm,gain,iterations,duration_ms,start_time,end_time,cpu_percent,ram_mb,num_workers,status,error,image_path\n";
    }
    ~ReconstructionMetadata()
    {
        if(report.is_open())
        {
            report.close();
        }
    }

    void WriteRow()
    {
        std::lock_guard<std::mutex> lock(report_mutex);
        report << job_id << "," 
               << signal_id << ","
               << scale_id << ","
               << model_matrix << ","
               << algorithm << ","
               << gain << ","
               << iterations << ","
               << starttime << ","
               << endtime << ","
               << duration_ms << ","
               << cpu_percent << ","
               << ram_mb << ","
               << num_workers << ","
               << status << ","
               << error << ","
               << image_width << ","
               << image_height << ","
               << image_path << "\n";
        std::lock_guard<std::mutex> unlock(report_mutex);
    }

};

class JobResult {
    public:
        int job_id;
        JobStatus status;
        std::string message;
        ReconstructionMetadata metadata;
};

#endif