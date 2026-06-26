#ifndef MODELS_H
#define MODELS_H

#include <string>
#include <json.hpp>

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
    int scale;
    std::string model_matrix;
    int algorithm;
    bool gain;
    int iterations;
    std::string start_time;
    std::string end_time;
    float duration_ms;
    float cpu_percent;
    float ram_mb;
    int num_workers;
    std::string status;
    std::string error;
    std::string image_path;

    ReconstructionMetadata()
        : job_id(0), signal_id(0), scale(0), algorithm(0), 
          gain(false), iterations(0), duration_ms(0.0f),
          cpu_percent(0.0f), ram_mb(0.0f), num_workers(0) {}
};

class JobResult {
    public:
        int job_id;
        JobStatus status;
        std::string message;
        ReconstructionMetadata metadata;
};

#endif