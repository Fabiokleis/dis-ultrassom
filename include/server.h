#ifndef SERVER_H
#define SERVER_H

#include "queue.h"
#include "job_db.h"
#include "worker_pool.h"
#include "report_writer.h"
#include <httplib.h>
#include <memory>
#include <string>

class Server {
private:
    int port_;
    int num_workers_;
    
    std::unique_ptr<JobQueue> queue_;
    std::unique_ptr<JobDB> job_db_;
    std::unique_ptr<ReportWriter> report_writer_;
    std::unique_ptr<WorkerPool> worker_pool_;
    
    httplib::Server http_server_;
    
    void setup_routes();
    
    void handle_submit_job(const httplib::Request& req, httplib::Response& res);
    void handle_get_job(const httplib::Request& req, httplib::Response& res);
    void handle_health(const httplib::Request& req, httplib::Response& res);

public:
    Server(
        int port = 8000,
        int num_workers = 4,
        const std::string& h30_path = "H-1.csv",
        const std::string& h60_path = "H-2.csv",
        const std::string& report_path = "reconstruction_report_cpp.csv"
    );
    
    ~Server();
    
    void start();
    void stop();
};

#endif // SERVER_H