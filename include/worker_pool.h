#ifndef WORKER_POOL_H
#define WORKER_POOL_H

#include "queue.h"
#include "job_db.h"
#include "report_writer.h"
#include <armadillo>
#include <thread>
#include <vector>
#include <string>

class WorkerPool {
private:
    int num_workers_;
    std::vector<std::thread> workers_;
    
    // H matrices (carregadas uma vez, compartilhadas entre workers)
    arma::mat H_30_;
    arma::mat H_60_;
    
    // Componentes compartilhados
    JobQueue* queue_;
    JobDB* job_db_;
    ReportWriter* report_writer_;
    
    // Worker loop (executado por cada thread)
    void worker_loop();
    
    // Processa um job individual
    void process_job(const JobInput& job);
    
    // Helper: seleciona matriz H baseado no scale
    const arma::mat& select_matrix(int scale);
    
    // Helper: gera timestamp ISO 8601
    std::string get_timestamp();
    
public:
    WorkerPool(
        int num_workers,
        const std::string& h30_path,
        const std::string& h60_path,
        JobQueue* queue,
        JobDB* job_db,
        ReportWriter* report_writer
    );
    
    ~WorkerPool();
    
    // Inicia threads
    void start();
    
    // Para threads (join)
    void stop();
};

#endif // WORKER_POOL_H
