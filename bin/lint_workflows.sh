#!/usr/bin/env bash
# Lints the workflows as .github/workflows/lint-workflows.yml does, with the same actionlint and zizmor: their versions,
# and the sha256 of actionlint, are read from that workflow, so they stay those of the CI. They are kept in .cache.
#
#   GH_TOKEN  a token for the audits of zizmor that ask GitHub, they are skipped without it
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workflow="$root/.github/workflows/lint-workflows.yml"
cache="$root/.cache/lint-workflows"

actionlint_version=$(sed -n 's/^ *ACTIONLINT_VERSION: *//p' "$workflow")
actionlint_sha256=$(sed -n 's/^ *ACTIONLINT_SHA256: *//p' "$workflow")
zizmor_version=$(sed -n 's/.*zizmor==\([0-9.]*\).*/\1/p' "$workflow")
if [ -z "$actionlint_version" ] || [ -z "$actionlint_sha256" ] || [ -z "$zizmor_version" ]; then
    echo "Could not read the versions of actionlint and zizmor from $workflow" >&2
    exit 1
fi

case "$(uname -s)_$(uname -m)" in
    Linux_x86_64) platform=linux_amd64;;
    Linux_aarch64) platform=linux_arm64;;
    *) echo "actionlint is downloaded only for Linux x86_64 and arm64 here" >&2; exit 1;;
esac

# the sha256 of the workflow is the one of linux_amd64, the other archives are checked against the checksums of the release
actionlint="$cache/actionlint-$actionlint_version"
if [ ! -x "$actionlint" ]; then
    mkdir -p "$cache"
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    url="https://github.com/rhysd/actionlint/releases/download/v${actionlint_version}"
    curl --retry 5 --retry-delay 5 -fsSLo "$tmp/actionlint.tar.gz" "$url/actionlint_${actionlint_version}_${platform}.tar.gz"
    if [ "$platform" = linux_amd64 ]; then
        echo "$actionlint_sha256  $tmp/actionlint.tar.gz" | sha256sum -c -
    else
        curl --retry 5 --retry-delay 5 -fsSLo "$tmp/checksums.txt" "$url/actionlint_${actionlint_version}_checksums.txt"
        expected=$(grep " actionlint_${actionlint_version}_${platform}.tar.gz\$" "$tmp/checksums.txt" | cut -d' ' -f1)
        echo "$expected  $tmp/actionlint.tar.gz" | sha256sum -c -
    fi
    tar -xzf "$tmp/actionlint.tar.gz" -C "$tmp" actionlint
    mv "$tmp/actionlint" "$actionlint"
fi

# in a folder of its own, not in a virtual environment: Debian and Ubuntu need python3-venv for one
zizmor="$cache/zizmor-$zizmor_version"
if [ ! -x "$zizmor/bin/zizmor" ]; then
    rm -rf "$zizmor"
    python3 -m pip install --quiet --disable-pip-version-check --target "$zizmor" "zizmor==$zizmor_version"
fi

cd "$root"
status=0
echo "actionlint $actionlint_version"
"$actionlint" -color || status=1
echo "zizmor $zizmor_version"
# no bars of progress: in a terminal they break into the lines of the findings, which the problem matcher of VS Code reads
"$zizmor/bin/zizmor" --no-progress .github || status=1
exit $status
