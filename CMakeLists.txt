cmake_minimum_required(VERSION 3.10)

project(dis_ultrassom CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Werror -Wpedantic -Wshadow -g")

find_package(PkgConfig REQUIRED)
pkg_check_modules(ARMADILLO REQUIRED armadillo)

include_directories(include ${ARMADILLO_INCLUDES_DIRS})
set(BACKUP_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

string(REPLACE "-Werror" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
string(REPLACE "-Wpedantic" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

set(CMAKE_POLICY_VERSION_MINIMUM 3.5)
add_subdirectory(deps/cppuprofile)

set(CMAKE_CXX_FLAGS "${BACKUP_CXX_FLAGS}")

file(GLOB CORE_SOURCES "src/*.cpp")
list(REMOVE_ITEM CORE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp")

add_library(core_lib STATIC ${CORE_SOURCES})
#target_link_libraries(core_lib ${ARMADILLO_LIBRARIES})
target_link_libraries(core_lib ${ARMADILLO_LIBRARIES} cppuprofile)

add_executable(dis src/main.cpp)
#target_link_libraries(dis core_lib)
target_link_libraries(dis core_lib cppuprofile)

enable_testing()


find_package(doctest REQUIRED)

file(GLOB TEST_SOURCES "tests/*.cpp")
add_executable(run_tests ${TEST_SOURCES})
#target_link_libraries(run_tests core_lib doctest::doctest)
target_link_libraries(run_tests core_lib doctest::doctest cppuprofile)

#configure_file(G-1.csv G-1.csv COPYONLY)
#configure_file(H-1.csv H-1.csv COPYONLY)

add_test(NAME cgne_convergence_test COMMAND run_tests)
