---
title: Using Keys-Only Wallet
---
# Using Keys-Only Wallet

`MoneroWalletKeys` is a `MoneroWallet` implementation that has the keys of a wallet alone, in memory, without files or RPC calls: it
works offline. [Keys-Only Wallet](../api/wallet_keys.md) says what it can do.

## Creating

A new wallet, with a random seed:

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.TESTNET
config.language = "English"                 # the language of the words of the seed

wallet = MoneroWalletKeys.create_wallet_random(config)
print(wallet.get_seed())
```

The same wallet, restored from its seed:

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.TESTNET
config.seed = "...wallet seed..."

wallet = MoneroWalletKeys.create_wallet_from_seed(config)
```

Or from its keys: with the view key and no spend key it is a view-only wallet:

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.TESTNET
config.primary_address = "...wallet primary address..."
config.private_view_key = "...wallet private view key..."

wallet = MoneroWalletKeys.create_wallet_from_keys(config)
print(wallet.is_view_only())                # True
```

## Keys and addresses

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.TESTNET
wallet = MoneroWalletKeys.create_wallet_random(config)

print(wallet.get_primary_address())
print(wallet.get_private_view_key(), wallet.get_public_view_key())
print(wallet.get_private_spend_key(), wallet.get_public_spend_key())

# the subaddresses of the first account
for index in range(1, 4):
    print(wallet.get_address(0, index))

# an address with a payment ID, and back
integrated = wallet.get_integrated_address()
print(integrated.integrated_address, integrated.payment_id)
decoded = wallet.decode_integrated_address(integrated.integrated_address)
print(decoded.standard_address == wallet.get_primary_address())
```

A view-only wallet made from these keys, by a [full wallet](../api/wallet_full.md) on a machine that is online, sees the payments to
the wallet without being able to spend them. A keys-only wallet also signs and checks messages:
[Proofs and Signatures](proofs_and_signatures.md).
