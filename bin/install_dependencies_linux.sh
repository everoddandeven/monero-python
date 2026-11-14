#!/usr/bin/env bash
# The packages of apt for the Linux build of build-linux.yml, and for the tests of build.yml: the module is linked to the shared libraries
# of some of them (the boost, zeromq, sodium and protobuf ones), so a job that only runs the module needs them too. The development packages
# bring the libraries, and are the same ones in both so that the module finds at run time what it was linked to.
set -euo pipefail

sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  pkg-config \
  libssl-dev \
  libzmq3-dev \
  libunbound-dev \
  libsodium-dev \
  libunwind8-dev \
  liblzma-dev \
  libreadline6-dev \
  libexpat1-dev \
  libpgm-dev \
  qttools5-dev-tools \
  libhidapi-dev \
  libusb-1.0-0-dev \
  libprotobuf-dev \
  protobuf-compiler \
  libudev-dev \
  libboost-chrono-dev \
  libboost-date-time-dev \
  libboost-filesystem-dev \
  libboost-locale-dev \
  libboost-program-options-dev \
  libboost-regex-dev \
  libboost-serialization-dev \
  libboost-system-dev \
  libboost-thread-dev \
  python3 \
  ccache \
  doxygen \
  graphviz \
  git \
  curl \
  autoconf \
  libtool \
  gperf \
  nettle-dev \
  libevent-dev \
  debhelper \
  python3-all \
  python3-pip \
  lcov
