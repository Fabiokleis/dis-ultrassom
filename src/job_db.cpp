#include "job_db.h"

JobDB::JobDB() : counter_(0) {}

int JobDB::create_job() {
    int job_id = counter_.fetch_add(1) + 1;  // Começa em 1
    
    std::lock_guard<std::mutex> lock(mutex_);
    
    JobResult result;
    result.job_id = job_id;
    result.status = JobStatus::PENDING;
    result.message = "Job created";
    
    jobs_[job_id] = result;
    
    return job_id;
}

std::optional<JobResult> JobDB::get_job(int job_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = jobs_.find(job_id);
    if (it != jobs_.end()) {
        return it->second;
    }
    
    return std::nullopt;
}

void JobDB::update_status(int job_id, JobStatus status) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = jobs_.find(job_id);
    if (it != jobs_.end()) {
        it->second.status = status;
        
        // Atualiza mensagem baseado no status
        switch (status) {
            case JobStatus::PENDING:
                it->second.message = "Pending";
                break;
            case JobStatus::PROCESSING:
                it->second.message = "Processing";
                break;
            case JobStatus::COMPLETED:
                it->second.message = "Completed successfully";
                break;
            case JobStatus::FAILED:
                it->second.message = "Failed";
                break;
        }
    }
}

void JobDB::update_job(int job_id, JobStatus status, const ReconstructionMetadata& metadata, const std::string& error) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = jobs_.find(job_id);
    if (it != jobs_.end()) {
        it->second.status = status;
        it->second.metadata = metadata;
        
        if (status == JobStatus::COMPLETED) {
            it->second.message = "Completed successfully";
        } else if (status == JobStatus::FAILED) {
            it->second.message = error.empty() ? "Failed" : error;
        }
    }
}

std::vector<JobResult> JobDB::list_jobs() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    std::vector<JobResult> result;
    result.reserve(jobs_.size());
    
    for (const auto& pair : jobs_) {
        result.push_back(pair.second);
    }
    
    return result;
}
