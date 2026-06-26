#ifndef JOB_QUEUE_H
#define JOB_QUEUE_H

#include <queue>
#include <mutex>
#include <condition_variable>
#include <functional>


class JobQueue {

private:

    std::queue<std::function<void()>> jobs;

    std::mutex mutex;

    std::condition_variable condition;

    bool stop = false;


public:

    void push(
        std::function<void()> job
    );


    void worker();


    void shutdown();

};


#endif