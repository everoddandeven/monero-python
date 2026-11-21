---
title: Test Environment
---
# Test Environment

The unit tests need only the module. The integration tests need a Monero network: two `monerod` nodes and three
`monero-wallet-rpc` servers on **regtest**, a private chain that the tests grow and reset themselves, in docker. These pages are
about that network and the configuration of the tests. [Running the Tests](../running/index.md) has the commands of pytest.

| Page | What it has |
| --- | --- |
| [Docker Network](network.md) | starting and stopping the network, its containers, how the tests use it |
| [Configuration](configuration.md) | the settings of `tests/config/config.ini`, key by key, and the other files of `tests/config` |
| [Servers Not in Docker](own_servers.md) | running the integration tests on servers of your own |
| [Troubleshooting](troubleshooting.md) | what can go wrong, and what to do |

## Requirements

| What | For | How |
| --- | --- | --- |
| the `monero` module, built | all the tests | [Build on Linux and macOS](../../getting_started/build_linux_macos.md), in `build/` |
| Python with the tools of the tests | all the tests | `./bin/setup_venv.sh`, or `pip install -r tests/requirements.txt` |
| Docker with Compose | the integration tests | [Docker Engine](https://docs.docker.com/engine/install/), the `docker compose` plugin |

The versions of the tools of the tests are pinned in `tests/requirements.txt`: pytest, pytest-cov, pytest-rerunfailures,
pytest-timeout, coverage, typing_extensions and PyYAML. They are the ones that CI runs with, and Dependabot updates them.
