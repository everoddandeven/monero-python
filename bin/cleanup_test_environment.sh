#!/usr/bin/env bash
# Removes the docker containers of the tests with their volumes, and what the tests leave: the wallets, the logs, the cache of pytest
# and the __pycache__ folders of the project. Not the ones of .venv, of the submodules and of .cache, which are not of the tests.
set -uo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root" || exit 1

# remove docker containers
docker compose -f tests/docker-compose.yml down -v

rm -rf test_wallets .pytest_cache
rm -f monero_tests_*.log
find . \( -path ./.venv -o -path ./external -o -path ./.git -o -path ./.cache \) -prune \
    -o -type d -name __pycache__ -prune -exec rm -rf {} +
