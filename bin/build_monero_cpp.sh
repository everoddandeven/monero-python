#!/usr/bin/env bash
# Builds monero-project and monero-cpp, the static libraries the python module links to.
# CI and the deb package use it on Linux and macOS. Windows has its own toolchain,
# see .github/workflows/build-windows.yml.
#
#   JOBS      parallel jobs for monero-project, 3 by default
#   COVERAGE  ON builds monero-cpp with coverage
#   OPENSSL_ROOT_DIR  the openssl both projects are built with, they look for brew's otherwise on macOS
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
jobs=${JOBS:-3}

# monero builds with -march=native unless it is told which cpu to build for, and objects compiled
# on a machine with newer instructions, restored by ccache or shipped in a package, end in an illegal
# instruction on another cpu
case $(uname -m) in
    x86_64) arch=x86-64;;
    aarch64|arm64) arch=armv8-a;;
    armv7l|armv8l) arch=armv7-a;;
    *) arch=native;;
esac

openssl_args=()
if [ -n "${OPENSSL_ROOT_DIR:-}" ]; then
    openssl_args+=(-DOPENSSL_ROOT_DIR="$OPENSSL_ROOT_DIR")
fi

# monero-project picks ccache up on its own
cd "$root/external/monero-cpp/external/monero-project"
mkdir -p build/release
cd build/release
cmake -DSTATIC=ON -DARCH="$arch" -DBUILD_64=ON -DCMAKE_BUILD_TYPE=Release ${openssl_args[@]+"${openssl_args[@]}"} ../../
make -j"$jobs" wallet cryptonote_protocol

# monero-cpp has to be told to use it
cd "$root/external/monero-cpp"
mkdir -p build
cd build
cmake_args=(${openssl_args[@]+"${openssl_args[@]}"})
if command -v ccache > /dev/null 2>&1; then
    cmake_args+=(-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache)
fi
if [ "${COVERAGE:-OFF}" = ON ]; then
    cmake_args+=(-DENABLE_COVERAGE=ON)
fi
cmake .. ${cmake_args[@]+"${cmake_args[@]}"}
cmake --build .
