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
elif [[ "$ARCH" == armv7* || "$ARCH" == "armhf" ]]; then
    ARCH="armhf"
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
    cd build/release &&
    cmake -DSTATIC=ON -DBUILD_64=ON -DCMAKE_BUILD_TYPE=Release ../../
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

CONTROL_FILE="build/${PACKAGE_NAME}/DEBIAN/control"
if [ -f "$CONTROL_FILE" ]; then
    echo "Patching control file architecture to: ${ARCH}"
    sed -i "s/^Architecture: .*/Architecture: ${ARCH}/" "$CONTROL_FILE"
else
    echo "WARNING: control file not found at: $CONTROL_FILE"
fi

dpkg-deb --build build/${PACKAGE_NAME}

echo "Package built successfully: build/${PACKAGE_NAME}.deb"
