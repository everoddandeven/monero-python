cmake_minimum_required(VERSION 3.15)

project(monero VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (WIN32)
  add_definitions( "-D_GLIBCXX_USE_NANOSLEEP=1" ) # "'sleep_for' is not a member of 'std::this_thread'" in gcc 4.7/4.8
  add_definitions( "-DWIN32_LEAN_AND_MEAN" )
endif()

option(ENABLE_COVERAGE "Enable coverage" OFF)

if(ENABLE_COVERAGE)
  message(STATUS "Coverage enabled")
  add_compile_options(--coverage -O0 -g -fprofile-update=atomic)
  add_link_options(--coverage)
endif()

###################
# monero-cpp
###################

set(MONERO_CPP "${CMAKE_SOURCE_DIR}/external/monero-cpp" CACHE STRING "Monero c++ source directory")
set(MONERO_CPP_SRC "${MONERO_CPP}/src")

###################
# monero-project
###################

set(MONERO_PROJECT "${MONERO_CPP}/external/monero-project" CACHE STRING "Monero project source directory")
set(MONERO_PROJECT_SRC "${MONERO_PROJECT}/src")

############
# Threads
############

find_package(Threads REQUIRED)

############
# Python3
############

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

############
# Pybind11
############

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

############
# Boost
############

set(Boost_NO_BOOST_CMAKE 1)
set(Boost_USE_MULTITHREADED ON)
set(BOOST_COMPONENTS thread serialization filesystem)

# Find Boost headers
set(BOOST_MIN_VER 1.62)
find_package(Boost ${BOOST_MIN_VER} QUIET REQUIRED)

# Boost System is header-only since 1.69
if (Boost_VERSION_STRING VERSION_LESS 1.69.0)
  list(APPEND BOOST_COMPONENTS system)
endif()

find_package(Boost ${BOOST_MIN_VER} QUIET REQUIRED COMPONENTS ${BOOST_COMPONENTS})
message(STATUS "Boost components: ${BOOST_COMPONENTS}")
message(STATUS "Using Boost include dir at ${Boost_INCLUDE_DIR}")

############
# OpenSSL
############

find_package(OpenSSL REQUIRED)
message(STATUS "Using OpenSSL include dir at ${OPENSSL_INCLUDE_DIR}")

if (WIN32)
  list(APPEND OPENSSL_LIBRARIES ws2_32 crypt32 bcrypt)
endif()

########################
# Build python library
########################

set(LIBRARY_SRC_FILES
  src/cpp/common/py_monero_common.cpp
  src/cpp/utils/py_monero_utils.cpp
  src/cpp/py_monero.cpp
)

link_directories(
  ${MONERO_CPP}/build
)

pybind11_add_module(monero ${LIBRARY_SRC_FILES})

if (WIN32)
  target_compile_options(monero PRIVATE -Wa,-mbig-obj)
endif()

target_include_directories(monero PRIVATE
  src/cpp
  "${MONERO_CPP_SRC}/"
  "${MONERO_PROJECT_SRC}/"
  "${MONERO_PROJECT}/contrib/epee/include"
  "${MONERO_PROJECT}/external"
  "${MONERO_PROJECT}/external/easylogging++"
  "${MONERO_PROJECT}/external/rapidjson/include"
  ${pybind11_INCLUDE_DIR}
  ${Boost_INCLUDE_DIR}
  ${OPENSSL_INCLUDE_DIR}
)

target_link_libraries(monero PRIVATE
  monero-cpp

  Threads::Threads
  ${Boost_LIBRARIES}
  ${OPENSSL_LIBRARIES}
)

install(TARGETS monero DESTINATION .)
