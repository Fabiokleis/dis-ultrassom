#ifndef QUEUE_H
#define QUEUE_H

#include "models.h"
#include <queue>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <vector>

// Input para job (request data)
struct JobInput {
    int job_id;
    int signal_id;      // SignalModel::G1, G2, G3
    int scale;          // ScaleModel::S1 (30), S2 (60)
    int algorithm;      // Algorithm::CGNE (1), CGNR (2)
    bool gain;
    int iterations;
    std::vector<double> signal_data;  // Vetor G carregado
};

class JobQueue {
private:
    std::queue<JobInput> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    bool stop_;

public:
    JobQueue();
    
    // Adiciona job na fila (producer)
    void push(const JobInput& job);
    
    // Remove job da fila (consumer, blocking)
    // Retorna std::nullopt quando queue está em shutdown
    std::optional<JobInput> pop();
    
    // Shutdown da fila (para workers)
    void shutdown();
    
    // Retorna tamanho atual da fila
    size_t size();
};

#endif // QUEUE_H
