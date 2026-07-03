#include "worker_pool.h"
#include "cgne.h"
#include "cgnr.h"
#include "signal_gain.h"
#include "generate_image.h"
#include "metrics.h"
#include "result.h"
#include <chrono>
#include <iomanip>
#include <sstream>
#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;

WorkerPool::WorkerPool(
    int num_workers,
    const std::string& h30_path,
    const std::string& h60_path,
    JobQueue* queue,
    JobDB* job_db,
    ReportWriter* report_writer
) : num_workers_(num_workers), queue_(queue), job_db_(job_db), report_writer_(report_writer) {
    
    bool h30_loaded = H_30_.load(h30_path, arma::csv_ascii);
    bool h60_loaded = H_60_.load(h60_path, arma::csv_ascii);
    
    if (!h30_loaded) {
        throw std::runtime_error("failed to load " + h30_path);
    }
    if (!h60_loaded) {
        throw std::runtime_error("failed to load " + h60_path);
    }
    
    std::cout << "worker pool: loaded H_30 (" << H_30_.n_rows << "x" << H_30_.n_cols << ")" << std::endl;
    std::cout << "worker pool: loaded H_60 (" << H_60_.n_rows << "x" << H_60_.n_cols << ")" << std::endl;
}

WorkerPool::~WorkerPool() {
    stop();
}

void WorkerPool::start() {
    std::cout << "worker pool: starting " << num_workers_ << " workers" << std::endl;
    
    for (int i = 0; i < num_workers_; ++i) {
        workers_.emplace_back(&WorkerPool::worker_loop, this);
    }
}

void WorkerPool::stop() {
    std::cout << "worker pool: stopping workers" << std::endl;
    
    for (auto& worker : workers_) {
        if (worker.joinable()) {
            worker.join();
        }
    }
    
    workers_.clear();
}

void WorkerPool::worker_loop() {
    while (true) {
        std::optional<JobInput> job_opt = queue_->pop();
        
        if (!job_opt.has_value()) {
            break;
        }
        
        JobInput job = job_opt.value();
        job_db_->update_status(job.job_id, JobStatus::PROCESSING);
        process_job(job);
    }
}

