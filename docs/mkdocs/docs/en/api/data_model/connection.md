---
title: Connection Data Model
---
# Connection Data Model

The classes around a [`MoneroRpcConnection`][monero.MoneroRpcConnection], the connection to a daemon or to a wallet server:

| Class | What it is |
| --- | --- |
| [`SslOptions`][monero.SslOptions] | the SSL of a connection: the certificates, and how the one of the server is checked; passed to [`MoneroWalletRpc.set_daemon_connection`][monero.MoneroWalletRpc.set_daemon_connection] |
| [`MoneroConnectionType`][monero.MoneroConnectionType] | how a peer of a daemon is connected, IPv4, IPv6, Tor or I2P: the `connection_type` of a [`MoneroPeer`][monero.MoneroPeer] |

::: monero.SslOptions

::: monero.MoneroConnectionType
