#!/usr/bin/env bash
# Builds or serves the site of docs/mkdocs as .github/workflows/docs.yml does, with the versions of docs/mkdocs/requirements.in.
# They are installed in .cache, again when the requirements change.
#
#   ./bin/docs.sh serve   the site at http://127.0.0.1:8000, rebuilt at every change
#   ./bin/docs.sh build   the code of the examples checked and then the site in docs/mkdocs/public, strict, as in CI: an example that
#                         does not pass bin/check_examples.py or a docstring or a reference that does not resolve fails
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
requirements="$root/docs/mkdocs/requirements.in"

case "${1:-serve}" in
    serve) args=(serve);;
    build) args=(build --strict);;
    *) echo "usage: $0 [serve|build]" >&2; exit 1;;
esac

# in a folder of its own, not in a virtual environment: Debian and Ubuntu need python3-venv for one
packages="$root/.cache/mkdocs-$(sha256sum "$requirements" | cut -c1-12)"
if [ ! -f "$packages/.installed" ]; then
    rm -rf "$packages"
    python3 -m pip install --quiet --disable-pip-version-check --target "$packages" -r "$requirements"
    touch "$packages/.installed"
fi

# the code of the examples first, as in CI
if [ "${args[0]}" = build ]; then
    PYTHONPATH="$packages" python3 "$root/bin/check_examples.py"
fi

cd "$root/docs/mkdocs"
# exec: who stops this script, as the stop button of VS Code, stops the server
PYTHONPATH="$packages" exec python3 -m mkdocs "${args[@]}"
