#!/bin/sh

#EMCC_DEBUG=1

# build boost library
cd ./external/boost/ && 
./bootstrap.sh && 
./b2 headers && 
cd ../../

# build libmonero-cpp shared library
cd ./external/monero-cpp/ && 
./bin/build_libmonero_cpp.sh &&

# copy libmonero-cpp shared library to ./build
cd ../../ &&
mkdir -p ./build &&
cp ./external/monero-cpp/build/libmonero-cpp.* ./build &&

# build monero-python
mkdir -p build && 
cd build && 
cmake .. && 
make .
