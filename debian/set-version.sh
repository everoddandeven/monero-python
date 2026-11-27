#!/bin/sh
# Adds an entry to debian/changelog for the version declared in pyproject.toml, so the
# version is not repeated here. The package is named like python3-monero_0.9.13-1noble1_amd64.deb.
# With a snapshot, such as the commit that is built, it is python3-monero_0.9.13~git1a2b3c4-1noble1_amd64.deb: the tilde sorts it
# before the release, so a release is always newer than the snapshots that came before it.
#
# usage: debian/set-version.sh [distribution [snapshot]]    the distribution is the one of the system by default
set -eu

cd "$(dirname "$0")/.."

version=$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml | head -n 1)
if [ -z "$version" ]; then
    echo "ERROR: could not read the version from pyproject.toml" >&2
    exit 1
fi

dist=${1:-$(. /etc/os-release && echo "$VERSION_CODENAME")}
snapshot=${2:-}
version=${version}${snapshot:+~$snapshot}
full_version="${version}-1${dist}1"

if [ "$(dpkg-parsechangelog -S Version)" = "$full_version" ]; then
    echo "debian/changelog is already at $full_version"
    exit 0
fi

maintainer=$(sed -n 's/^Maintainer: //p' debian/control)
{
    printf 'python3-monero (%s) %s; urgency=medium\n\n' "$full_version" "$dist"
    printf '  * Build of %s for %s.\n\n' "$version" "$dist"
    printf ' -- %s  %s\n\n' "$maintainer" "$(date -R)"
    cat debian/changelog
} > debian/changelog.new
mv debian/changelog.new debian/changelog
echo "debian/changelog is now at $full_version"
