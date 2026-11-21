---
title: Backup and Recovery
---
# Backup and Recovery

A wallet is its keys. The files of a [full wallet](../../api/wallet_full.md) can be lost, copied, corrupted: what matters is that the
keys can be made again, and that the wallet finds its money again on the chain.

## What to keep

| What | For | Where |
| --- | --- | --- |
| the **seed**, 25 words, and its `seed_offset` if it has one | the keys: everything else is made from it | written on paper, not on a machine that is online |
| the **restore height**, or the date of the first payment | where to start looking on the chain: without it, the first block | next to the seed |
| the files of the wallet, `<path>` and `<path>.keys`, with the password | a faster restore: the keys, and the cache of what it synced | a backup of the machine |
| the notes and the address book | what the chain does not have: what each payment was for | in the cache file, or exported by the application |

The seed and the restore height are enough to get the money back. The files save time, and keep what only the wallet knew.

```python
from monero import MoneroNetworkType, MoneroWalletFull

wallet = MoneroWalletFull.open_wallet("wallets/main", "supersecretpassword123", MoneroNetworkType.MAINNET)
print("seed:", wallet.get_seed())
print("seed language:", wallet.get_seed_language())
print("restore height:", wallet.get_restore_height())
```

## Restoring from the seed

The restored wallet is the same wallet, with new files. It looks for its outputs from the restore height: one that is too high misses the
payments before it, one that is too low only takes longer.

```python
from monero import MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletFull

config = MoneroWalletConfig()
config.path = "wallets/restored"
config.password = "a new password"
config.network_type = MoneroNetworkType.MAINNET
config.server = MoneroRpcConnection("http://localhost:18081")
config.seed = "...the 25 words..."
config.restore_height = 3200000
wallet = MoneroWalletFull.create_wallet(config)
```

When the height is not known but the date is, [`get_height_by_date`][monero.MoneroWallet.get_height_by_date] gives a height a little
before that date, and the wallet starts from there before its first sync:

```python
wallet.set_restore_height(wallet.get_height_by_date(2025, 3, 1))     # a day before the first payment
result = wallet.sync()
print(f"{result.num_blocks_fetched} blocks, balance {wallet.get_balance()}")
```

## When the wallet is wrong

A wallet that was restored, moved or interrupted can show a wrong balance. Each case has its call:

| What is wrong | Why | The call |
| --- | --- | --- |
| a payment that the explorer shows is missing | the restore height was after it, or a block was missed | [`scan_txs`][monero.MoneroWallet.scan_txs] with its hash, or a restore from an earlier height |
| outputs show as unspent, and the wallet can not spend them | the wallet missed that they were spent, as after a restore from the keys, with another wallet that spent them | [`rescan_spent`][monero.MoneroWallet.rescan_spent], which needs a [trusted daemon](../../api/glossary.md#transactions) |
| the cache seems corrupted | the files were damaged | [`rescan_blockchain`][monero.MoneroWallet.rescan_blockchain]: it forgets what it synced, and syncs again from the restore height |

```python
wallet.scan_txs(["..."])            # the hash of the payment that is missing
wallet.rescan_spent()               # ask the daemon which outputs are spent
```

`rescan_blockchain` forgets what the wallet knew of its outgoing payments and that the chain does not have, such as their destinations:
the wallet finds the payments again, not to whom they went. The notes stay.

## Checking a backup

A backup that was never tried is a hope. The seed is checked without touching the wallet: a [keys-only wallet](../../api/wallet_keys.md)
made from it, offline, has the same primary address.

```python
from monero import MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.MAINNET
config.seed = "...the 25 words, as written in the backup..."
check = MoneroWalletKeys.create_wallet_from_seed(config)
assert check.get_primary_address() == wallet.get_primary_address(), "the seed of the backup is not the one of the wallet"
```
