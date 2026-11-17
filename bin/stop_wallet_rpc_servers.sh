#!/usr/bin/env bash

# stop the wallet rpc servers of the test environment, only the rpc wallet tests use them
# the containers and their volumes stay, setup_test_environment.sh starts them again
sudo docker compose -f tests/docker-compose.yml stop xmr_wallet_1 xmr_wallet_2 xmr_wallet_3
