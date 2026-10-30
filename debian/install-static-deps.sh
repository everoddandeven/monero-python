#!/bin/sh
# Installs static expat and unbound in /usr/local, which the archive does not provide
# that way and monero links to. It needs the network and root, so it is meant for a
# build container or a CI runner. Safe to run again.
set -eu

jobs=${JOBS:-1}

# the objects of both go through ccache when it is there
if command -v ccache > /dev/null 2>&1; then
    export CC="ccache gcc"
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

if [ ! -f /usr/local/lib/libexpat.a ]; then
    wget -nv https://github.com/libexpat/libexpat/releases/download/R_2_7_1/expat-2.7.1.tar.bz2
    echo "45c98ae1e9b5127325d25186cf8c511fa814078e9efeae7987a574b482b79b3d  expat-2.7.1.tar.bz2" | sha256sum -c
    tar -xf expat-2.7.1.tar.bz2
    (cd expat-2.7.1 && ./configure --enable-static --disable-shared --with-pic && make -j"$jobs" && make install)
fi

if [ ! -f /usr/local/lib/libunbound.a ]; then
    wget -nv https://www.nlnetlabs.nl/downloads/unbound/unbound-1.22.0.tar.gz
    echo "c5dd1bdef5d5685b2cedb749158dd152c52d44f65529a34ac15cd88d4b1b3d43  unbound-1.22.0.tar.gz" | sha256sum -c
    tar -xzf unbound-1.22.0.tar.gz
    # monero only needs libunbound, skip the daemon and the tools
    (cd unbound-1.22.0 && ./configure --with-libexpat=/usr/local --with-ssl=/usr --enable-static --disable-shared --with-pic && make -j"$jobs" lib && make install-lib)
fi

ldconfig
