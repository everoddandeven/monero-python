#!/usr/bin/env bash

# Created: everoddandeven (https://github.com/everoddandeven)
# Edited: Mecanik (https://github.com/Mecanik)
# Description: This script initializes and updates git submodules recursively.
# It also runs the appropriate bootstrap script for the Boost library based on the operating system.
# Usage: ./update_submodules.sh

# Initialize submodules recursively
git submodule update --init --recursive

# Enter boost submodule and run bootstrap and b2 headers
BOOST_DIR="./external/boost"

if [ -d "$BOOST_DIR" ]; then
  cd "$BOOST_DIR" || exit

  if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "Running bootstrap.bat for Windows"
    ./bootstrap.bat
    echo "Generating Boost headers (Windows)"
    ./b2.exe headers
  else
    echo "Running bootstrap.sh for Unix/Linux/macOS"
    ./bootstrap.sh
    echo "Generating Boost headers (Unix/Linux/macOS)"
    ./b2 headers
  fi

  cd ../../
else
  echo "Boost submodule not found!"
fi
