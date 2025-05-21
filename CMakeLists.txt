cmake_minimum_required(VERSION 3.14)
project(monero LANGUAGES CXX)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 REQUIRED)

set(SOURCES
  src/cpp/py_monero.cpp
)

include_directories(
  ${pybind11_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/src
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/external/monero-project/src
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/external/monero-project/contrib/epee/include
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/external/monero-project/external
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/external/monero-project/external/easylogging++
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/external/monero-project/external/rapidjson/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/common
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/daemon
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/wallet
)

link_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/build
  ${CMAKE_CURRENT_SOURCE_DIR}/lib
)

pybind11_add_module(monero ${SOURCES})

target_link_libraries(monero PRIVATE monero-cpp)

if (MSVC)
  target_compile_options(monero PRIVATE /std:c++17)
else()
  target_compile_options(monero PRIVATE -std=c++17)
endif()
