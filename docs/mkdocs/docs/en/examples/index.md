---
title: Examples
---
# Examples

The examples are in two parts:

- **Basics**: one topic each, the calls that it takes: connecting to a server, the three wallets, sending, querying, listening, proofs,
  multisig.
- **Scenarios**: what an application does with them, from start to end: each one puts several of the basics together for a real use.

## Scenarios

### Commerce

| Scenario | What it shows |
| --- | --- |
| [Accepting Payments in a Shop](scenarios/accepting_payments.md) | a subaddress for each order, a payment URI for its QR code, a listener that sees the payment, the confirmations to wait, and the unlock time to check |
| [Checking Out as a Customer](scenarios/checkout.md) | the other side: reading a payment URI, showing the fee before sending, and a note on the payment |

### Exchanges and Services

| Scenario | What it shows |
| --- | --- |
| [Batch Withdrawals](scenarios/batch_withdrawals.md) | many users paid in one transaction, with the limit of its outputs, the fee by priority and the change that locks |
| [Proof of Reserves](scenarios/proof_of_reserves.md) | proving that the funds of the users are there, without the view key, and what such a proof does not prove |

### Custody

| Scenario | What it shows |
| --- | --- |
| [Signing Offline with a Cold Wallet](scenarios/cold_signing.md) | the spend key on a machine that is never online: a view-only wallet prepares the transaction, the offline one signs it |
| [Escrow with a 2-of-3 Multisig](scenarios/escrow_with_multisig.md) | a buyer, a seller and an arbiter: the funds wait in a multisig wallet, and any two of them decide where they go |

### Trust and Identity

| Scenario | What it shows |
| --- | --- |
| [Proving a Payment in a Dispute](scenarios/payment_dispute.md) | a customer proves that a payment reached the shop, without giving away a key |
| [Sign in with Monero](scenarios/sign_in.md) | an address as the account of a site, and a signed challenge instead of a password |

### Operations

| Scenario | What it shows |
| --- | --- |
| [Backup and Recovery](scenarios/backup_and_recovery.md) | what to keep, restoring from the seed and a date, the rescans, and checking a backup |
| [Developing on Regtest](scenarios/developing_on_regtest.md) | a chain of your own, with blocks mined on demand, to try every state of a payment in seconds |

## Before running them

- The code needs a daemon, and the RPC wallets a `monero-wallet-rpc` ([RPC Wallet](../api/wallet_rpc.md#the-server)). Try them on
  **stagenet**, whose coins have no value: the [Glossary](../api/glossary.md#networks) has the ports of each network.
- The seeds, addresses and hashes written as `"..."` are yours to fill in.
- Every amount is in atomic units, 1 XMR is 10¹² of them: `MoneroUtils.xmr_to_atomic_units(0.25)` is 0.25 XMR.
- The code of the pages is checked against the types of the library, the one of the scenarios is cut down to what each step does: an
  application adds the handling of its errors ([Errors](../api/errors.md)) and the storage of its state.
