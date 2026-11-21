---
title: Interact with RPC Wallet
---
# Interact with RPC Wallet

`MoneroWalletRpc` offers a `MoneroWallet` implementation that talks to a [`monero-wallet-rpc`](https://docs.getmonero.org/rpc-library/wallet-rpc/){ target="_blank" rel="noopener" } through
its JSON-RPC interface. [RPC Wallet](../../api/wallet_rpc.md) explains how to start the server.

Creating a `MoneroWalletRpc` instance is very simple:

```python
from monero import MoneroWalletRpc

# create RPC wallet connected to `monero-wallet-rpc` server
wallet = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")    # the --rpc-login of the server
```

It can also be done using a `MoneroRpcConnection` instance:

```python
from monero import MoneroRpcConnection, MoneroWalletRpc

# create rpc connection
connection = MoneroRpcConnection("http://localhost:38083", "rpc_user", "abc123")

# create wallet using RPC connection
wallet = MoneroWalletRpc(connection)
```

A new wallet, in the `--wallet-dir` of the server:

```python
from monero import MoneroWalletConfig

# build wallet configuration
config = MoneroWalletConfig()
config.path = "wallet_name"         # the name of its file, in the folder of the server
config.password = "wallet_password"

# create new wallet file in rpc server
wallet.create_wallet(config)
```

Or a wallet that is already there: opening one closes the wallet that was open.

```python
# open wallet with config
wallet.open_wallet(config)

# or open by path and password
wallet.open_wallet("wallet_name", "wallet_password")
```

Then the wallet answers as any other:

```python
# get wallet information
primary_address: str = wallet.get_primary_address()
view_key: str = wallet.get_private_view_key()
seed: str = wallet.get_seed()
balance: int = wallet.get_balance()

print(f"primary address: {primary_address}")
print(f"view_key: {view_key}")
print(f"seed: {seed}")
print(f"balance: {balance}")
```
