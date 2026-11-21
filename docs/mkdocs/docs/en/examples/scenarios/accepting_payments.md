---
title: Accepting Payments in a Shop
---
# Accepting Payments in a Shop

A shop gives each order an address of its own, a subaddress of its wallet: a payment to that address is the payment of that order,
without asking the customer for a reference. It shows the address as a payment URI, which a wallet reads from a QR code, watches it with a
listener, and ships the order once the payment has the confirmations that the shop waits for.

The wallet of the shop can be a view-only one ([Glossary](../../api/glossary.md#keys-and-addresses)): it sees the payments, and the spend key stays
elsewhere ([Signing Offline with a Cold Wallet](cold_signing.md)).

## An order

```python
from dataclasses import dataclass

from monero import MoneroSubaddress, MoneroTxConfig, MoneroUtils, MoneroWallet

ACCOUNT = 0     # the account of the wallet that receives the payments


@dataclass
class Order:
    id: str
    amount: int             # atomic units
    subaddress_index: int
    address: str


def new_order(wallet: MoneroWallet, order_id: str, price_xmr: float) -> tuple[Order, str]:
    """A new order, with its subaddress, and the payment URI to show as a QR code."""
    subaddress: MoneroSubaddress = wallet.create_subaddress(ACCOUNT, f"order {order_id}")
    assert subaddress.index is not None and subaddress.address is not None
    order = Order(order_id, MoneroUtils.xmr_to_atomic_units(price_xmr), subaddress.index, subaddress.address)

    # monero:<address>?tx_amount=...&recipient_name=...&tx_description=...
    request = MoneroTxConfig()
    request.address = order.address
    request.amount = order.amount
    request.recipient_name = "The Shop"
    request.note = f"order {order_id}"
    return order, wallet.get_payment_uri(request)
```

The label of the subaddress is the order: [`get_subaddresses`][monero.MoneroWallet.get_subaddresses] shows it later, in the wallet.

## Seeing the payment

A listener hears of an output to one of the subaddresses as soon as its transaction reaches the pool, before it is in a block. It is the
moment to tell the customer that the payment is seen, not yet to ship:

```python
import threading

from monero import MoneroOutputWallet, MoneroWalletListener


class Payments(MoneroWalletListener):

    def __init__(self, orders: dict[int, Order]) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self._orders = orders           # by the index of their subaddress

    def on_output_received(self, output: MoneroOutputWallet) -> None:
        if output.account_index != ACCOUNT or output.subaddress_index is None:
            return
        with self._lock:
            order = self._orders.get(output.subaddress_index)
        if order is not None:
            confirmed = "confirmed" if output.tx.is_confirmed else "in the pool"
            print(f"order {order.id}: {output.amount} received, {confirmed}")
```

## Is it paid?

The listener tells what happens, the wallet tells the state: what an order received is the sum of the incoming transfers to its
subaddress, and each counts once it has the confirmations that the shop waits for.

```python
from monero import MoneroIncomingTransfer, MoneroTransferQuery, MoneroWallet

CONFIRMATIONS = 10      # the outputs of a payment can be spent after 10 blocks


def amount_paid(wallet: MoneroWallet, order: Order) -> tuple[int, int]:
    """What the order received: the confirmed amount, and the one that waits for its confirmations."""
    query = MoneroTransferQuery()
    query.account_index = ACCOUNT
    query.subaddress_index = order.subaddress_index
    transfers: list[MoneroIncomingTransfer] = wallet.get_incoming_transfers(query)

    confirmed = pending = 0
    for transfer in transfers:
        if (transfer.tx.num_confirmations or 0) >= CONFIRMATIONS:
            confirmed += transfer.amount or 0
        else:
            pending += transfer.amount or 0
    return confirmed, pending


def is_paid(wallet: MoneroWallet, order: Order) -> bool:
    confirmed, _ = amount_paid(wallet, order)
    return confirmed >= order.amount
```

How many confirmations to wait is the choice of the shop: none for a coffee, where a double spend costs little, more for what is
expensive. [`num_suggested_confirmations`][monero.MoneroIncomingTransfer.num_suggested_confirmations] of a transfer is the number that the wallet suggests for its
amount. A customer may pay in more transactions, or pay less: the sum of the transfers handles both.

## Putting it together

```python
from monero import MoneroNetworkType, MoneroWalletFull

wallet = MoneroWalletFull.open_wallet("wallets/shop", "supersecretpassword123", MoneroNetworkType.STAGENET)

orders: dict[int, Order] = {}
order, uri = new_order(wallet, "1234", 0.05)
orders[order.subaddress_index] = order
print(f"pay {uri}")

wallet.add_listener(Payments(orders))
wallet.start_syncing(5000)

# later, for each order that waits: ship it once it is paid
if is_paid(wallet, order):
    print(f"order {order.id} paid: ship it")
```

The orders, with their subaddress index, belong in the database of the shop: the wallet keeps the subaddresses and their labels, not
the orders.
