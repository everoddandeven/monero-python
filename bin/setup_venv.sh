#!/usr/bin/env bash
# Creates the virtual environment .venv for working on the library locally, with the versions that CI builds, tests and makes the
# docs with: requirements-build.txt, tests/requirements.txt and docs/mkdocs/requirements.in. Run it again after a change of one of
# them, it installs what changed.
#
# The files stay apart, each one is what a job of CI installs and what Dependabot updates on its own: a requirements file that
# included them with -r would make Dependabot update them twice.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

python3 -m venv "$root/.venv"
"$root/.venv/bin/pip" install --disable-pip-version-check \
    -r "$root/requirements-build.txt" \
    -r "$root/tests/requirements.txt" \
    -r "$root/docs/mkdocs/requirements.in"

echo "Activate it with: . .venv/bin/activate"
