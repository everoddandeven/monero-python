---
title: Daemon Interface
---
# Daemon Interface

[`MoneroDaemon`][monero.MoneroDaemon] is the interface of a daemon, which [`MoneroDaemonRpc`][monero.MoneroDaemonRpc] implements over
the RPC of `monerod`: the chain, its blocks and transactions, the pool, the peers, mining, and the state of the daemon
([Daemon Data Model](data_model/daemon.md)).

A public node runs with `--restricted-rpc`: it answers what reads the chain and the pool, and refuses what administers the daemon, such
as [`stop`][monero.MoneroDaemon.stop], [`set_peer_ban`][monero.MoneroDaemon.set_peer_ban] or
[`start_mining`][monero.MoneroDaemon.start_mining]. These need a daemon of your own.

::: monero.MoneroDaemon
