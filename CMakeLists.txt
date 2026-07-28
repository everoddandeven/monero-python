cmake_minimum_required(VERSION 3.15)

project(monero VERSION 1.0.0 LANGUAGES CXX)

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
# Monero C++
###################

set(MONERO_CPP "${CMAKE_SOURCE_DIR}/external/monero-cpp" CACHE STRING "Monero c++ source directory")
set(MONERO_CPP_SRC "${MONERO_CPP}/src")
set(MONERO_CPP_BUILD "${MONERO_CPP}/build")

add_library(monero-cpp STATIC IMPORTED)
set_target_properties(monero-cpp PROPERTIES IMPORTED_LOCATION
    ${MONERO_CPP_BUILD}/libmonero-cpp.a)

###################
# Monero
###################

set(MONERO_PROJECT "${MONERO_CPP}/external/monero-project" CACHE STRING "Monero project source directory")
set(MONERO_PROJECT_SRC "${MONERO_PROJECT}/src")
set(MONERO_PROJECT_BUILD "${MONERO_PROJECT}/build/release" CACHE STRING "Monero project build directory")

list(APPEND CMAKE_MODULE_PATH "${MONERO_PROJECT}/cmake")

add_library(wallet STATIC IMPORTED)
set_target_properties(wallet PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/lib/libwallet.a)

# libwallet-crypto.a provides x86_64 asm for some wallet functions
if (EXISTS ${MONERO_PROJECT_BUILD}/src/crypto/wallet/libwallet-crypto.a)
  add_library(wallet_crypto_lib STATIC IMPORTED)
  set_target_properties(wallet_crypto_lib PROPERTIES IMPORTED_LOCATION
      ${MONERO_PROJECT_BUILD}/src/crypto/wallet/libwallet-crypto.a)
  set(wallet_crypto wallet_crypto_lib)
endif()

add_library(lmdb STATIC IMPORTED)
set_target_properties(lmdb PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/external/db_drivers/liblmdb/liblmdb.a)

add_library(epee STATIC IMPORTED)
set_target_properties(epee PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/contrib/epee/src/libepee.a)

add_library(rpc_base STATIC IMPORTED)
set_target_properties(rpc_base PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/rpc/librpc_base.a)

add_library(net STATIC IMPORTED)
set_target_properties(net PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/net/libnet.a)

add_library(hardforks STATIC IMPORTED)
set_target_properties(hardforks PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/hardforks/libhardforks.a)
    
add_library(easylogging STATIC IMPORTED)
set_target_properties(easylogging PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/external/easylogging++/libeasylogging.a)

add_library(cryptonote_core STATIC IMPORTED)
set_target_properties(cryptonote_core PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/cryptonote_core/libcryptonote_core.a)

add_library(cryptonote_protocol STATIC IMPORTED)
set_target_properties(cryptonote_protocol PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/cryptonote_protocol/libcryptonote_protocol.a)

add_library(cryptonote_basic STATIC IMPORTED)
set_target_properties(cryptonote_basic PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/cryptonote_basic/libcryptonote_basic.a)
    
add_library(cryptonote_format_utils_basic STATIC IMPORTED)
set_target_properties(cryptonote_format_utils_basic PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/cryptonote_basic/libcryptonote_format_utils_basic.a)

add_library(mnemonics STATIC IMPORTED)
set_target_properties(mnemonics PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/mnemonics/libmnemonics.a)

add_library(common STATIC IMPORTED)
set_target_properties(common PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/common/libcommon.a)

add_library(cncrypto STATIC IMPORTED)
set_target_properties(cncrypto PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/crypto/libcncrypto.a)

add_library(ringct STATIC IMPORTED)
set_target_properties(ringct PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/ringct/libringct.a)

add_library(ringct_basic STATIC IMPORTED)
set_target_properties(ringct_basic PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/ringct/libringct_basic.a)

add_library(blockchain_db STATIC IMPORTED)
set_target_properties(blockchain_db PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/blockchain_db/libblockchain_db.a)

add_library(blocks STATIC IMPORTED)
set_target_properties(blocks PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/blocks/libblocks.a)

add_library(checkpoints STATIC IMPORTED)
set_target_properties(checkpoints PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/checkpoints/libcheckpoints.a)

add_library(device STATIC IMPORTED)
set_target_properties(device PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/device/libdevice.a)
    
