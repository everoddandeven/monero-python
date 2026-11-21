---
title: Keys-Only Wallet
---
# Keys-Only Wallet

A keys-only wallet is the keys of a wallet, in memory, with no file and no daemon: it works offline. It makes a seed, the keys and the
addresses, and signs and checks messages, but it knows nothing of the chain: no balance, no transaction, no sync
([Wallet Support](wallet_support.md)).

It is for what needs the keys alone: making a wallet on a machine that is never online, deriving the addresses of a wallet, checking a
seed.

## Creating

Each way of making it has its own function, which takes a [`MoneroWalletConfig`][monero.MoneroWalletConfig] with its `network_type`:

| Function | From |
| --- | --- |
| [`create_wallet_random`][monero.MoneroWalletKeys.create_wallet_random] | nothing: a new seed, in `language` |
| [`create_wallet_from_seed`][monero.MoneroWalletKeys.create_wallet_from_seed] | `seed`, and `seed_offset` |
| [`create_wallet_from_keys`][monero.MoneroWalletKeys.create_wallet_from_keys] | `primary_address`, `private_view_key`, and `private_spend_key` or not: without the spend key it is view-only |

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.MAINNET
wallet = MoneroWalletKeys.create_wallet_random(config)

print(wallet.get_seed())
print(wallet.get_primary_address())
print(wallet.get_address(0, 1))     # the first subaddress of the first account
```

The seed and the keys are the ones that a [full wallet](wallet_full.md) or an [RPC wallet](wallet_rpc.md) is restored from, to use the
wallet on the chain.

::: monero.MoneroWalletKeys
