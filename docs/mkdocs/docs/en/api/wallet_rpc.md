---
title: RPC Wallet
---
# RPC Wallet

An RPC wallet is a client of `monero-wallet-rpc`, the wallet server of monero: the wallet runs in the server, which keeps its files and
syncs it with a daemon, and the client sends it the calls over HTTP(S). A server has one wallet open at a time.

## The server

`monero-wallet-rpc` comes with monero. It is started with the folder of its wallets, the daemon that they sync with, and the credentials
of its RPC:

```bash
monero-wallet-rpc --stagenet \
    --rpc-bind-port 38083 \
    --rpc-login rpc_user:abc123 \
    --wallet-dir ./wallets \
    --daemon-address localhost:38081
```

`--disable-rpc-login` instead of `--rpc-login` lets anyone that reaches the port use the wallet: only on a server that nobody else
reaches. The [network of the tests](../tests/environment/network.md) runs three of them, in docker.

## Connecting, opening and creating

The client connects to the server, and opens a wallet of its `--wallet-dir` by name, or creates one there:

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletRpc

wallet = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")

# a wallet that is in the folder of the server
wallet.open_wallet("main", "supersecretpassword123")

# or a new one, there: the config is the one of a full wallet, its path is the name of the wallet in the folder
config = MoneroWalletConfig()
config.path = "other"
config.password = "supersecretpassword123"
config.network_type = MoneroNetworkType.STAGENET
wallet.create_wallet(config)
```

Opening a wallet closes the one that was open. [`close`][monero.MoneroWallet.close] closes the wallet in the server,
[`stop`][monero.MoneroWalletRpc.stop] stops the server.

## What it does differently

- The server syncs its wallet on its own. [`sync`][monero.MoneroWallet.sync] asks it for a sync now, without a listener of progress
  ([Wallet Support](wallet_support.md)).
- The client learns of new blocks, outputs and balances by polling the server: its listeners are called from a thread that polls every
  [`set_poll_period_in_ms`][monero.MoneroWalletRpc.set_poll_period_in_ms].
- What the server can not do through its RPC, the client can not either: the network type of the wallet, moving its files
  ([Wallet Support](wallet_support.md)).

::: monero.MoneroWalletRpc
