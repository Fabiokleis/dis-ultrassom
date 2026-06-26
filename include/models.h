#ifndef METADATA_H
#define METADATA_H

#include <string>
#include <json.hpp>


class Metadata {

public:

static nlohmann::json create(
    const std::string& job,
    const std::string& signal,
    const std::string& algorithm,
    int iterations,
    double duration,
    int width,
    int height,
    const std::string& path
);

};


#endif