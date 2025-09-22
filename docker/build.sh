#!/bin/bash
set -e

PACKAGE_NAME=${PACKAGE_NAME:-python3-monero_main-1noble1_amd64}

git submodule update --init --recursive
echo "AAAA"
ls
mkdir -p build
cd ./external/monero-cpp
echo "BBBB"
ls
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
