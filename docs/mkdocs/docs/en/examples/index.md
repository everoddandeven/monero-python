---
title: Examples
---
# Examples

The examples are in two parts:

- **Basics**: one topic each, the calls that it takes: connecting to a server, the three wallets, sending, querying, listening, proofs,
  multisig.
- **Scenarios**: what an application does with them, from start to end: each one puts several of the basics together for a real use.

| Scenario | What it shows |
| --- | --- |
| [Accepting Payments in a Shop](scenarios/accepting_payments.md) | a subaddress for each order, a payment URI for its QR code, a listener that sees the payment, and the confirmations to wait |
| [Escrow with a 2-of-3 Multisig](scenarios/escrow_with_multisig.md) | a buyer, a seller and an arbiter: the funds wait in a multisig wallet, and any two of them decide where they go |
| [Signing Offline with a Cold Wallet](scenarios/cold_signing.md) | the spend key on a machine that is never online: a view-only wallet prepares the transaction, the offline one signs it |
| [Proving a Payment in a Dispute](scenarios/payment_dispute.md) | a customer proves that a payment reached the shop, without giving away a key |

## Before running them

- The code needs a daemon, and the RPC wallets a `monero-wallet-rpc` ([RPC Wallet](../api/wallet_rpc.md#the-server)). Try them on
  **stagenet**, whose coins have no value: the [Glossary](../api/glossary.md#networks) has the ports of each network.
- The seeds, addresses and hashes written as `"..."` are yours to fill in.
- Every amount is in atomic units, 1 XMR is 10¹² of them: `MoneroUtils.xmr_to_atomic_units(0.25)` is 0.25 XMR.
- The code of the pages is checked against the types of the library, the one of the scenarios is cut down to what each step does: an
  application adds the handling of its errors ([Errors](../api/errors.md)) and the storage of its state.
