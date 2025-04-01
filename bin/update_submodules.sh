#!/usr/bin/env bash

# Created: everoddandeven (https://github.com/everoddandeven)
# Edited: Mecanik (https://github.com/Mecanik)
# Description: Reinitializes Boost submodule to compatible version and generates headers.
# Usage: ./update_submodules.sh

set -e

BOOST_DIR="./external/boost"

echo "Removing existing Boost submodule (if exists)..."
git submodule deinit -f "$BOOST_DIR" || true
git rm -rf "$BOOST_DIR" || true
rm -rf ".git/modules/$BOOST_DIR"
rm -rf "$BOOST_DIR"

echo "Cloning Boost 1.77.0 (Monero-compatible)..."
mkdir -p external
cd external
git clone --branch boost-1.77.0 --depth 1 https://github.com/boostorg/boost.git
cd boost

echo "Initializing Boost submodules (minimal)..."
git submodule update --init --recursive --depth 1

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OS" == "Windows_NT" ]]; then
  echo "Running bootstrap.bat for Windows..."
  ./bootstrap.bat
  echo "Generating Boost headers (Windows)..."
  ./b2.exe headers
else
  echo "Running bootstrap.sh for Unix/Linux/macOS..."
  ./bootstrap.sh
  echo "Generating Boost headers (Unix/Linux/macOS)..."
  ./b2 headers
fi

cd ../../

echo "Boost 1.77.0 fully initialized and headers generated"
