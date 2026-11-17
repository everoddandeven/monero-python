---
title: Wallet Interface
---
# Wallet Interface

[`MoneroWallet`][monero.MoneroWallet] is the interface that the four wallets implement: code written for it works with a
[full](wallet_full.md), an [RPC](wallet_rpc.md), a [light](wallet_light.md) or a [keys-only](wallet_keys.md) wallet, within what each
one supports ([Wallet Support](wallet_support.md), which groups its methods by topic).

| Topic | Methods |
| --- | --- |
| keys and addresses | `get_seed`, `get_primary_address`, `get_address`, `get_integrated_address`, the keys |
| daemon and sync | `set_daemon_connection`, `sync`, `start_syncing`, `get_height`, `get_daemon_height` |
| balances and accounts | `get_balance`, `get_unlocked_balance`, `get_accounts`, `create_account`, `create_subaddress` |
| transactions, transfers and outputs | `get_txs`, `get_transfers`, `get_outputs`, with their [queries](data_model/wallet/inputs.md) |
| sending | `create_tx`, `create_txs`, `sweep_unlocked`, `relay_tx`, the transaction sets of cold and multisig wallets |
| proofs and messages | `sign_message`, `get_tx_proof`, `get_reserve_proof_wallet` and their checks |
| multisig | `prepare_multisig`, `make_multisig`, `exchange_multisig_keys`, `sign_multisig_tx_hex` |
| listeners, saving, closing | `add_listener`, `save`, `close` |

The [examples](../examples/index.md) show them at work.

::: monero.MoneroWallet
