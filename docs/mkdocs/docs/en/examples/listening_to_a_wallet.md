---
title: Listening to a Wallet
---
# Listening to a Wallet

A listener is told what a wallet finds while it syncs: the progress, the new blocks, the outputs received and spent, the changes of the
balance. It is a subclass of [`MoneroWalletListener`][monero.MoneroWalletListener] that overrides the methods it needs.

## The progress of a sync

A listener given to [`sync`][monero.MoneroWallet.sync] gets the progress of that sync:

```python
from monero import MoneroNetworkType, MoneroWalletFull, MoneroWalletListener


class SyncProgress(MoneroWalletListener):

    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        print(f"{percent_done * 100:.1f}%  ({height} of {end_height})")


wallet = MoneroWalletFull.open_wallet("wallets/main", "supersecretpassword123", MoneroNetworkType.STAGENET)
result = wallet.sync(SyncProgress())
print(f"{result.num_blocks_fetched} blocks, money received: {result.received_money}")
```

## Payments received

A listener added with [`add_listener`][monero.MoneroWallet.add_listener] stays until
[`remove_listener`][monero.MoneroWallet.remove_listener], and gets what every sync finds, the ones of
[`start_syncing`][monero.MoneroWallet.start_syncing] in the background too:

```python
import threading

from monero import MoneroNetworkType, MoneroOutputWallet, MoneroUtils, MoneroWalletFull, MoneroWalletListener


class Payments(MoneroWalletListener):

    def __init__(self) -> None:
        super().__init__()
        # the wallet calls it from the thread that syncs it, not from the one that added it
        self._lock = threading.Lock()
        self.received: list[MoneroOutputWallet] = []

    def on_output_received(self, output: MoneroOutputWallet) -> None:
        with self._lock:
            self.received.append(output)
        amount = MoneroUtils.atomic_units_to_xmr(output.amount or 0)
        print(f"received {amount} XMR in {output.tx.hash}, to the subaddress {output.account_index}/{output.subaddress_index}")

    def on_balances_changed(self, new_balance: int, new_unlocked_balance: int) -> None:
        print(f"balance {new_balance}, unlocked {new_unlocked_balance}")


wallet = MoneroWalletFull.open_wallet("wallets/main", "supersecretpassword123", MoneroNetworkType.STAGENET)
payments = Payments()
wallet.add_listener(payments)
wallet.start_syncing(5000)     # every 5 seconds

# ... the application runs ...

wallet.remove_listener(payments)
wallet.close(True)
```

An output is reported when its transaction is seen, in the pool or in a block: `output.tx.is_confirmed` says which, and an output can be
spent only once it is unlocked ([Glossary](../api/glossary.md#transactions)).

## The listeners and the threads

- The methods of a listener run on the thread that syncs the wallet: the one of `start_syncing`, or for an
  [RPC wallet](../api/wallet_rpc.md) the one that polls the server. What they share with the rest of the application needs a lock, as
  above.
- They hold that thread while they run: a slow listener delays the sync. Hand long work to a queue, and return.
- An exception raised in a listener does not reach the code that started the sync: catch it in the listener.

## A daemon

A [`MoneroDaemonListener`][monero.MoneroDaemonListener] added to a daemon is told of each new block:

```python
from monero import MoneroBlockHeader, MoneroDaemonListener, MoneroDaemonRpc


class NewBlocks(MoneroDaemonListener):

    def on_block_header(self, header: MoneroBlockHeader) -> None:
        print(f"block {header.height}: {header.hash}")


daemon = MoneroDaemonRpc("http://localhost:38081")
daemon.add_listener(NewBlocks())
```
