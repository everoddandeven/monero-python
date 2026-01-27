cmake_minimum_required(VERSION 3.14)

if (WIN32)
  add_definitions( "-D_GLIBCXX_USE_NANOSLEEP=1" ) # "'sleep_for' is not a member of 'std::this_thread'" in gcc 4.7/4.8
  add_definitions( "-DWIN32_LEAN_AND_MEAN" )
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wa,-mbig-obj -O2 -fPIC -F/Library/Frameworks -pthread -lcrypto -lcrypt32 -lbcrypt")
else()
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -F/Library/Frameworks -pthread")
endif()

project(monero LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 REQUIRED)
set(Boost_NO_BOOST_CMAKE 1)
set(Boost_USE_MULTITHREADED ON)
find_package(Boost REQUIRED COMPONENTS system thread serialization filesystem)

set(SOURCES
  src/cpp/common/py_monero_common.cpp
  src/cpp/daemon/py_monero_daemon_model.cpp
  src/cpp/daemon/py_monero_daemon_default.cpp
  src/cpp/daemon/py_monero_daemon_rpc.cpp
  src/cpp/wallet/py_monero_wallet_model.cpp
  src/cpp/wallet/py_monero_wallet.cpp
  src/cpp/wallet/py_monero_wallet_full.cpp
  src/cpp/wallet/py_monero_wallet_rpc.cpp
  src/cpp/utils/py_monero_utils.cpp
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
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/utils
)

link_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/external/monero-cpp/build
)

pybind11_add_module(monero ${SOURCES})

target_link_libraries(monero PRIVATE
  monero-cpp

  Boost::system
  Boost::thread
  Boost::serialization
  Boost::filesystem

  ssl
  crypto
)

if (WIN32)
    target_link_libraries(monero PRIVATE
        ws2_32
        crypt32
        bcrypt
    )
endif()
