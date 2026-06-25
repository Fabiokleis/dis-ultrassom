#include "server.h"

#include <httplib.h>
#include <iostream>



void Server::start(int port)
{

httplib::Server app;



app.Get("/",[](auto&,auto& res){

res.set_content(
"{\"status\":\"ok\"}",
"application/json"
);

});



std::cout
<<"Servidor C++ porta "
<<port
<<"\n";



app.listen(
"0.0.0.0",
port
);


}