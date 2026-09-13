#!/usr/bin/env bash

# remove docker containers
sudo docker compose -f tests/docker-compose.yml down -v
rm -rf test_wallets 2>&1
rm monero_tests_* 2>&1
rm -rf .pytest_cache 2>&1
rm -rf __pycache__ 2>&1
rm -rf tests/__pycache__ 2>&1
rm -rf tests/utils/__pycache__ 2>&1
