---
title: Daemon RPC
---
# Daemon RPC

The client of the RPC of a `monerod` ([Interact with RPC Daemon](../examples/basics/interact_with_daemon.md)). It is made with the URI
of the daemon and its credentials, or with a [`MoneroRpcConnection`][monero.MoneroRpcConnection], and polls the daemon for its
[listeners](../examples/basics/listening_to_a_wallet.md#a-daemon).

## ZMQ

A daemon is polled every [`set_poll_period_in_ms`][monero.MoneroDaemonRpc.set_poll_period_in_ms], 10 seconds when it is not set, to tell its
listeners of a new block, which may then be one period late. If its connection has a `zmq_uri`, the `--zmq-pub` of the `monerod`
([ZMQ](connection.md#zmq)), the daemon is polled also each time the `monerod` publishes a block, and the listeners are told as it is added:

```python
from monero import MoneroDaemonRpc

daemon = MoneroDaemonRpc("http://localhost:18081", zmq_uri="tcp://127.0.0.1:18083")
```

The period still holds: ZMQ does not guarantee that a publication arrives, so the daemon is polled every period whether the `monerod`
publishes or not, and a block that it did not publish is told at most a period late. The daemon is polled by the period alone when the
connection has no `zmq_uri`, when it has a `proxy_uri` (ZMQ connects directly, and would skip it), and when the subscription fails, which is
logged. The `zmq_uri` and the `proxy_uri` are read at each poll, so a connection that changes them while the daemon is listened to is
followed.

::: monero.MoneroDaemonRpc
