#!/usr/bin/env bash
# Builds monero-project, monero-cpp and the module. JOBS is the number of compilers at once for the module, and for monero-project
# on Linux and macOS, 3 by default
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

case "$(uname -s)" in
    # the script of monero-cpp has the toolchain of msys2, as in the steps of the README for Windows
    MINGW64_NT*|MSYS*)
        # monero-cpp has to be told to use ccache, monero-project and the module look for it themselves
        ccache_args=()
        if command -v ccache > /dev/null 2>&1; then
            ccache_args=(-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache)
        fi
        (cd "$root/external/monero-cpp" && ./bin/build_libmonero_cpp.sh ${ccache_args[@]+"${ccache_args[@]}"});;
    # the one of CI, which expects the submodules of monero-project to be there
    *)
        git -C "$root/external/monero-cpp/external/monero-project" submodule update --init --force
        "$root/bin/build_monero_cpp.sh";;
esac

cmake -S "$root" -B "$root/build"
cmake --build "$root/build" -j"${JOBS:-3}"
