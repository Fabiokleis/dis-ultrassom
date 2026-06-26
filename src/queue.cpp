#include "queue.h"

JobQueue::JobQueue() : stop_(false) {}

void JobQueue::push(const JobInput& job) {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(job);
    }
    cv_.notify_one();  // Notifica um worker esperando
}

std::optional<JobInput> JobQueue::pop() {
    std::unique_lock<std::mutex> lock(mutex_);
    
    // Espera até ter job ou shutdown
    cv_.wait(lock, [this] { return !queue_.empty() || stop_; });
    
    if (stop_ && queue_.empty()) {
        return std::nullopt;  // Shutdown
    }
    
    JobInput job = queue_.front();
    queue_.pop();
    
    return job;
}

void JobQueue::shutdown() {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        stop_ = true;
    }
    cv_.notify_all();  // Acorda todos os workers
}

size_t JobQueue::size() {
    std::lock_guard<std::mutex> lock(mutex_);
    return queue_.size();
}
