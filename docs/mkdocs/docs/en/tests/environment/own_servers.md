---
title: Servers Not in Docker
---
# Servers Not in Docker

The tests can run against servers of your own, on the host or elsewhere. They expect:

- a daemon on the network of `network_type`, at `rpc_uri`, with the login of `[daemon]`; on regtest, with a peer, as `node_1`;
- three wallet rpc servers, from the port `rpc_port_start` (18082, 18083, 18084), with the login of `[wallet]`;
- the mining wallet and the test wallet of `config.ini`, or keys of your own in it.

Then, before running the tests:

```bash
export IN_CONTAINER=false
```

When a test creates or opens a wallet on a wallet rpc server, it gives the server the address of the daemon. In docker that is
`http://node_2:18081`, the name of the daemon in the network of the containers. `IN_CONTAINER=false` gives it the `rpc_uri` of
`config.ini` instead, the address that a server on the host reaches.
