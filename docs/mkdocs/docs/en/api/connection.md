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
| `timeout_ms` | how long a request waits for the answer: 3 minutes when not set |
| `ssl_verify` | whether the certificate of an `https` server is checked |

[`check_connection`][monero.MoneroRpcConnection.check_connection] tries the server, and then
[`is_online`][monero.MoneroRpcConnection.is_online], [`is_authenticated`][monero.MoneroRpcConnection.is_authenticated] and
[`response_time`][monero.MoneroRpcConnection.response_time] tell how it went. A method of the RPC that the library does not wrap is
called with [`send_json_request`][monero.MoneroRpcConnection.send_json_request], or `send_path_request` and `send_binary_request` for the
other interfaces of the daemon ([Connect to RPC Server](../examples/basics/connect_to_rpc_server.md)).

::: monero.MoneroRpcConnection
