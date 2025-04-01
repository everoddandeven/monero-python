#!/bin/bash

# Created: everoddandeven (https://github.com/everoddandeven)
# Edited: Mecanik (https://github.com/Mecanik)
# Description: This script builds the libmonero-cpp shared library and copies it to the ./build directory.
# Usage: ./build_libmonero_python.sh

set -e

cd ./external/monero-cpp

if [ ! -f build/libmonero-cpp.so ]; then
    echo "libmonero-cpp.so not found, building..."
    mkdir -p build
    cd build
    cmake .. -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release
    cmake --build . -j"$(nproc)"
    cd ..
else
    echo "libmonero-cpp.so already built."
fi

cd ../..

echo "Copying shared lib to ./build/"
mkdir -p ./build
cp ./external/monero-cpp/build/libmonero-cpp.* ./build/
