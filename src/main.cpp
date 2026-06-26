#include "server.h"
#include <iostream>
#include <csignal>

Server* server_instance = nullptr;

void signal_handler(int signal) {
    if (server_instance) {
        std::cout << "\nreceived signal " << signal << ", shutting down..." << std::endl;
        server_instance->stop();
        exit(0);
    }
}

int main(int argc, char* argv[]) {
    int port = 8000;
    int num_workers = 4;
    
    if (argc > 1) {
        port = std::atoi(argv[1]);
    }
    if (argc > 2) {
        num_workers = std::atoi(argv[2]);
    }
    
    std::cout << "starting c++ ultrassom reconstruction server" << std::endl;
    std::cout << "port: " << port << std::endl;
    std::cout << "workers: " << num_workers << std::endl;
    
    Server server(port, num_workers);
    server_instance = &server;
    
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);
    
    server.start();
    
    return 0;
}
