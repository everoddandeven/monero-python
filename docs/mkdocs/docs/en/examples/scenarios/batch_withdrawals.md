---
title: Batch Withdrawals
---
# Batch Withdrawals

A service that pays many users, an exchange with its withdrawals or a pool with its miners, does not send a transaction for each: it
pays them together, many destinations in one transaction. That is fewer fees, one for many payments, and fewer outputs of its own to
wait for, since a transaction locks the change for 10 blocks.

A transaction of Monero has at most 16 outputs, and one of them is the change: 15 destinations at most. A batch of more is split.

## The withdrawals waiting

```python
from dataclasses import dataclass

from monero import MoneroDestination, MoneroUtils


@dataclass
class Withdrawal:
    id: int
    address: str
    amount: int     # atomic units


pending = [
    Withdrawal(1, "...", MoneroUtils.xmr_to_atomic_units(0.5)),
    Withdrawal(2, "...", MoneroUtils.xmr_to_atomic_units(1.2)),
    # ... the ones that the users asked for since the last batch
]

MAX_DESTINATIONS = 15   # 16 outputs, one of them the change
batches = [pending[i:i + MAX_DESTINATIONS] for i in range(0, len(pending), MAX_DESTINATIONS)]
```

Before a withdrawal joins a batch, the service checks its address: one that is not valid fails the whole transaction.

```python
from monero import MoneroNetworkType, MoneroUtils

valid = [w for w in pending if MoneroUtils.is_valid_address(w.address, MoneroNetworkType.MAINNET)]
```

## The fee

The daemon estimates the fee by priority. A withdrawal can wait some minutes: the lowest priority that gets into the next blocks is
enough, and a service that sends many transactions saves on it.

```python
from monero import MoneroDaemonRpc

daemon = MoneroDaemonRpc("http://localhost:18081")
estimate = daemon.get_fee_estimate()
print(f"fee per byte: {estimate.fee}, by priority: {estimate.fees}")
```

## Paying a batch

```python
from monero import MoneroTxConfig, MoneroTxPriority, MoneroWalletRpc

wallet = MoneroWalletRpc("http://localhost:18083", "rpc_user", "abc123")
wallet.open_wallet("hot", "supersecretpassword123")


def pay(batch: list[Withdrawal]) -> list[str]:
    """Pays a batch in one transaction, and returns its hash."""
    config = MoneroTxConfig()
    config.account_index = 0
    config.destinations = [MoneroDestination(w.address, w.amount) for w in batch]
    config.priority = MoneroTxPriority.UNIMPORTANT
    config.relay = True
    tx = wallet.create_tx(config)
    assert tx.hash is not None

    # what the transaction paid, in the wallet: the ids of the withdrawals
    wallet.set_tx_note(tx.hash, "withdrawals " + ",".join(str(w.id) for w in batch))
    return [tx.hash]


for batch in batches:
    tx_hashes = pay(batch)
    # mark the withdrawals of the batch as sent, with tx_hashes, in the database of the service
```

A batch is all or nothing: the transaction pays every destination, or it is not created. An error leaves every withdrawal of the batch
waiting, and none paid twice.

## Before the next batch

The change of a transaction is locked for 10 blocks: a wallet that sends a batch every few minutes runs out of unlocked funds while its
balance is fine. A service keeps its funds in several outputs, so that some are unlocked while others wait: a
[`sweep_unlocked`][monero.MoneroWallet.sweep_unlocked] with `sweep_each_subaddress` or several payments to its own subaddresses splits
them.

```python
balance, unlocked = wallet.get_balance(0), wallet.get_unlocked_balance(0)
needed = sum(w.amount for w in pending)
if unlocked < needed:
    print(f"wait: {unlocked} unlocked of {balance}, the batch needs {needed}")
```
