#!/usr/bin/env bash
# Builds libunbound as a static library in /usr/local against openssl@3, for the macOS builds (build-macos.yml and test.yml). It needs the
# formulae expat and openssl@3 of brew, and sudo for the install.
#
# The unbound of brew is built with OpenSSL 4, and the module links OpenSSL 3 as boost 1.85 does not build with 4: the same as the
# build of monero-cpp does. It is the same version and the same checksum as debian/install-static-deps.sh has for Linux. The library
# is made with no libevent and no DoH, so the module needs neither libevent nor nghttp2.
set -euo pipefail

version=1.22.0
sha256=c5dd1bdef5d5685b2cedb749158dd152c52d44f65529a34ac15cd88d4b1b3d43

# the headers and the library of brew's unbound would be found before the ones of /usr/local
if brew list --versions unbound > /dev/null 2>&1; then
    brew unlink unbound
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

curl --retry 5 --retry-delay 5 -fsSLO "https://www.nlnetlabs.nl/downloads/unbound/unbound-${version}.tar.gz"
echo "${sha256}  unbound-${version}.tar.gz" | shasum -a 256 -c -
tar xzf "unbound-${version}.tar.gz"
cd "unbound-${version}"
./configure --with-libexpat="$(brew --prefix expat)" --with-ssl="$(brew --prefix openssl@3)" --with-libunbound-only --with-libevent=no --enable-static --disable-shared --with-pic
make -j3
sudo make install
