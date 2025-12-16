cmake_minimum_required(VERSION 3.15)
project(QuantCore)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenMP REQUIRED)

set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../eigen-3.4.0")
include_directories(${EIGEN3_INCLUDE_DIR})

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

pybind11_add_module(core_cpp
    bindings/python_bindings.cpp
    src/hello.cpp
)

target_link_libraries(core_cpp PRIVATE OpenMP::OpenMP_CXX)

install(TARGETS core_cpp DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../app/services)
