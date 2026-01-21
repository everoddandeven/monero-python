#!/usr/bin/env bash

# remove docker containers
sudo docker compose -f tests/docker-compose.yml down -v
