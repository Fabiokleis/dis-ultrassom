#ifndef JOB_DB_H
#define JOB_DB_H

#include "models.h"
#include <map>
#include <mutex>
#include <atomic>
#include <optional>

class JobDB {
private:
    std::map<int, JobResult> jobs_;
    std::mutex mutex_;
    std::atomic<int> counter_;

public:
    JobDB();
    
    // Cria novo job e retorna job_id
    int create_job();
    
    // Obtém job por ID (retorna nullptr se não encontrado)
    std::optional<JobResult> get_job(int job_id);
    
    // Atualiza status do job
    void update_status(int job_id, JobStatus status);
    
    // Atualiza job com metadata completo
    void update_job(int job_id, JobStatus status, const ReconstructionMetadata& metadata, const std::string& error = "");
    
    // Lista todos os jobs
    std::vector<JobResult> list_jobs();
};

#endif // JOB_DB_H
