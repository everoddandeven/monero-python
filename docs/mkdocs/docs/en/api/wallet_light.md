---
title: Light Wallet
---
# Light Wallet

A light wallet is a client of [`monero-lws`](https://github.com/vtnerd/monero-lws), the light wallet server: the server scans the chain
for the wallet, which does not download blocks. The wallet keeps the keys in memory, builds and signs its transactions, and sends them
through the server.

!!! warning "The server learns the private view key"

    The wallet gives the server its primary address and its private view key: the server sees what the wallet receives. The spend key
    stays in the wallet, so the server can not spend the funds. Use a server that you run, or one that you trust with that.

## Creating and opening

The server is a [`MoneroRpcConnection`][monero.MoneroRpcConnection], given when the wallet is made:

```python
from monero import MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletLight

server = MoneroRpcConnection("http://localhost:8443")

# a new wallet, whose account is registered on the server
config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.STAGENET
wallet = MoneroWalletLight.create_wallet(config, server)
seed = wallet.get_seed()
wallet.close()

# the same wallet later, from its seed
config.seed = seed
wallet = MoneroWalletLight.open_wallet(config, server)

wallet.sync()                   # fetch what the server has scanned
wallet.start_syncing(5000)      # and keep fetching it, every 5 seconds
print(wallet.get_balance())
wallet.close()
```

A light wallet has no file: it is opened from its `seed`, or from its `primary_address` and `private_view_key`, with the
`private_spend_key` or without it, which makes it view-only. [`create_wallet`][monero.MoneroWalletLight.create_wallet] fails when the
server already has the account, [`wallet_exists`][monero.MoneroWalletLight.wallet_exists] tells whether it has it.

A server may wait for its administrator to accept a new account before it scans it.

## Accounts, subaddresses and restore height

- The server reports the transactions of the accounts and subaddresses that are registered on it.
  [`create_account`][monero.MoneroWallet.create_account] and [`create_subaddress`][monero.MoneroWallet.create_subaddress] register them,
  without a label. To restore a wallet that already used more of them, set `account_lookahead` and `subaddress_lookahead` in the config,
  both together.
- `restore_height` asks the server to scan the account again from that height. A server may ask for a payment to do it: the wallet then
  raises an error with the address and the amount.

## What it does differently

- The server does not report the transactions of the pool: the wallet sees a transaction that it receives after its first confirmation.
  It reports the ones that it sends as unconfirmed on its own, and forgets them when it is closed.
- It does not keep the payment id of the transactions that it creates.
- Its listeners are called after a sync, with what the server has scanned since the one before.
- Nothing is saved: [`close`][monero.MoneroWallet.close] refuses `save=True`.
- No attributes, labels, account tags, notes or address book, no transaction, spend or reserve proofs, no multisig and no mining
  ([Wallet Support](wallet_support.md)).

::: monero.MoneroWalletLight
