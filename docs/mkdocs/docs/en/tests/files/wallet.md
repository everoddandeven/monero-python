---
title: tests/wallet
---
# tests/wallet

The tests of the wallets.

## The topics

A file for each topic, with a class for each wallet type: `TestMoneroWalletFull<Topic>` and `TestMoneroWalletRpc<Topic>` are
integration tests, `TestMoneroWalletKeys<Topic>` are unit tests (the keys-only wallet has no daemon, and most of what it does not
support raises at once).

| File | What it tests |
| --- | --- |
| `test_creation.py` | creating wallets (random, from a seed, with an offset, from keys), opening, saving, closing, the path, the password, the attributes, view-only and offline wallets, the subaddress lookahead |
| `test_keys_and_addresses.py` | the seed and its language, the keys, the primary address and the subaddresses, the address indices, the integrated addresses, signing and verifying messages, payment uris |
| `test_connection.py` | the daemon connection of the wallet, the heights of the daemon, an offline wallet |
| `test_sync.py` | syncing, with and without progress, from a seed and from a height, the background sync, the heights by date, scanning and rescanning |
| `test_accounts.py` | balances, accounts and subaddresses, their labels, the account tags, the address book |
| `test_send.py` | sending: to self, to an external address, to several, split, dust, subtracting the fee, from subaddresses, with a payment id, creating then relaying, the default fee priority |
| `test_sweep.py` | sweeping outputs, dust, subaddresses, accounts and the whole wallet |
| `test_txs.py` | the transactions of the wallet: by hash, height and query, the payment ids, the filters, the notes |
| `test_transfers.py` | the transfers, incoming and outgoing, by query |
| `test_outputs.py` | the outputs by query, exporting and importing outputs and key images, freezing outputs |
| `test_proofs.py` | the proofs of transactions, of spends and of reserves, and checking them |
| `test_pool.py` | syncing with the pool: transactions submitted, flushed, relayed |
| `test_update_locked.py` | sending with an unlock time, and the transactions as they unlock |
| `test_listeners.py` | the notifications of the wallets, sender and receiver, in the same or another account or wallet, relayed or not |
| `test_multisig.py` | multisig wallets, M of N, and the sample code |
| `test_mining.py` | starting and stopping mining from the wallet |
| `test_equality.py` | that the wallet equals a new full wallet of the same seed synced from the chain, and that its balances add up across accounts, subaddresses, transactions, transfers and outputs |

`base_test_monero_wallet.py` has the base class of the tests of the wallets, `wallet_support.py` the support classes of the three
types (`FullWalletSupport`, `RpcWalletSupport`, `KeysWalletSupport`), and `conftest.py` the [order](../running/selecting.md#the-order-of-the-wallet-tests)
of the tests and the closing of the wallets at the end.

## The other wallet tests

| File | Marker | What it tests |
| --- | --- | --- |
| `test_interface.py` | unit | every call of the wallet interface `MoneroWallet`, which raise "not supported" there, and the checks that it does itself |
| `test_support.py` | unit | the [support matrix](../../api/wallet_support.md) of `wallet_support.yml`, against what each wallet type implements |
| `test_full_offline.py` | unit | a full wallet without a daemon: the ring database, importing key images, moving it, exporting and importing its files |
| `test_listener_lifetime.py` | unit | a listener that Python does not reference any more stays alive while the wallet has it, and a wallet rpc is destroyed safely with a request in flight |
| `model/test_config.py` | unit | the wallet and tx configs and the destinations |
| `model/test_accounts.py` | unit | subaddresses, accounts, integrated and decoded addresses, address book entries, account tags |
| `model/test_txs.py` | unit | wallet transactions and tx sets: deserialization, copy, merge, their inputs, outputs and transfers |
| `model/test_transfers.py` | unit | incoming and outgoing transfers: deserialization, copy, merge, ordering |
| `model/test_outputs.py` | unit | wallet outputs: deserialization, copy, merge, ordering |
| `model/test_tx_query.py` | unit | the tx query: which transactions it matches, deserialization, copy |
| `model/test_transfer_query.py` | unit | the transfer query: which transfers it matches, deserialization, copy |
| `model/test_output_query.py` | unit | the output query: which outputs it matches, deserialization, copy |
| `model/test_results.py` | unit | the results of key image imports and exports, message signatures, checks, multisig, sync |
