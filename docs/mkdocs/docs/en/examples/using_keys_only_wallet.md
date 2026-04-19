---
title: Using Keys-Only Wallet
---
# Using Keys-Only Wallet

`MoneroWalletKeys` is a `MoneroWallet` implementation that supports only basic keys operations, without files or RPC calls.

Creating a in-memory keys-only wallet with `MoneroWalletKeys` is very simple:

```python
from monero import MoneroWalletKeys, MoneroWalletConfig, MoneroNetworkType

# setup wallet configuration
config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.TESTNET

# create random wallet
wallet = MoneroWalletKeys.create_wallet_random(config)
```

Restore specific wallet from seed:

```python
config.seed = "...wallet seed..."

# restore wallet from seed
wallet = MoneroWalletKeys.create_wallet_from_seed(config)
```

Or from wallet keys:

```python
config.primary_address = "...wallet primary address..."
config.private_view_key = "...wallet private view key..."

# restore wallet from keys
wallet = MoneroWalletKeys.create_wallet_from_keys(config)
```