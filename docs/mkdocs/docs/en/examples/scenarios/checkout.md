---
title: Checking Out as a Customer
---
# Checking Out as a Customer

The other side of [Accepting Payments in a Shop](accepting_payments.md): the wallet of a customer reads the payment request of the
shop, shows what the payment will cost, and sends it only once the customer agrees. It is what any wallet does between scanning a QR
code and "Sent".

## Reading the request

A payment request is a URI, `monero:<address>?tx_amount=...&recipient_name=...&tx_description=...`, often shown as a QR code.
[`parse_payment_uri`][monero.MoneroWallet.parse_payment_uri] turns it into the [`MoneroTxConfig`][monero.MoneroTxConfig] of the payment:

```python
from monero import MoneroNetworkType, MoneroUtils, MoneroWalletFull

wallet = MoneroWalletFull.open_wallet("wallets/customer", "supersecretpassword123", MoneroNetworkType.STAGENET)
wallet.sync()

uri = "monero:...?tx_amount=0.05&recipient_name=The%20Shop&tx_description=order%201234"
request = wallet.parse_payment_uri(uri)
assert request.address is not None and request.amount is not None

print(f"pay {MoneroUtils.atomic_units_to_xmr(request.amount)} XMR to {request.recipient_name}: {request.note}")
MoneroUtils.validate_address(request.address, MoneroNetworkType.STAGENET)     # raises if it is not an address of this network
```

The address is checked against the network of the wallet: a request of mainnet in a wallet of stagenet, or the other way round, is a
mistake to stop here.

## Creating it, without sending it

With `relay = False` the wallet creates and signs the transaction, and keeps it: nothing reaches the network yet. Its fee is known:

```python
from monero import MoneroTxPriority

request.account_index = 0
request.priority = MoneroTxPriority.NORMAL
request.relay = False
tx = wallet.create_tx(request)

fee = tx.fee or 0
unlocked = wallet.get_unlocked_balance(0)
print(f"amount {request.amount}, fee {fee}, left {unlocked - request.amount - fee}")
```

A balance that is not enough raises an error here, before anything is sent: an application shows it to the customer as "not enough
unlocked funds", with the [locked](../../api/glossary.md#when-an-output-can-be-spent) part of the balance, which is not spendable yet.

## Sending it, or not

```python
if input("Send? [y/N] ").lower() == "y":
    tx_hash = wallet.relay_tx(tx)
    wallet.set_tx_note(tx_hash, f"{request.recipient_name}: {request.note}")
    print(f"sent: {tx_hash}")
# otherwise nothing happens: the transaction was never relayed, and its outputs are free again
```

The note is the record of the customer: [`get_tx_note`][monero.MoneroWallet.get_tx_note] shows later what the payment was for, and the
hash is what proves it, if the shop says it did not arrive ([Proving a Payment in a Dispute](payment_dispute.md)).
