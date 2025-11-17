#!/bin/bash
set -e

DISTRO_CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d'=' -f2)
DEFAULT_VERSION="0.0.1"

if [ -z "$DISTRO_CODENAME" ]; then
    DISTRO_CODENAME=$(lsb_release -c -s 2>/dev/null || echo "unknown")
fi

ARCH=$(dpkg --print-architecture 2>/dev/null || uname -m)
if [ "$ARCH" == "x86_64" ]; then
    ARCH="amd64"
elif [[ "$ARCH" == arm64* || "$ARCH" == aarch64* ]]; then
    ARCH="arm64"
fi

PACKAGE_NAME=${PACKAGE_NAME:-python3-monero_${DEFAULT_VERSION}-1${DISTRO_CODENAME}1_${ARCH}}

echo "Building package: ${PACKAGE_NAME}"
echo "Distro codename: ${DISTRO_CODENAME}"
echo "Architecture: ${ARCH}"

git submodule update --init --recursive
mkdir -p build

# build monero-project dependencies
cd ./external/monero-cpp/external/monero-project/
git submodule update --init --force
HOST_NCORES=$(nproc 2>/dev/null || shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)
if [[ $(uname -s) == "MINGW64_NT"* || $(uname -s) == "MSYS"* ]]; then
    bit=$(getconf LONG_BIT)
    if [ "$bit" == "64" ]; then
        make release-static-win64 -j$HOST_NCORES
    else
        make release-static-win32 -j$HOST_NCORES
    fi
else
    # OS is not windows
    mkdir -p build/release &&
    cd build/release
    if [ "$ARCH" == "amd64" ]; then
        cmake -D STATIC=ON -D BUILD_64=ON -D CMAKE_BUILD_TYPE=Release ../../
    elif [ "$ARCH" == "armhf" ]; then
        cmake -D BUILD_TESTS=OFF -D ARCH="armv7-a" -D STATIC=ON -D BUILD_64=OFF -D CMAKE_BUILD_TYPE=Release -D BUILD_TAG="linux-armv7" ../../
    elif [ "$ARCH" == "i386" ]; then
        cmake -D STATIC=ON -D ARCH="i686" -D BUILD_64=OFF -D CMAKE_BUILD_TYPE=Release -D BUILD_TAG="linux-x86" ../../
    elif [ "$ARCH" == "arm64" ]; then
        cmake -D BUILD_TESTS=OFF -D ARCH="armv8-a" -D STATIC=ON -D BUILD_64=ON -D CMAKE_BUILD_TYPE=Release -D BUILD_TAG="linux-armv8" ../../
    else
        echo "Unsupported architecture"
        exit 1
    fi
    make -j$HOST_NCORES wallet cryptonote_protocol
fi
cd ../../../../

# build libmonero-cpp shared library
mkdir -p build && 
cd build && 
cmake .. && 
cmake --build . && 
make .
cd ../../../

pip3 install . --target build/${PACKAGE_NAME}/usr/lib/python3/dist-packages

cp -R src/python build/${PACKAGE_NAME}/usr/lib/python3/dist-packages/monero
rm -rf build/${PACKAGE_NAME}/usr/lib/python3/dist-packages/pybind11*
rm -rf build/${PACKAGE_NAME}/usr/lib/python3/dist-packages/bin
cp -R "debian/${DISTRO_CODENAME}" "build/${PACKAGE_NAME}/DEBIAN"
cp external/monero-cpp/build/libmonero-cpp.so build/${PACKAGE_NAME}/usr/lib/
dpkg-deb --build build/${PACKAGE_NAME}

echo "Package built successfully: build/${PACKAGE_NAME}.deb"
