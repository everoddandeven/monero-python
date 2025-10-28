#!/bin/bash
set -e

DISTRO_CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d'=' -f2)
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

if [ -z "$DISTRO_CODENAME" ]; then
    DISTRO_CODENAME=$(lsb_release -c -s 2>/dev/null || echo "unknown")
fi

PACKAGE_NAME=${PACKAGE_NAME:-python3-monero_${BRANCH_NAME}-1${DISTRO_CODENAME}1_amd64}

git submodule update --init --recursive
mkdir -p build
cd ./external/monero-cpp
./bin/build_libmonero_cpp.sh
cp build/libmonero* ../../build
cd ../../

pip3 install . --target build/${PACKAGE_NAME}/usr/lib/python3/dist-packages

cp -R src/python build/${PACKAGE_NAME}/usr/lib/python3/dist-packages/monero
rm -rf build/${PACKAGE_NAME}/usr/lib/python3/dist-packages/pybind11*
rm -rf build/${PACKAGE_NAME}/usr/lib/python3/dist-packages/bin
cp -R debian build/${PACKAGE_NAME}/DEBIAN
cp external/monero-cpp/build/libmonero-cpp.so build/${PACKAGE_NAME}/usr/lib/
dpkg-deb --build build/${PACKAGE_NAME}

echo "Package built: build/${PACKAGE_NAME}.deb"
