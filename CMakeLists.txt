cmake_minimum_required(VERSION 3.10)

if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()

project(dis_ultrassom CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Werror -Wpedantic -Wshadow -g")

find_package(PkgConfig REQUIRED)
pkg_check_modules(ARMADILLO REQUIRED armadillo)

include_directories(include ${ARMADILLO_INCLUDES_DIRS})

file(GLOB CORE_SOURCES "src/*.cpp")
list(REMOVE_ITEM CORE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp" "${CMAKE_CURRENT_SOURCE_DIR}/src/app.cpp")

add_library(core_lib STATIC ${CORE_SOURCES})
target_link_libraries(core_lib ${ARMADILLO_LIBRARIES})

add_executable(dis src/main.cpp)
target_link_libraries(dis core_lib)

enable_testing()


find_package(doctest REQUIRED)

file(GLOB TEST_SOURCES "tests/*.cpp")
add_executable(run_tests ${TEST_SOURCES})
target_link_libraries(run_tests core_lib doctest::doctest)

#configure_file(G-1.csv G-1.csv COPYONLY)
#configure_file(H-1.csv H-1.csv COPYONLY)

add_test(NAME cgne_convergence_test COMMAND run_tests)

add_executable(app_cpp src/app.cpp)

target_link_libraries(app_cpp core_lib)