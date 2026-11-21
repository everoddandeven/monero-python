---
title: Configuration
---
# Configuration

`tests/config/config.ini` has the settings of all the tests. The values of the repository are the ones of the docker network.

## `[general]`

| Key | Default | What it does |
| --- | --- | --- |
| `network_type` | `regtest` | the network of the daemon and of the wallets: `mainnet`, `testnet`, `stagenet` or `regtest` |
| `test_non_relays` | `True` | the tests that do not send to the network. `False` skips most of the integration tests |
| `test_relays` | `True` | the tests that relay transactions to the network |
| `test_notifications` | `True` | the tests of the listeners of the daemon and of the wallets |
| `test_resets` | `True` | the tests that make a wallet read the chain again: `scan_txs`, `rescan_spent`, `rescan_blockchain` |
| `lite_mode` | `False` | `True` skips the slowest tests |
| `auto_connect_timeout_ms` | `3000` | the timeout of the tests of the connection manager |
| `log_level` | `3` | the log level of monero-cpp, from 0 to 4 |
| `log_categories` | `*:WARNING,...` | the log categories of monero-cpp |

## `[daemon]`

| Key | What it is |
| --- | --- |
| `rpc_uri`, `rpc_username`, `rpc_password` | the rpc of the daemon of the tests, `node_2` |
| `zmq_uri`, `zmq_pub_uri` | its zmq rpc and zmq notifications |
| `poll_period_in_ms` | how often the listeners of the daemon ask for a new block |
| `log_level` | the log level that the tests set on the daemon |

## `[wallet]`

| Key | What it is |
| --- | --- |
| `name`, `password`, `language` | the test wallet: the name of its file, its password, the language of its seed |
| `seed`, `address`, `private_view_key`, `private_spend_key`, `public_view_key`, `public_spend_key` | the keys of the test wallet, which every wallet type opens |
| `first_receive_height` | the height of its first funds |
| `dir` | the folder of the wallet files of the full wallet, `./test_wallets` |
| `rpc_domain`, `rpc_port_start`, `rpc_username`, `rpc_password` | the wallet rpc servers: `rpc_port_start` is the port of the first one, the others follow |
| `rpc_zmq_enabled`, `rpc_zmq_port_start`, `rpc_zmq_bind_port_start`, `rpc_zmq_domain` | the zmq of the wallet rpc servers, off |
| `sync_period_in_ms` | the period of the background sync of the wallets |

## `[mining_wallet]`

The wallet that receives the mined blocks and funds the others: `name`, `password`, `address`, its keys and `seed`.

## The other files of `tests/config`

| File | What it has |
| --- | --- |
| `test_monero_utils.ini` | the addresses of each network (valid, subaddresses, integrated, invalid), the keys and the seeds that `MoneroUtils` is tested with, and a text to serialize |
| `test_monero_wallet_common.ini` | the seed of the tests that create a wallet from a seed |
