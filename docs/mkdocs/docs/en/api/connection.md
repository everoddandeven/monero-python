---
title: RPC Connection
---
# RPC Connection

A [`MoneroRpcConnection`][monero.MoneroRpcConnection] is how a daemon or a wallet server is reached:

| Field | What it is |
| --- | --- |
| `uri` | the address of the server, `http://host:port` or `https://...` |
| `username`, `password` | the login of its RPC, `--rpc-login` of the server ([`set_credentials`][monero.MoneroRpcConnection.set_credentials]) |
| `proxy_uri` | a proxy for the requests, as the SOCKS of Tor to reach an onion address |
| `zmq_uri` | the ZMQ publisher of a daemon, `--zmq-pub` of `monerod`, as `tcp://127.0.0.1:18083`: [ZMQ](#zmq) |
| `timeout_ms` | how long a request waits for the answer: 3 minutes when not set |
| `ssl_verify` | whether the certificate of an `https` server is checked |

[`check_connection`][monero.MoneroRpcConnection.check_connection] tries the server, and then
[`is_online`][monero.MoneroRpcConnection.is_online], [`is_authenticated`][monero.MoneroRpcConnection.is_authenticated] and
[`response_time`][monero.MoneroRpcConnection.response_time] tell how it went. A method of the RPC that the library does not wrap is
called with [`send_json_request`][monero.MoneroRpcConnection.send_json_request], or `send_path_request` and `send_binary_request` for the
other interfaces of the daemon ([Connect to RPC Server](../examples/basics/connect_to_rpc_server.md)). Their response is parsed as Python's
`json` module parses it, and they run without the GIL: threads with a connection each send their requests at once.

## ZMQ

A `monerod` that runs with `--zmq-pub` publishes what happens on its chain and in its pool over ZMQ: a block added to the chain, a
transaction that enters the pool. It is the `zmq_uri` of the connection, which is not the one of `--zmq-rpc-bind-port`, and
[`subscribe_zmq`][monero.MoneroRpcConnection.subscribe_zmq] connects to it and returns a
[`MoneroZmqSubscriber`][monero.MoneroZmqSubscriber], which gives the [`MoneroZmqPublication`][monero.MoneroZmqPublication] of the topics that
it was asked for. The `json` of a publication is the text that the daemon published:

```python
import json

from monero import MoneroRpcConnection

connection = MoneroRpcConnection("http://localhost:18081", zmq_uri="tcp://127.0.0.1:18083")
subscriber = connection.subscribe_zmq(["json-minimal-chain_main"])

publication = subscriber.wait_for_publication(10000)
if publication is not None:
    print(publication.topic, json.loads(publication.json))
```

- [`wait_for_publication`][monero.MoneroZmqSubscriber.wait_for_publication] waits as long as it is told for the next publication, and gives
  `None` if there is none by then. It runs without the GIL, as the requests do.
  [`discard_publications`][monero.MoneroZmqSubscriber.discard_publications] drops those that are waiting, for a program that only cares for
  what happens next.
- ZMQ matches a topic by its start: `json-minimal` takes all the publications of the minimal JSON, and `json-minimal-chain_main` only the
  ones of the blocks that are added to the main chain.
- The subscriber connects in the background, and again every second if it loses the daemon: `subscribe_zmq` does not fail because the
  daemon is not there. A publication that the daemon makes while the subscriber is not connected is lost, and ZMQ does not send it again: a
  program that can not miss a block reads the chain from the daemon too.
- A subscriber is used by one thread at a time.
- `subscribe_zmq` raises a [`MoneroError`][monero.MoneroError] if the connection has no `zmq_uri`, and if it has a `proxy_uri`: ZMQ connects
  directly, and would skip the proxy.

A [`MoneroDaemonRpc`][monero.MoneroDaemonRpc] uses it to learn of the new blocks sooner: [Daemon RPC](daemon_rpc.md#zmq).

::: monero.MoneroRpcConnection
