#!/bin/bash

# Created: Mecanik (https://github.com/Mecanik)
# Description: This script installs all the dependencies required to build Monero.
# Usage: ./install_monero_deps.sh
# Note: This script is intended for Debian-based systems (e.g., Ubuntu).

set -e

echo "Updating package list..."
sudo apt update

echo "Installing all Monero build dependencies..."
sudo apt install -y \
  build-essential cmake pkg-config \
  python3-dev python3-pip python3-venv \
  libboost-all-dev \
  libprotobuf-dev protobuf-compiler \
  libssl-dev \
  libzmq3-dev \
  libsodium-dev \
  libhidapi-dev \
  libunbound-dev \
  libusb-1.0-0-dev \
  libreadline-dev \
  libpgm-dev \
  libnorm-dev \
  libcap-dev \
  qtbase5-dev qttools5-dev-tools

echo "Dependencies installed successfully."
