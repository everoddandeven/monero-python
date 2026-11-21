---
title: Full Wallet
---
# Full Wallet

A full wallet is `wallet2`, the wallet of monero, in the process: it keeps its files on disk, or in memory, and syncs with a daemon. It
implements almost every method of the interface ([Wallet Support](wallet_support.md)).

## Creating and opening

[`create_wallet`][monero.MoneroWalletFull.create_wallet] makes a new wallet from a [`MoneroWalletConfig`][monero.MoneroWalletConfig],
and how depends on what the config has:

| The config has | The wallet is |
| --- | --- |
| `seed` (and `seed_offset`, `restore_height`) | restored from the seed |
| `primary_address`, `private_view_key`, and `private_spend_key` or not | restored from the keys: without the spend key it is view-only |
| none of them | a new wallet, with a random seed; `restore_height` is not allowed, it syncs from the height of the daemon |

`network_type` is always needed. `path` is where the wallet is written, `server` the daemon that it syncs with:

```python
from monero import MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletFull

config = MoneroWalletConfig()
config.path = "wallets/main"
config.password = "supersecretpassword123"
config.network_type = MoneroNetworkType.STAGENET
config.server = MoneroRpcConnection("http://localhost:38081")
config.seed = "hefty value scenic..."
config.restore_height = 573936    # the height to sync from: without it a restored wallet syncs from the first block

wallet = MoneroWalletFull.create_wallet(config)
```

A wallet that is already on disk is opened with [`open_wallet`][monero.MoneroWalletFull.open_wallet], after checking it with
[`wallet_exists`][monero.MoneroWalletFull.wallet_exists]:

```python
from monero import MoneroNetworkType, MoneroWalletFull

if MoneroWalletFull.wallet_exists("wallets/main"):
    wallet = MoneroWalletFull.open_wallet("wallets/main", "supersecretpassword123", MoneroNetworkType.STAGENET)
```

## Its files

A wallet with a `path` is two files: `<path>.keys`, its keys encrypted with the password, and `<path>`, the cache of what it synced.
Without the cache a wallet syncs again, without the keys it is lost: back up the seed.

A wallet without a `path` is only in memory. [`get_keys_file_buffer`][monero.MoneroWalletFull.get_keys_file_buffer] and
[`get_cache_file_buffer`][monero.MoneroWalletFull.get_cache_file_buffer] give the content of its two files, and
[`open_wallet_data`][monero.MoneroWalletFull.open_wallet_data] opens a wallet from them: an application can keep them where it wants.

## Syncing

A wallet knows its outputs and its transactions up to the height that it synced, [`get_height`][monero.MoneroWallet.get_height]:

- [`sync`][monero.MoneroWallet.sync] syncs up to the height of the daemon, and returns when it is done; a listener given to it gets the
  progress.
- [`start_syncing`][monero.MoneroWallet.start_syncing] syncs in the background, on a thread of its own, every 10 seconds or the period
  given; [`stop_syncing`][monero.MoneroWallet.stop_syncing] stops it. The
  [listeners][monero.MoneroWalletListener] of the wallet get what it finds.

A sync from far away takes long: the `restore_height` of a restored wallet saves the blocks before it.

## Saving and closing

[`save`][monero.MoneroWallet.save] writes the files, [`close`][monero.MoneroWallet.close] stops the sync and closes the wallet, and with
`close(True)` saves it first. A wallet closed without saving loses what it synced since its last save, and syncs it again when it is
opened.

::: monero.MoneroWalletFull
