# Monero Python Library
[![Build](https://github.com/everoddandeven/monero-python/actions/workflows/build-deb.yml/badge.svg)](https://github.com/everoddandeven/monero-python/actions/workflows/build-deb.yml)
[![Tests](https://github.com/everoddandeven/monero-python/actions/workflows/test.yml/badge.svg)](https://github.com/everoddandeven/monero-python/actions/workflows/test.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/aeff91a5b1d543ddb400f88ffce150a8)](https://app.codacy.com/gh/everoddandeven/monero-python/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

> [!WARNING]
>
> monero-python is currently under maintenance, expect bugs and breaking changes.
> The maintenance of this project has been generously funded by the [Monero CCS](https://ccs.getmonero.org/proposals/everoddandeven-monero-python-maintenance.html).

A Python library for creating Monero applications using RPC and Python bindings to [monero v0.18.4.4 'Fluorine Fermi'](https://github.com/monero-project/monero/tree/v0.18.4.4).

* Supports wallet and daemon RPC clients.
* Supports client-side wallets using Python bindings.
* Supports multisig, view-only, and offline wallets.
* Wallet types are interchangeable by conforming to a [common interface](https://woodser.github.io/monero-java/javadocs/monero/wallet/MoneroWallet.html).
* Uses a clearly defined [data model and API specification](https://woodser.github.io/monero-java/monero-spec.pdf) intended to be intuitive and robust.
* Query wallet transactions, transfers, and outputs by their properties.
* Fetch and process binary data from the daemon (e.g. raw blocks).
* Receive notifications when blocks are added to the chain or when wallets sync, send, or receive.

## Architecture

<p align="center">
	<img width="85%" height="auto" src="docs/architecture.png"/><br>
	<i>Build Python
     applications using RPC or Python bindings to <a href="https://github.com/monero-project/monero">monero-project/monero</a>.  Wallet implementations are interchangeable by conforming to a common interface, <a href="https://woodser.github.io/monero-java/javadocs/monero/wallet/MoneroWallet.html">MoneroWallet</a>.</i>
</p>


## Sample code

```python
from monero import *

# connect to daemon
daemon: MoneroDaemon = MoneroDaemonRpc("http://localhost:38081", "superuser", "abctesting123")
height: int = daemon.get_height() # 1523651
txsInPool: list[MoneroTx] = daemon.get_tx_pool() # get transactions in the pool

# create wallet from mnemonic phrase using Python bindings to monero-project

wallet_config = MoneroWalletConfig()
wallet_config.path = "sample_wallet_full"
wallet_config.password = "supersecretpassword123"
wallet_config.network_type = MoneroNetworkType.STAGENET
wallet_config.server = MoneroRpcConnection()
wallet_config.server.username = "superuser"
wallet_config.server.password = "abctesting123"
wallet_config.seed = "hefty value scenic..."
wallet_config.restore_height = 573936
wallet_full: MoneroWallet = MoneroWalletFull.create_wallet(wallet_config)

# custom wallet listener implementation
listener: MoneroWalletListener = MyWalletListener()

# synchronize the wallet and receive progress notifications
wallet_full.sync(listener)

# synchronize in the background every 5 seconds
wallet_full.start_syncing(5000)

# receive notifications when funds are received, confirmed, and unlocked
wallet_full.add_listener(listener)

# connect to wallet RPC and open wallet
wallet_rpc: MoneroWallet = new MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
wallet_rpc.open_wallet("sample_wallet_rpc", "supersecretpassword123")
primary_address: str = wallet_rpc.get_primary_address() # 555zgduFhmKd2o8rPUz...
balance: int = wallet_rpc.get_balance() # 533648366742
txs: list[MoneroTxWallet] = wallet_rpc.get_txs() # get transactions containing transfers to/from the wallet

# send funds from RPC wallet to full wallet
tx_config = MoneroTxConfig()
tx_config.account_index = 0
tx_config.address = wallet_full.get_address(1, 0)
tx_config.amount = 250000000000 # send 0.25 XMR (denominated in atomic units)
tx_config.relay = False # create transaction and relay to the network if true

created_tx: MoneroTxWallet = wallet_rpc.create_tx(tx_config)
fee: int = created_tx.get_fee() # "Are you sure you want to send... ?"
wallet_rpc.relay_tx(created_tx) # relay the transaction

# save and close wallet
wallet_full.close(true)
```

## Building monero-python from source

### Linux and macOS

1. Install build dependencies:<br>
    ```bash
    # Ubuntu/Debian

    sudo apt install -y python3-all python3-pip python3-pybind11
    ```
    ```bash
    # Fedora/RedHat

    sudo dnf install -y python3-all python3-pip python3-pybind11
    ```
    
2. Clone the project repository: 
    ```bash
    git clone --recurse-submodules https://github.com/everoddandeven/monero-python.git
    ```
3. Build the monero-cpp submodule (located at `./external/monero-cpp`) as a native library by following [instructions](https://github.com/woodser/monero-cpp#using-monero-cpp-in-your-project) for your system.
4. Copy shared library `./external/monero-cpp/build/libmonero-cpp.so` to `/usr/lib`:
    ```
    sudo cp ./external/monero-cpp/build/libmonero-cpp.so /usr/lib/
    ```
5. Build monero-python to `./build/`:<br>
    ```bash
    cd monero-python
    mkdir -p build
    cd build
    cmake ..
    make
    ```
6. Or build and install monero-python with pip: `pip3 install . --break-system-packages`

### Linux Docker Build
1. Install [Docker](https://docs.docker.com/engine/install/)
2. Clone the repository
    ```sh
    git clone --recursive https://github.com/everoddandeven/monero-python.git
    ```
3. Prepare build environment
    ```sh
    cd monero-python
    docker build --tag monero-python:build-linux --build-arg THREADS=4 --file Dockerfile.linux .
    ```
4. (Optional) Specify build image
    ```sh
    cd monero-python
    docker build --tag monero-python:build-linux --build-arg BASE_IMAGE="ubuntu:22.04" --build-arg THREADS=4 --file Dockerfile.linux .
    ```

5. Build
    ```sh
    docker run --rm -it -v <MONERO_PYTHON_DIR_FULL_PATH>:/monero-python -w /monero-python monero-python:build-linux sh ./docker/build.sh
    ```

    * `MONERO_PYTHON_DIR_FULL_PATH` - full path to `monero-python` directory

6. Library build will be placed in `monero-python/build` directory

## Use RPC servers in your project:

1. Download and install [Monero CLI](https://web.getmonero.org/downloads/).
2. Start monerod, e.g.: `./monerod --stagenet` (or use a remote daemon).
3. Start monero-wallet-rpc, e.g.: `./monero-wallet-rpc --daemon-address http://localhost:38081 --stagenet --rpc-bind-port 38083 --rpc-login rpc_user:abc123 --wallet-dir ./`

> [!NOTE]
> On Windows, if you want to use native wallets instead of monero-wallet-rpc, or if you want to process binary data, first install MSYS2:
> 1. Install [MSYS2](https://www.msys2.org/).
> 2. Environment variables > System variables > Path > Edit > New > C:\msys64\mingw64\bin


## Memory Growth

If you see unrestricted memory growth using monero-python, consider applying [jemalloc](https://jemalloc.net/) to improve memory management with `malloc`. In many cases, this can completely resolve the memory growth.

For example: `export LD_PRELOAD=/path/to/libjemalloc.a` then run your app.

## Running Python tests

1. Install `pytest`:
    ```bash
    # With PIP

    pip3 install pytest pytest-rerunfailures --break-system-packages
    ```
    ```bash
    # System-wide installation Ubuntu/Debian

    sudo apt install -y python3-pytest python3-pytest-rerunfailures
    ```
    ```bash
    # System-wide installation Fedora/RedHat

    sudo dnf install -y python3-pytest python3-pytest-rerunfailures
    ```
2. Clone the project repository: 
    ```bash
    git clone --recurse-submodules https://github.com/everoddandeven/monero-python.git

    cd monero-python
    ```
3. Setup docker test environment
    ```bash
    docker compose -f tests/docker-compose.yml up -d node_1 node_2 xmr_wallet_1 xmr_wallet_2
    ```
4. Or start RPC servers locally:
	1. Download and install [Monero CLI](https://web.getmonero.org/downloads/).
	2. Start monerod, e.g.: `./monerod --stagenet` (or use a remote daemon).
	3. Start monero-wallet-rpc, e.g.: `./monero-wallet-rpc --daemon-address http://localhost:38081 --stagenet --rpc-bind-port 38083 --rpc-login rpc_user:abc123 --wallet-dir ./`
5. Configure the appropriate RPC endpoints, authentication, and other settings in [config.ini](tests/config/config.ini).
6. Run all python tests with:
    ```bash
    pytest
    ```


## Related projects

* [monero-cpp](https://github.com/woodser/monero-cpp)
* [monero-java](https://github.com/woodser/monero-cpp)
* [monero-ts](https://github.com/woodser/monero-ts)

## License

This project is licensed under MIT.

## Donations

If this library has been valuable to you, please consider donating to support its continued development. 🙏

<p align="center">
  <code>XMR</code><br>
	<img src="donate.png" style="margin-top: 5px" width="115" height="115"/><br>
	<code>84rXAu3QhsfbQ2vbxyoEptbRLZ2gtyL8k2qCeJwM5AU4FcxVDEbLRuxMZD5pXD1TR295Nodn7y9mkjoMemHrnMqa9ZnJTza</code>
</p>
