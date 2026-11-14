#!/usr/bin/env bash

# ccache for the compilations when it is installed, the plain build otherwise. monero-project and the module look for it themselves
# (USE_CCACHE in their CMakeLists.txt), monero-cpp has to be told to use it
CMAKE_CCACHE_ARGS=()
if command -v ccache > /dev/null 2>&1; then
    echo "Using ccache: $(command -v ccache)"
    CMAKE_CCACHE_ARGS=(-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache)
fi

# build monero-project dependencies
cd ./external/monero-cpp/external/monero-project/ || exit 1
git submodule update --init --force || exit 1
HOST_NCORES=$(nproc 2>/dev/null || shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)
if [[ $(uname -s) == "MINGW64_NT"* || $(uname -s) == "MSYS"* ]]; then
    bit=$(getconf LONG_BIT)
    FOLDER=$(cd ${MINGW_PREFIX}/.. && pwd -W)
    if [ "$bit" == "64" ]; then
        cmake -G "MSYS Makefiles" \
            -D STATIC=ON \
            -D ARCH="x86-64" \
            -D BUILD_64=ON \
            -D CMAKE_BUILD_TYPE=Release \
            -D BUILD_TAG="win-x64" \
            -D CMAKE_TOOLCHAIN_FILE=../../cmake/64-bit-toolchain.cmake \
            -D MSYS2_FOLDER="$FOLDER" \
            ../../
            
        make -j"$HOST_NCORES" wallet cryptonote_protocol || exit 1
    else
        cmake -G "MSYS Makefiles" \
            -D STATIC=ON \
            -D ARCH="i686" \
            -D BUILD_64=OFF \
            -D CMAKE_BUILD_TYPE=Release \
            -D BUILD_TAG="win-x32" \
            -D CMAKE_TOOLCHAIN_FILE=../../cmake/32-bit-toolchain.cmake \
            -D MSYS2_FOLDER="$FOLDER" \
            ../../
            
        make -j"$HOST_NCORES" wallet cryptonote_protocol || exit 1
    fi
else
    # OS is not windows
    mkdir -p build/release &&
    cd build/release &&
    cmake -DCMAKE_BUILD_TYPE=Release ../../
    make -j$HOST_NCORES wallet cryptonote_protocol || exit 1
fi
cd ../../../../

# build libmonero-cpp shared library
mkdir -p build && 
cd build && 
cmake .. "${CMAKE_CCACHE_ARGS[@]}" && 
cmake --build . && 
make .
cd ../../../

# build libmonero-python shared library
mkdir -p build &&
cd build &&
cmake ..
make -j$HOST_NCORES

