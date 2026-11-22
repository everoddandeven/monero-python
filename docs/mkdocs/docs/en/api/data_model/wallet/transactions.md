---
title: Transactions, Transfers and Outputs
---
# Transactions, Transfers and Outputs

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroTxWallet`][monero.MoneroTxWallet] | a transaction of the wallet: its `incoming_transfers`, its `outgoing_transfer`, its outputs, and its `tx_set` when it is not signed or relayed | [`get_txs`][monero.MoneroWallet.get_txs], [`create_tx`][monero.MoneroWallet.create_tx] |
| [`MoneroTransfer`][monero.MoneroTransfer], [`MoneroIncomingTransfer`][monero.MoneroIncomingTransfer], [`MoneroOutgoingTransfer`][monero.MoneroOutgoingTransfer] | what a transaction moved for the wallet: in, to a subaddress, or out, from an account to its destinations; each has its `tx` | [`get_transfers`][monero.MoneroWallet.get_transfers], [`get_incoming_transfers`][monero.MoneroWallet.get_incoming_transfers], [`get_outgoing_transfers`][monero.MoneroWallet.get_outgoing_transfers] |
| [`MoneroOutputWallet`][monero.MoneroOutputWallet] | an output of the wallet: its amount, whether it is spent or frozen, its account and subaddress | [`get_outputs`][monero.MoneroWallet.get_outputs] |
| [`MoneroTxSet`][monero.MoneroTxSet] | transactions to sign or to submit elsewhere: unsigned, signed, or of a multisig wallet | [`describe_tx_set`][monero.MoneroWallet.describe_tx_set], [`sign_txs`][monero.MoneroWallet.sign_txs] |

A transaction links to its transfers and outputs, and they link back to it: one query returns the graph, from any of its ends.

::: monero.MoneroTxWallet

::: monero.MoneroTransfer

::: monero.MoneroIncomingTransfer

::: monero.MoneroOutgoingTransfer

::: monero.MoneroOutputWallet

::: monero.MoneroTxSet
