---
title: Monero Python Documentation
hide:
  - navigation
---
# Monero Python Documentation

Welcome to the Monero Python documentation.

The aim of this project is to provide an intuitive and robust way to interact with the Monero cryptocurrency in Python using a clearly defined data model. It provides high level classes representing objects from the Monero environment, like wallets, accounts, addresses and transactions.

Developers can create Monero applications using JSON-RPC or Python bindings to monero v0.18.5.3 'Fluorine Fermi'.

Contributions can be made via issues and pull requests on GitHub, or communicated via the #monero-python workgroup on Matrix.

[:simple-github: GitHub](https://github.com/libmonero/monero-python){ .md-button }
[:simple-matrix: Matrix](https://matrix.to/#/%23monero-python:monero.social){ .md-button }

## What it has

- **Daemon**: `MoneroDaemonRpc`, a client of `monerod`: blocks, transactions, the pool, peers, mining, and listeners of the new blocks
- **Wallets**: three implementations of `MoneroWallet`: `MoneroWalletFull`, a wallet file that syncs with a daemon through the wallet of monero-project; `MoneroWalletRpc`, a client of `monero-wallet-rpc`; `MoneroWalletKeys`, the keys and the addresses of a wallet, offline. [Wallet Support](api/wallet_support.md) says what each of them does
- **Data model**: blocks, transactions, transfers, outputs and the queries that filter them, all serializable to JSON
- **Utilities**: `MoneroUtils`: the validation of addresses, keys and seeds, amounts in atomic units, payment uris
- **Platforms**: deb packages for Debian and Ubuntu on amd64, arm64 and armhf, and wheels for macOS and Windows, with every [release](https://github.com/libmonero/monero-python/releases)

## A quick look

--8<-- "README.md:sample-code"

## The documentation

<div class="grid cards" markdown>

-   :material-download: **Getting Started**

    ---

    Install a release, or build the module from source on Linux, macOS or Windows.

    [:octicons-arrow-right-24: Installation](getting_started/installation.md)

-   :material-book-open-variant: **API Reference**

    ---

    Every class of the library, from the stubs of the module, and the support of each wallet.

    [:octicons-arrow-right-24: Wallet interface](api/wallet.md)

-   :material-code-braces: **Examples**

    ---

    Connecting to the servers, creating wallets, sending payments, querying transactions.

    [:octicons-arrow-right-24: Connect to an RPC server](examples/connect_to_rpc_server.md)

-   :material-test-tube: **Tests**

    ---

    How the tests are organized, how to run them on a regtest network, and their coverage.

    [:octicons-arrow-right-24: Tests](tests/index.md)

</div>
