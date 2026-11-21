---
title: tests/daemon
---
# tests/daemon

The tests of the daemon.

## tests/daemon/rpc

The rpc daemon, `MoneroDaemonRpc`, on `node_2`. All integration tests.

| File | What it tests |
| --- | --- |
| `test_info.py` | the version, the trust, the general, sync and hard fork information, the network stats, an offline daemon |
| `test_blocks.py` | the height, the block template, the headers and the blocks by hash, height and range (also binary and in chunks), the block hashes, the miner tx sum, the alternative chains, popping blocks |
| `test_txs.py` | the transactions and their hex by hash, also in the pool |
| `test_tx_pool.py` | the fee estimate, the pool and its stats, flushing it, submitting and relaying transactions |
| `test_outputs.py` | the spent status of key images, the output histogram and distribution, the output indices and the outputs |
| `test_peers.py` | the peers, known and public, the limits of the peers and of the bandwidth, the bans |
| `test_mining.py` | mining, its status, submitting a block, the miner data, the proof of work, the auxiliary proof of work |
| `test_admin.py` | pruning, the updates, saving the chain, the cache, the bootstrap daemon, the poll period, the log level and categories |
| `test_listeners.py` | the block listeners: being notified, removing them, starting and stopping |

## The other daemon tests

| File | Marker | What it tests |
| --- | --- | --- |
| `test_interface.py` | unit | the calls of the daemon interface `MoneroDaemon`, which raise "not supported" there |
| `test_listener_lifetime.py` | unit | a listener that Python does not reference any more stays alive while the daemon has it, and a daemon is destroyed safely with a request in flight |
| `model/test_blocks.py` | unit | blocks, headers, templates and their results: deserialization, copy, merge |
| `model/test_txs.py` | unit | transactions, submit results and pool stats: deserialization, copy, merge, ordering |
| `model/test_outputs.py` | unit | key images, outputs, distributions and histograms |
| `model/test_info.py` | unit | the information of the daemon: alternative chains, pruning, fee estimate, sync, hard fork, network stats, updates |
| `model/test_mining.py` | unit | mining status, miner tx sum, generated blocks, miner data, auxiliary proof of work |
| `model/test_peers.py` | unit | bans, connection spans, peers and their connection type |
| `model/test_rpc.py` | unit | the version, the rpc payment info, the rpc connection |