void WorkerPool::process_job(const JobInput& job) {
    auto start_time = std::chrono::steady_clock::now();
    std::string start_timestamp = get_timestamp();
    
    ReconstructionMetadata metadata;
    metadata.job_id = job.job_id;
    metadata.signal_id = job.signal_id;
    metadata.scale = job.scale;
    metadata.model_matrix = (job.scale == 30) ? "H-1" : "H-2";
    metadata.algorithm = job.algorithm;
    metadata.gain = job.gain;
    metadata.iterations = job.iterations;
    metadata.start_time = start_timestamp;
    metadata.num_workers = num_workers_;
    
    try {
        const arma::mat& H = select_matrix(job.scale);
        arma::vec g(job.signal_data);

        if (job.gain) {
            int N = 64; // O transdutor de ultrassom tem sempre 64 canais
            int S_amostras = 0;
            
            // Define o número de amostras (S) por canal dependendo do tamanho total do sinal
            if (g.n_elem == 50816) {
                S_amostras = 794;
            } else if (g.n_elem == 27904) {
                S_amostras = 436;
            } else {
                // Caso seja um sinal genérico de testes
                N = 1;
                S_amostras = g.n_elem;
            }
            // 2. Passa os tamanhos para a função de ganho
            g = apply_signal_gain(g, S_amostras, N);
        }


        AlgResult result;
        if (job.algorithm == static_cast<int>(Algorithm::CGNE)) {
            // CORRIGIDO: Passando job.iterations dinamicamente
            result = cgne(H, g, 1e-4, job.iterations);
        } else {
            // CORRIGIDO: Passando job.iterations dinamicamente
            result = cgnr(H, g, 1e-4, job.iterations);
        }
        
        
        arma::vec f = result.f;
        
        int side = static_cast<int>(std::sqrt(f.n_elem));

        

        // 3. Achata de novo para o formato que o save_png espera (.flatten())
        
    
        
        // Gera timestamp para o nome do arquivo (formato: YYYYMMDD_HHMMSS_microseconds)
        auto now = std::chrono::system_clock::now();
        auto tt = std::chrono::system_clock::to_time_t(now);
        auto us = std::chrono::duration_cast<std::chrono::microseconds>(
            now.time_since_epoch()
        ) % 1000000;
        
        std::ostringstream ts_oss;
        ts_oss << std::put_time(std::localtime(&tt), "%Y%m%d_%H%M%S_");
        ts_oss << std::setfill('0') << std::setw(6) << us.count();
        std::string filename_timestamp = ts_oss.str();
        
        // Formato: {signal_id}_{algorithm}_{timestamp}.png
        std::string image_filename = std::to_string(job.signal_id) + "_" 
                                   + std::to_string(job.algorithm) + "_"
                                   + filename_timestamp + ".png";
        std::string image_path = "imagens/" + image_filename;
        
        fs::create_directories("imagens");
        save_png(f, side, side, image_path.c_str());
        
        auto end_time = std::chrono::steady_clock::now();
        float duration_ms = std::chrono::duration<float, std::milli>(end_time - start_time).count();
        
        SystemMetrics metrics = MetricsCollector::CollectMetrics(num_workers_);
        
        metadata.end_time = get_timestamp();
        metadata.duration_ms = duration_ms;
        metadata.cpu_percent = metrics.cpu_percent;
        metadata.ram_mb = metrics.ram_mb;
        metadata.status = "completed";
        metadata.error = "";
        metadata.image_path = image_path;
        
        job_db_->update_job(job.job_id, JobStatus::COMPLETED, metadata, "");
        
        report_writer_->write_row(
            metadata.job_id,
            metadata.signal_id,
            metadata.scale,
            metadata.model_matrix,
            metadata.algorithm,
            metadata.gain,
            metadata.iterations,
            metadata.duration_ms,
            metadata.start_time,
            metadata.end_time,
            metadata.cpu_percent,
            metadata.ram_mb,
            metadata.num_workers,
            metadata.status,
            metadata.error,
            metadata.image_path
        );
        
        std::cout << "worker pool: job " << job.job_id << " completed in " 
                  << duration_ms << "ms" << std::endl;
        
    } catch (const std::exception& e) {
        auto end_time = std::chrono::steady_clock::now();
        float duration_ms = std::chrono::duration<float, std::milli>(end_time - start_time).count();
        
        std::string error_msg = e.what();
        
        metadata.end_time = get_timestamp();
        metadata.duration_ms = duration_ms;
        metadata.status = "failed";
        metadata.error = error_msg;
        metadata.image_path = "";
        
        SystemMetrics metrics = MetricsCollector::CollectMetrics(num_workers_);
        metadata.cpu_percent = metrics.cpu_percent;
        metadata.ram_mb = metrics.ram_mb;
        
        job_db_->update_job(job.job_id, JobStatus::FAILED, metadata, error_msg);
        
        report_writer_->write_row(
            metadata.job_id,
            metadata.signal_id,
            metadata.scale,
            metadata.model_matrix,
            metadata.algorithm,
            metadata.gain,
            metadata.iterations,
            metadata.duration_ms,
            metadata.start_time,
            metadata.end_time,
            metadata.cpu_percent,
            metadata.ram_mb,
            metadata.num_workers,
            metadata.status,
            metadata.error,
            metadata.image_path
        );
        
        std::cerr << "worker pool: job " << job.job_id << " failed: " << error_msg << std::endl;
    }
}

const arma::mat& WorkerPool::select_matrix(int scale) {
    if (scale == 30) {
        return H_30_;
    } else {
        return H_60_;
    }
}

std::string WorkerPool::get_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto tt = std::chrono::system_clock::to_time_t(now);
    auto us = std::chrono::duration_cast<std::chrono::microseconds>(
        now.time_since_epoch()
    ) % 1000000;
    
    std::ostringstream oss;
    oss << std::put_time(std::localtime(&tt), "%Y-%m-%dT%H:%M:%S");
    oss << '.' << std::setfill('0') << std::setw(6) << us.count();
    
    return oss.str();
}
