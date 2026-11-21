---
title: Create Local Full Wallet
---
# Create Local Full Wallet

`MoneroWalletFull` is the `MoneroWallet` implementation that wraps the [wallet2 API](https://github.com/monero-project/monero/blob/master/src/wallet/wallet2.h){ target="_blank" rel="noopener" }
of monero in the process: it creates and opens wallet files, and syncs them with a daemon. [Full Wallet](../../api/wallet_full.md) explains
how it works.

## A new wallet

```python
from monero import MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletFull

config = MoneroWalletConfig()
config.path = "test_wallet_full"                    # test_wallet_full and test_wallet_full.keys
config.password = "supersecretpassword123"
config.network_type = MoneroNetworkType.TESTNET
config.server = MoneroRpcConnection("http://localhost:28081")

wallet = MoneroWalletFull.create_wallet(config)
print(wallet.get_seed())                            # write it down: it is the wallet
```

## A wallet restored from its seed

```python
from monero import MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletFull

config = MoneroWalletConfig()
config.path = "restored_wallet"
config.password = "supersecretpassword123"
config.network_type = MoneroNetworkType.TESTNET
config.server = MoneroRpcConnection("http://localhost:28081")
config.seed = "...the 25 words..."
config.restore_height = 2500000                     # a height before the first payment to the wallet

wallet = MoneroWalletFull.create_wallet(config)
wallet.sync()
print(wallet.get_balance(), wallet.get_unlocked_balance())
```

Without `restore_height` the wallet syncs from the first block, which takes long. [`get_height_by_date`][monero.MoneroWallet.get_height_by_date]
gives the height of a date, when the date of the wallet is known better than its height.

## Opening, syncing and closing

```python
from monero import MoneroNetworkType, MoneroWalletFull

if MoneroWalletFull.wallet_exists("test_wallet_full"):
    wallet = MoneroWalletFull.open_wallet("test_wallet_full", "supersecretpassword123", MoneroNetworkType.TESTNET)

    # sync in the background, every 10 seconds, while the application runs
    wallet.start_syncing()

    # ... the application uses the wallet ...

    # stop the sync, save what it synced, and close the wallet
    wallet.close(True)
```

[Listening to a Wallet](listening_to_a_wallet.md) has how to follow what the sync finds.

## A wallet in memory

A wallet with no `path` is not written to disk: its data are taken with
[`get_keys_file_buffer`][monero.MoneroWalletFull.get_keys_file_buffer] and
[`get_cache_file_buffer`][monero.MoneroWalletFull.get_cache_file_buffer], kept where the application wants, and opened again with
[`open_wallet_data`][monero.MoneroWalletFull.open_wallet_data]:

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletFull

config = MoneroWalletConfig()
config.password = "supersecretpassword123"
config.network_type = MoneroNetworkType.TESTNET
wallet = MoneroWalletFull.create_wallet(config)

keys_data: bytes = wallet.get_keys_file_buffer("supersecretpassword123", False)
cache_data: bytes = wallet.get_cache_file_buffer()
wallet.close()

wallet = MoneroWalletFull.open_wallet_data("supersecretpassword123", MoneroNetworkType.TESTNET, keys_data, cache_data)
```
