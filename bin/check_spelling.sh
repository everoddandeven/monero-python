#!/usr/bin/env bash
# Checks the spelling of the files of git as .github/workflows/spelling.yml does, with the same codespell: its version is read from that
# workflow, and it is kept in .cache. The words that are not typos are in .codespellrc.
#
#   ./bin/check_spelling.sh        reports the typos, and fails when there are some
#   ./bin/check_spelling.sh -w     fixes the ones that have a single correction
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workflow="$root/.github/workflows/spelling.yml"

version=$(sed -n 's/^ *CODESPELL_VERSION: *//p' "$workflow")
if [ -z "$version" ]; then
    echo "Could not read the version of codespell from $workflow" >&2
    exit 1
fi

venv="$root/.cache/codespell-$version"
if [ ! -x "$venv/bin/codespell" ]; then
    rm -rf "$venv"
    python3 -m venv "$venv"
    "$venv/bin/pip" install --quiet --disable-pip-version-check "codespell==$version"
fi

# the files of git, without the submodules, whose entries are folders, and without what the build and the tests leave around
cd "$root"
git ls-files -z | grep -zv '^external/' | xargs -0 "$venv/bin/codespell" "$@"
