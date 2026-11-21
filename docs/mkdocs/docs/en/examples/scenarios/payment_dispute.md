---
title: Proving a Payment in a Dispute
---
# Proving a Payment in a Dispute

A customer paid order 1234, and the shop says that the money never arrived. The chain does not show who paid whom: the customer has to
prove it, to the shop or to whoever settles the dispute, and without giving away a key that shows more than this payment.

A **transaction proof** does it: the customer's wallet signs, with the transaction, the address that it paid and a message, the proof
that the transaction sent that address an amount. Anyone with a wallet synced with a daemon checks it, and sees the amount and the
confirmations.

## The customer: making the proof

The customer has the hash of the transaction, in the wallet that sent it, and the address of the order:

```python
from monero import MoneroWalletRpc

customer = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
shop_address = "..."            # the address that the shop gave for the order

# the payment to that address, among the outgoing transfers of the wallet: their destinations are known to the wallet that sent them
paid = [
    transfer for transfer in customer.get_outgoing_transfers()
    if any(destination.address == shop_address for destination in transfer.destinations)
]
tx_hash = paid[0].tx.hash
assert tx_hash is not None

# the message ties the proof to the dispute: the same proof does not serve another
message = "payment of order 1234"
signature: str = customer.get_tx_proof(tx_hash, shop_address, message)
# send tx_hash, shop_address, message and signature to the shop, or to the arbiter
```

## The shop, or the arbiter: checking it

```python
from monero import MoneroCheckTx, MoneroUtils, MoneroWalletRpc

checker = MoneroWalletRpc("http://localhost:38084", "rpc_user", "abc123")
check: MoneroCheckTx = checker.check_tx_proof(tx_hash, shop_address, message, signature)

if not check.is_good:
    print("the proof is not valid: this transaction did not pay this address")
elif check.in_tx_pool:
    print("paid, but the transaction is still in the pool")
else:
    amount = MoneroUtils.atomic_units_to_xmr(check.received_amount or 0)
    print(f"paid {amount} XMR, {check.num_confirmations} confirmations")
```

A proof that is good with an amount less than the price is a payment of less than the price: the dispute is about something else.

## Why not the key of the transaction

[`get_tx_key`][monero.MoneroWallet.get_tx_key] gives the key of the transaction, which proves the payment too, with
[`check_tx_key`][monero.MoneroWallet.check_tx_key]. But a key is not tied to a message: whoever gets it can show the same payment for any
purpose, for good. A proof is made for its message, and the customer can make another one for another request.

The shop can prove the other way too, that it received: [`get_tx_proof`][monero.MoneroWallet.get_tx_proof] works from the wallet of the
receiver as well. And a customer can prove that a payment was theirs, not of somebody else who claims it, with a **spend proof**:
[`get_spend_proof`][monero.MoneroWallet.get_spend_proof] and [`check_spend_proof`][monero.MoneroWallet.check_spend_proof]
([Proofs and Signatures](../basics/proofs_and_signatures.md)).
