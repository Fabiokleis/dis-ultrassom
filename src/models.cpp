#include "metadata.h"


using json=nlohmann::json;



json Metadata::create(
    const std::string& job,
    const std::string& signal,
    const std::string& algorithm,
    int iterations,
    double duration,
    int width,
    int height,
    const std::string& path
){


return json{

    {"job_id",job},

    {"signal_id",signal},

    {"algorithm",algorithm},

    {"iterations",iterations},

    {"duration_ms",duration},

    {"image_width",width},

    {"image_height",height},

    {"image_path",path}

};

}