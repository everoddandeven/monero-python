---
title: Configurations and Queries
---
# Configurations and Queries

| Class | What it is | For |
| --- | --- | --- |
| [`MoneroWalletConfig`][monero.MoneroWalletConfig] | how to create or open a wallet: path, password, network, seed or keys, daemon | [`MoneroWalletFull.create_wallet`][monero.MoneroWalletFull.create_wallet], [`MoneroWalletRpc.create_wallet`][monero.MoneroWalletRpc.create_wallet], the functions of [`MoneroWalletKeys`][monero.MoneroWalletKeys] |
| [`MoneroTxConfig`][monero.MoneroTxConfig], [`MoneroDestination`][monero.MoneroDestination], [`MoneroTxPriority`][monero.MoneroTxPriority] | a payment to make: its `destinations`, each an address and an amount, the account to pay from, the priority of its fee, whether to relay it | [`create_tx`][monero.MoneroWallet.create_tx], [`create_txs`][monero.MoneroWallet.create_txs], [`sweep_unlocked`][monero.MoneroWallet.sweep_unlocked] |
| [`MoneroTxQuery`][monero.MoneroTxQuery], [`MoneroTransferQuery`][monero.MoneroTransferQuery], [`MoneroOutputQuery`][monero.MoneroOutputQuery] | which transactions, transfers or outputs to get: each is the class that it selects, with the fields to match, and can hold the query of the others (`tx_query`, `transfer_query`, `output_query`) | [`get_txs`][monero.MoneroWallet.get_txs], [`get_transfers`][monero.MoneroWallet.get_transfers], [`get_outputs`][monero.MoneroWallet.get_outputs] |
| [`MoneroMessageSignatureType`][monero.MoneroMessageSignatureType] | which key signs a message | [`sign_message`][monero.MoneroWallet.sign_message] |

::: monero.MoneroWalletConfig

::: monero.MoneroTxConfig

::: monero.MoneroDestination

::: monero.MoneroTxPriority

::: monero.MoneroTxQuery

::: monero.MoneroTransferQuery

::: monero.MoneroOutputQuery

::: monero.MoneroMessageSignatureType
