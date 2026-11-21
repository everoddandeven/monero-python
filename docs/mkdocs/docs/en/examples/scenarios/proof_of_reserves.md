---
title: Proof of Reserves
---
# Proof of Reserves

An exchange holds the money of its users. They want to know that it is there, and the exchange does not want to show its wallet: a
**reserve proof** proves that a wallet has at least an amount that is not spent, without the view key: it shows the outputs that hold
the amount, not the history of the wallet.

## The exchange: making the proof

The exchange makes the proof for a message of its choice, which ties it to a date: a proof of last year says nothing of today.

```python
from monero import MoneroWalletRpc

exchange = MoneroWalletRpc("http://localhost:18083", "rpc_user", "abc123")
exchange.open_wallet("reserves", "supersecretpassword123")

address = exchange.get_primary_address()
message = "reserves of the exchange, 2026-11-21"

# all the unspent funds of the wallet
signature = exchange.get_reserve_proof_wallet(message)

# or at least an amount, from one account
signature_account = exchange.get_reserve_proof_account(0, 1000 * 10**12, message)

# publish address, message and signature
```

A proof of the whole wallet shows all that it has, a proof of an account shows that it has at least the amount asked, and not how much
more.

## Anyone: checking it

```python
from monero import MoneroCheckReserve, MoneroUtils, MoneroWalletRpc

checker = MoneroWalletRpc("http://localhost:18084", "rpc_user", "abc123")
check: MoneroCheckReserve = checker.check_reserve_proof(address, message, signature)

if check.is_good:
    total = MoneroUtils.atomic_units_to_xmr(check.total_amount or 0)
    spent = MoneroUtils.atomic_units_to_xmr(check.unconfirmed_spent_amount or 0)
    print(f"the address has {total} XMR, of which {spent} spent in the pool")
else:
    print("the proof is not valid")
```

The checker needs a wallet synced with a daemon, any wallet: it looks on the chain whether the outputs of the proof are spent.

## What it proves, and what not

- It proves that the funds **exist and are not spent**, at the moment of the check. A check of tomorrow can say otherwise: the exchange
  publishes a new proof regularly.
- It does not prove what the exchange **owes**: reserves of 1000 XMR are a lot for users owed 100, and not for users owed 5000. The
  liabilities are proved elsewhere, by the exchange.
- It does not prove that the funds are **only for the users**: the same funds can be in the proof of another exchange, if the two share
  them. A message that names the exchange makes that harder to hide.
- It reveals the **key images** of the outputs: whoever has the proof sees when those outputs are spent, from then on. A proof is public,
  and so is the moment when the exchange moves those funds.
