---
title: Tests
---
# Tests

The tests are written with [pytest](https://docs.pytest.org/en/stable/) and are in [tests/](https://github.com/libmonero/monero-python/tree/main/tests).
They test the module as a user of the library does: they import `monero`, the module that CMake builds, and call it. There are
about 1200 of them, on the models, the utilities, the daemon and the three wallet types.

| Page | What it has |
| --- | --- |
| [Test Environment](environment/index.md) | the regtest network in docker that the integration tests run on, and the configuration of the tests |
| [Running the Tests](running/index.md) | the commands: setting up, choosing the tests, reading the results, the logs, debugging, the coverage |
| [Test Files](files/index.md) | what each file of `tests/` tests |
| [Writing Tests](writing/index.md) | how a test is made: the base classes, the wallet tests, the markers, the helpers |
| [VS Code](vscode/index.md) | the tasks, the Testing panel, debugging in Python and in C++ |
| [Coverage](../coverage.md) | the coverage reports of the last run of `main` |

## In short

```bash
./bin/setup_venv.sh && . .venv/bin/activate     # the tools of the tests, at the versions of CI
export PYTHONPATH="$PWD/build"                  # the module that CMake built
pytest -m unit                                  # the unit tests, no server needed
./bin/setup_test_environment.sh                 # the network in docker
pytest -m integration                           # the integration tests
./bin/cleanup_test_environment.sh               # the network down, and what the tests left
```

## Unit and integration tests

Every test has one of two markers, and the two together are the whole suite:

| Marker | What the tests need | How long they take |
| --- | --- | --- |
| `unit` | nothing: the models, the utilities, the calls of the interfaces, an offline full wallet, a keys-only wallet, local fake servers | about half a minute |
| `integration` | a regtest network: two `monerod` nodes and three `monero-wallet-rpc` servers, which `tests/docker-compose.yml` starts | about 45 minutes in CI |

Two more markers are for the tests of the wallet types that do not do something, as [Writing Tests](writing/wallet.md#when-a-wallet-type-does-not-do-something)
explains:

| Marker | Meaning | Passes when |
| --- | --- | --- |
| `not_supported` | the wallet type can not do it | the test raises a "not supported" error |
| `not_implemented` | the wallet type does not do it yet | it is a strict xfail: it xfails while the test fails, and fails once it passes, so that the marker is removed |

## Layout

| Folder | What it tests |
| --- | --- |
| `tests/common` | what is not about a wallet or a daemon: the rpc connection, the errors, `MoneroUtils` (in `monero_utils/`) |
| `tests/daemon/rpc` | the rpc daemon, a file for each topic |
| `tests/daemon/model` | the models of the daemon |
| `tests/wallet` | the wallets, a file for each topic, with a class for each wallet type |
| `tests/wallet/model` | the models of the wallet |
| `tests/utils` | the helpers of the tests, imported as `utils` |
| `tests/config` | the configuration: the servers, the wallets, the network, the data of some tests |

[Test Files](files/index.md) has every file.

## In CI

The CI of each push and pull request (`.github/workflows/ci.yml`) builds the module and runs the tests on what it built:

| Job | Tests |
| --- | --- |
| `unit tests / windows`, `unit tests / mac-arm64`, `unit tests / mac-x86_64` | the unit tests, on the wheel of the platform |
| `unit tests / linux-x86_64` | the unit tests, on the module built with coverage |
| `integration tests / linux-x86_64` | the integration tests, with the network of `tests/docker-compose.yml` |
| `coverage report` | merges the coverage of the two Linux jobs into the [reports](../coverage.md) |

- The summary of each test job lists its xfail tests, and the `not_implemented` ones that pass now.
- The logs of the tests, and of the containers for the integration tests, are artifacts of the run, for 14 days.
- On `main`, the docs are published after the coverage report, with its reports.