add_library(device_trezor STATIC IMPORTED)
set_target_properties(device_trezor PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/device_trezor/libdevice_trezor.a)

add_library(multisig STATIC IMPORTED)
set_target_properties(multisig PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/multisig/libmultisig.a)

add_library(version STATIC IMPORTED)
set_target_properties(version PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/src/libversion.a)
    
add_library(randomx STATIC IMPORTED)
set_target_properties(randomx PROPERTIES IMPORTED_LOCATION
    ${MONERO_PROJECT_BUILD}/external/randomx/librandomx.a)

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
set(BOOST_COMPONENTS thread serialization filesystem program_options)

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

############
# Unbound
############

find_package(Unbound REQUIRED)
message(STATUS "Using libunbound library at ${UNBOUND_LIBRARIES}")

if (APPLE)
  find_library(EXPAT_LIBRARY expat HINTS /opt/homebrew/opt/expat/lib /usr/local/opt/expat/lib)
  if (EXPAT_LIBRARY)
    list(APPEND UNBOUND_LIBRARIES ${EXPAT_LIBRARY})
  endif()
  find_library(EVENT_LIBRARY NAMES event event_core HINTS /opt/homebrew/opt/libevent/lib /usr/local/opt/libevent/lib)
  if (EVENT_LIBRARY)
    list(APPEND UNBOUND_LIBRARIES ${EVENT_LIBRARY})
  endif()
  find_library(NGHTTP2_LIBRARY nghttp2 HINTS /opt/homebrew/opt/libnghttp2/lib /usr/local/opt/libnghttp2/lib)
  if (NGHTTP2_LIBRARY)
    list(APPEND UNBOUND_LIBRARIES ${NGHTTP2_LIBRARY})
  endif()
endif()

############
# LibUSB
############

find_library(usb_LIBRARY NAMES usb-1.0 libusb usb)
set(LibUSB_LIBRARIES ${usb_LIBRARY})

############
# HIDAPI
############

find_package(HIDAPI REQUIRED)
message(STATUS "Using HIDAPI include dir at ${HIDAPI_INCLUDE_DIR}")

############
# libsodium
############

find_library(SODIUM_LIBRARY sodium REQUIRED)
message(STATUS "Using libsodium library at ${SODIUM_LIBRARY}")

############
# Protobuf
############

if (NOT APPLE)
  include(FindProtobuf)
  find_package(Protobuf)
  message(STATUS "Protobuf lib: ${Protobuf_LIBRARY}, inc: ${Protobuf_INCLUDE_DIR}, protoc: ${Protobuf_PROTOC_EXECUTABLE}")
endif()

########################
# Build python library
########################

set(LIBRARY_SRC_FILES
  src/cpp/common/py_monero_common.cpp
  src/cpp/common/py_monero_common_bindings.cpp
  src/cpp/daemon/py_monero_daemon_bindings.cpp
  src/cpp/wallet/py_monero_wallet_bindings.cpp
  src/cpp/utils/py_monero_utils.cpp
  src/cpp/utils/py_monero_utils_bindings.cpp
  src/cpp/py_monero.cpp
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
  ${HIDAPI_INCLUDE_DIR}
  ${Protobuf_INCLUDE_DIR}
  ${UNBOUND_INCLUDE_DIR}
)

set(MONERO_PYTHON_LINK_LIBS 
  monero-cpp
  wallet
  rpc_base
  net
  lmdb
  easylogging
  cryptonote_core
  cryptonote_protocol
  cryptonote_basic
  cryptonote_format_utils_basic
  mnemonics
  ringct
  ringct_basic
  common
  blockchain_db
  blocks
  checkpoints
  device
  device_trezor
  multisig
  version
  cncrypto
  randomx
  epee
  hardforks
  ${wallet_crypto}

  Threads::Threads
  ${Boost_LIBRARIES}
  ${OPENSSL_LIBRARIES}
  ${Protobuf_LIBRARY}
  ${LibUSB_LIBRARIES}
  ${SODIUM_LIBRARY}
  ${HIDAPI_LIBRARIES}
  ${UNBOUND_LIBRARIES}
)

target_link_libraries(monero PRIVATE ${MONERO_PYTHON_LINK_LIBS})

install(TARGETS monero DESTINATION .)
