#!/usr/bin/env bash

# start docker containers
sudo docker compose -f tests/docker-compose.yml up -d node_1 node_2 xmr_wallet_1 xmr_wallet_2
