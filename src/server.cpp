#include "server.h"
#include "models.h"
#include <json.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <ctime>
#include <iomanip>

using json = nlohmann::json;

// Helper function to log HTTP requests (similar to uvicorn/FastAPI)
void log_http_request(const httplib::Request& req, const httplib::Response& res) {
    // Build query string from params
    std::string query_string;
    if (!req.params.empty()) {
        query_string = "?";
        bool first = true;
        for (const auto& param : req.params) {
            if (!first) query_string += "&";
            query_string += param.first + "=" + param.second;
            first = false;
        }
    }
    
    // Get status code text
    std::string status_text;
    switch (res.status) {
        case 200: status_text = "OK"; break;
        case 201: status_text = "Created"; break;
        case 400: status_text = "Bad Request"; break;
        case 404: status_text = "Not Found"; break;
        case 500: status_text = "Internal Server Error"; break;
        default: status_text = ""; break;
    }
    
    // Format: IP:port - "METHOD path HTTP/1.1" status status_text
    std::cout << "INFO:     " 
              << req.remote_addr << ":" << req.remote_port << " - "
              << "\"" << req.method << " " << req.path << query_string << " HTTP/1.1\" "
              << res.status << " " << status_text
              << std::endl;
}

Server::Server(
    int port,
    int num_workers,
    const std::string& h30_path,
    const std::string& h60_path,
    const std::string& report_path
) : port_(port), num_workers_(num_workers) {
    
    queue_ = std::make_unique<JobQueue>();
    job_db_ = std::make_unique<JobDB>();
    report_writer_ = std::make_unique<ReportWriter>(report_path);
    worker_pool_ = std::make_unique<WorkerPool>(
        num_workers,
        h30_path,
        h60_path,
        queue_.get(),
        job_db_.get(),
        report_writer_.get()
    );
    
    setup_routes();
}

Server::~Server() {
    stop();
}

void Server::setup_routes() {
    http_server_.Get("/", [this](const httplib::Request& req, httplib::Response& res) {
        handle_health(req, res);
    });
    
    http_server_.Post("/ultrassom", [this](const httplib::Request& req, httplib::Response& res) {
        handle_submit_job(req, res);
    });
    
    http_server_.Get(R"(/jobs/(\d+))", [this](const httplib::Request& req, httplib::Response& res) {
        handle_get_job(req, res);
    });
}

void Server::handle_health(const httplib::Request& req, httplib::Response& res) {
    json response = {
        {"status", "ok"},
        {"message", "c++ server running"},
        {"num_workers", num_workers_},
        {"queue_size", queue_->size()}
    };
    
    res.status = 200;
    res.set_content(response.dump(), "application/json");
    log_http_request(req, res);
}

void Server::handle_submit_job(const httplib::Request& req, httplib::Response& res) {
    try {
        int signal_id = std::stoi(req.get_param_value("signal_id"));
        int scale = std::stoi(req.get_param_value("scale"));
        int algorithm = std::stoi(req.get_param_value("algorithm"));
        bool gain = req.has_param("gain") && req.get_param_value("gain") == "true";
        
        if (!req.form.has_file("signal")) {
            json error = {{"detail", "missing signal file"}};
            res.status = 400;
            res.set_content(error.dump(), "application/json");
            log_http_request(req, res);
            return;
        }
        
        const auto& signal_file = req.form.get_file("signal");
        
        std::istringstream iss(signal_file.content);
        arma::vec g;
        bool loaded = g.load(iss, arma::csv_ascii);
        
        if (!loaded) {
            json error = {{"detail", "failed to parse signal CSV"}};
            res.status = 400;
            res.set_content(error.dump(), "application/json");
            log_http_request(req, res);
            return;
        }
        
        std::vector<double> signal_data = arma::conv_to<std::vector<double>>::from(g);
        
        int job_id = job_db_->create_job();
        
        JobInput job_input;
        job_input.job_id = job_id;
        job_input.signal_id = signal_id;
        job_input.scale = scale;
        job_input.algorithm = algorithm;
        job_input.gain = gain;
        job_input.iterations = 10;
        job_input.signal_data = signal_data;
        
        queue_->push(job_input);
        
        json response = {
            {"job_id", job_id},
            {"status", "PENDING"},
            {"message", "job submitted to queue"}
        };
        
        res.status = 200;
        res.set_content(response.dump(), "application/json");
        log_http_request(req, res);
        
    } catch (const std::exception& e) {
        json error = {{"detail", std::string("error: ") + e.what()}};
        res.status = 500;
        res.set_content(error.dump(), "application/json");
        log_http_request(req, res);
        std::cerr << "server: error submitting job: " << e.what() << std::endl;
    }
}

void Server::handle_get_job(const httplib::Request& req, httplib::Response& res) {
    try {
        int job_id = std::stoi(req.matches[1]);
        
        auto job_opt = job_db_->get_job(job_id);
        
        if (!job_opt.has_value()) {
            json error = {{"detail", "job not found"}};
            res.status = 404;
            res.set_content(error.dump(), "application/json");
            log_http_request(req, res);
            return;
        }
        
        JobResult job = job_opt.value();
        
        std::string status_str;
        switch (job.status) {
            case JobStatus::PENDING:
                status_str = "PENDING";
                break;
            case JobStatus::PROCESSING:
                status_str = "PROCESSING";
                break;
            case JobStatus::COMPLETED:
                status_str = "COMPLETED";
                break;
            case JobStatus::FAILED:
                status_str = "FAILED";
                break;
        }
        
        json response = {
            {"job_id", job.job_id},
            {"status", status_str},
            {"message", job.message}
        };
        
        if (job.status == JobStatus::COMPLETED) {
            response["metadata"] = {
                {"signal_id", job.metadata.signal_id},
                {"scale", job.metadata.scale},
                {"model_matrix", job.metadata.model_matrix},
                {"algorithm", job.metadata.algorithm},
                {"gain", job.metadata.gain},
                {"iterations", job.metadata.iterations},
                {"duration_ms", job.metadata.duration_ms},
                {"cpu_percent", job.metadata.cpu_percent},
                {"ram_mb", job.metadata.ram_mb},
                {"image_path", job.metadata.image_path}
            };
        }
        
        res.status = 200;
        res.set_content(response.dump(), "application/json");
        log_http_request(req, res);
        
    } catch (const std::exception& e) {
        json error = {{"detail", std::string("error: ") + e.what()}};
        res.status = 500;
        res.set_content(error.dump(), "application/json");
        log_http_request(req, res);
        std::cerr << "server: error getting job: " << e.what() << std::endl;
    }
}

void Server::start() {
    std::cout << "server: starting worker pool (" << num_workers_ << " workers)" << std::endl;
    worker_pool_->start();
    
    std::cout << "server: listening on port " << port_ << std::endl;
    http_server_.listen("0.0.0.0", port_);
}

void Server::stop() {
    std::cout << "server: shutting down" << std::endl;
    
    http_server_.stop();
    
    queue_->shutdown();
    worker_pool_->stop();
}