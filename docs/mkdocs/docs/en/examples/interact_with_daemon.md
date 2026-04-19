---
title: Interact with RPC Daemon
---
# Interact with RPC Daemon

`MoneroDaemonRpc` offers a `MoneroDaemon` implementation that interacts with [monero-rpc](https://docs.getmonero.org/rpc-library/monerod-rpc/) server using calls to `RPC`, `JSON-RPC` and `Binary` interfaces.

Creating a `MoneroDaemonRpc` instance is very simple:

```python
from monero import MoneroDaemonRpc

# create RPC daemon connected to `monerod-rpc` server
daemon = MoneroDaemonRpc("http://monerod_rpc_uri:18081")
```

It can also be done using a `MoneroRpcConnection` instance:

```python
from monero import MoneroRpcConnection, MoneroDaemonRpc

# create rpc connection
connection = MoneroRpcConnection("http://monerod_rpc_uri:18081")

# create daemon using RPC connection
daemon = MoneroDaemonRpc(connection)
```

Fetch daemon info and status:

```python
# get general daemon rpc info
daemon_info = daemon.get_info()
print(f"Daemon info: {daemon_info.serialize()}")

# get daemon specific sync info
sync_info = daemon.get_sync_info()
print(f"Sync info: {sync_info.serialize()}")

# get peer bans
bans = daemon.get_peer_bans()
for ban in bans:
    print(f"Banned peer: {peer.serialize()}")
```

Query blocks and txs on blockchain:

```python
# get last block header added to blockchain
last_block = daemon.get_last_block_header()
print(f"Last block header: {last_block.serialize()}")

# get specific block by height
block = daemon.get_block_by_height(1520000)
print(f"Block fetched by height: {block.serialize()}")

# get specific block by hash
block = daemon.get_block_by_hash("...block hash...")
print(f"Block fetched by hash: {block.serialize()}")

# get alternative chains seen by the daemon
chains = daemon.get_alt_chains()
print(f"Found {len(chains)} alternative chains")

# get unconfirmed txs in pool
tx_pool = daemon.get_tx_pool()
for tx in tx_pool:
    print(f"Found tx in pool: {tx.serialize()}")

# get specific tx added to chain
tx = daemon.get_tx("...tx hash...")
print(f"Fetched tx: {tx.serialize()}")
```

Relay mined blocks and signed txs:

```python
# submit a mined block
daemon.submit_block("...block blob...")

# submit a signed tx
tx: Monerotx = ...
daemon.submit_tx(tx.full_hex)

```