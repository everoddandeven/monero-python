#!/usr/bin/env bash
# Removes the docker containers of the tests with their volumes, and what the tests leave in the repository:
#
#   the wallets           test_wallets/
#   the logs              test_logs/, and the monero_tests_*.log that the tests wrote in the root before test_logs/
#   the coverage          .coverage of coverage.py, coverage.xml and the reports and tracefiles of tests/running/coverage.md
#                         (coverage*.info, coverage_*_html/), the counters of gcov (*.gcda) in the builds of the module and of monero-cpp
#   the caches            .pytest_cache, and the __pycache__ folders of the project
#
# Not the __pycache__ of .venv, of the submodules and of .cache, which are not of the tests, nor the builds themselves.
set -uo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root" || exit 1

# remove docker containers
docker compose -f tests/docker-compose.yml down -v

rm -rf test_wallets test_logs .pytest_cache
rm -f monero_tests_*.log
rm -f .coverage .coverage.* coverage.xml coverage*.info
rm -rf coverage_*_html

# the counters that a run of the tests with the coverage builds wrote, so that the next run counts from zero
for build in build build-debug external/monero-cpp/build; do
    [ -d "$build" ] && find "$build" -name '*.gcda' -delete
done

find . \( -path ./.venv -o -path ./external -o -path ./.git -o -path ./.cache \) -prune \
    -o -type d -name __pycache__ -prune -exec rm -rf {} +
