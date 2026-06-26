#ifndef METRICS_H
#define METRICS_H

#include <string>
#include <json.hpp>
#include <mutex>
#include <fstream>

class SystemMetrics {
public:
    float cpu_percent;
    float ram_mb;
    int num_workers;
};

class MetricsCollector {
public:
    static SystemMetrics CollectMetrics();
};

#endif