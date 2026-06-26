#include "metrics.h"
#include <uprofile.h>
#include <numeric>

SystemMetrics MetricsCollector::CollectMetrics(int num_workers) {
    SystemMetrics metrics;
    metrics.num_workers = num_workers;
    
    std::vector<float> cpu_loads = uprofile::getInstantCpuUsage();
    if (!cpu_loads.empty()) {
        float total = std::accumulate(cpu_loads.begin(), cpu_loads.end(), 0.0f);
        metrics.cpu_percent = total;
    } else {
        metrics.cpu_percent = 0.0f;
    }
    
    int rss = 0, shared = 0;
    uprofile::getProcessMemory(rss, shared);
    metrics.ram_mb = rss / 1024.0f;
    
    return metrics;
}
