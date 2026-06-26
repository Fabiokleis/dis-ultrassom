#include "job_queue.h"



void JobQueue::push(
    std::function<void()> job
){

    {

        std::lock_guard<std::mutex> lock(mutex);

        jobs.push(job);

    }

    condition.notify_one();

}



void JobQueue::worker()
{


while(true){


    std::function<void()> job;


    {

        std::unique_lock<std::mutex> lock(mutex);


        condition.wait(
            lock,
            [this]{

                return stop || !jobs.empty();

            }
        );


        if(stop && jobs.empty())
            return;


        job = jobs.front();

        jobs.pop();

    }


    job();


}


}



void JobQueue::shutdown()
{

    {

        std::lock_guard<std::mutex> lock(mutex);

        stop=true;

    }


    condition.notify_all();

}