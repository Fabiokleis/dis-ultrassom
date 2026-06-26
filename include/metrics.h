#ifndef METRICS_H
#define METRICS_H

struct SystemMetrics {
    float cpu_percent;
    float ram_mb;
    int num_workers;
};

class MetricsCollector {
public:
    static SystemMetrics CollectMetrics(int num_workers);
};

#endif // METRICS_H