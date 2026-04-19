---
title: Interact with RPC Wallet
---
# Interact with RPC Wallet

`MoneroWalletRpc` offers a `MoneroWallet` implementation that interacts with [monero-wallet-rpc](https://docs.getmonero.org/rpc-library/wallet-rpc/) using calls to the `JSON-RPC` interface.


Creating a `MoneroWalletRpc` instance is very simple:

```python
from monero import MoneroWalletRpc

# create RPC wallet connected to `monero-wallet-rpc` server
wallet = MoneroWalletRpc("http://wallet_rpc_uri:18081")
```

It can also be done using a `MoneroRpcConnection` instance:

```python
from monero import MoneroRpcConnection, MoneroWalletRpc

# create rpc connection
connection = MoneroRpcConnection("http://wallet_rpc_uri:18081")

# create wallet using RPC connection
wallet = MoneroWalletRpc(connection)
```

Let's create a new wallet file:

```python
# build wallet configuration
config: MoneroWalletConfig = ...

# create new wallet file in rpc server
wallet.create_wallet(config)
```

Or open an already existing wallet:

```python
# open wallet with config
wallet.open_wallet(config)

# or open by path and password
wallet.open_wallet("wallet_path", "wallet_password")
```

And fetch some info:

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
