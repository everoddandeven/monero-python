#!/usr/bin/env bash
# Prints the versions of the tools and of the libraries that bin/install_dependencies_linux.sh installs with apt, for the log of a job. They are the ones that the
# distribution of the runner has, not pinned ones, so what a run built and tested with is only known from its log.
set -uo pipefail

# only the installed ones: a pattern also matches the packages of other versions that the distribution has, which are not installed
dpkg-query -W -f='${db:Status-Abbrev} ${Package} ${Version}\n' \
  libssl-dev libzmq3-dev libunbound-dev libsodium-dev libunwind8-dev liblzma-dev libexpat1-dev libpgm-dev \
  libhidapi-dev libusb-1.0-0-dev libprotobuf-dev protobuf-compiler 'libboost1.*-dev' \
  cmake ccache python3 lcov 2> /dev/null | awk '$1 == "ii" { print $2, $3 }'
g++ --version | head -n 1
