#!/usr/bin/env bash
# Checks the links to the web of the docs, the docstrings of the stubs and README.md with lychee, as .github/workflows/links.yml does: the
# workflow runs this script. lychee is downloaded once into .cache, from its release on GitHub, and checked against the sha256 of the
# release. The configuration of lychee is lychee.toml.
#
#   ./bin/check_links.sh [options of lychee]   as -vv, which shows where each redirect goes
#
#   GITHUB_TOKEN  a token for the links to GitHub, which answers fewer requests without one: export GITHUB_TOKEN=$(gh auth token)
set -euo pipefail

# not updated by Dependabot: a new version can report more
version=0.24.2

# the files whose links are checked
inputs=(README.md SECURITY.md .github/release-notes.md 'docs/*.md' 'docs/mkdocs/docs/**/*.md' 'src/monero/*.pyi')

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

case "$(uname -s)_$(uname -m)" in
    Linux_x86_64) target=x86_64-unknown-linux-gnu;;
    Linux_aarch64) target=aarch64-unknown-linux-gnu;;
    Darwin_x86_64) target=x86_64-apple-darwin;;
    Darwin_arm64) target=aarch64-apple-darwin;;
    *) echo "lychee is downloaded only for Linux and macOS, on x86_64 and arm64, here" >&2; exit 1;;
esac

lychee="$root/.cache/lychee-$version/lychee"
if [ ! -x "$lychee" ]; then
    archive="lychee-$target.tar.gz"
    url="https://github.com/lycheeverse/lychee/releases/download/lychee-v$version/$archive"
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    curl --retry 5 --retry-delay 5 -fsSLo "$tmp/$archive" "$url"
    curl --retry 5 --retry-delay 5 -fsSLo "$tmp/$archive.sha256" "$url.sha256"

    # the sha256 of the release, against the one of the download: sha256sum on Linux, shasum on macOS
    expected=$(cut -d ' ' -f 1 "$tmp/$archive.sha256")
    if command -v sha256sum > /dev/null; then
        actual=$(sha256sum "$tmp/$archive" | cut -d ' ' -f 1)
    else
        actual=$(shasum -a 256 "$tmp/$archive" | cut -d ' ' -f 1)
    fi
    if [ "$expected" != "$actual" ]; then
        echo "The sha256 of $archive is $actual, the release says $expected" >&2
        exit 1
    fi

    # the binary is in a folder of the archive
    binary=$(tar -tzf "$tmp/$archive" | grep -E '(^|/)lychee$' | head -n 1)
    tar -xzf "$tmp/$archive" -C "$tmp" "$binary"
    mkdir -p "$(dirname "$lychee")"
    install -m 755 "$tmp/$binary" "$lychee"
fi

cd "$root"
# lychee.toml of the root is read on its own
if [ -z "${GITHUB_STEP_SUMMARY:-}" ]; then
    exec "$lychee" --no-progress "$@" "${inputs[@]}"
fi

# in CI, the report goes to the summary of the run as well
report=$(mktemp)
status=0
"$lychee" --no-progress "$@" "${inputs[@]}" 2>&1 | tee "$report" || status=$?
{ echo '### Links'; echo; echo '```'; cat "$report"; echo '```'; } >> "$GITHUB_STEP_SUMMARY"
rm -f "$report"
exit "$status"
