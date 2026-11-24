---
title: tests/common
---
# tests/common

What is not about a wallet or a daemon.

| File | Marker | What it tests |
| --- | --- | --- |
| `test_common.py` | unit | `MoneroError`, the serialization of the structs, the SSL options |
| `test_serializable_struct.py` | unit | the equality, the hash and the `repr` of the structs, of `MoneroRpcConnection` and of `MoneroWalletConfig` |
| `test_rpc_connection.py` | integration | `MoneroRpcConnection`: the validation of the uri, the copy and the serialization, the credentials, the priority, the connections to a node and to a wallet rpc server, the json, binary and path requests |
| `test_gen_utils.py` | unit | the helpers of the tests: the uuids, the waits, and the reconciliation of the values of two models (the rules of `merge`) |
| `test_block_generation.py` | unit | the choice of the tests between generating blocks (at a low difficulty) and mining them |
| `test_wallet_tx_tracker.py` | unit | the helper that waits for the transactions of the wallets to leave the pool before the next one |

## tests/common/monero_utils

`MoneroUtils`, a file for each topic, all unit tests.

| File | What it tests |
| --- | --- |
| `test_amounts.py` | the conversion between XMR and atomic units: rounding, invalid amounts, the limits of uint64 |
| `test_blocks.py` | `get_blocks_from_txs`, `get_blocks_from_transfers` and `get_blocks_from_outputs`: the blocks without duplicates and in order, the unconfirmed ones, the errors |
| `test_general.py` | the integrated addresses, the version, the ring size |
| `test_memory.py` | `MoneroUtils.free`: breaking the references between blocks, transactions, transfers and outputs, so that they are freed |
| `test_payment_uri.py` | making and parsing payment uris: the parameters, the payment ids, the wrong ones |
| `test_serialization.py` | the binary serialization of heights, big values and texts |
| `test_validation.py` | the validation of addresses, keys, seeds, seed languages and payment ids |
