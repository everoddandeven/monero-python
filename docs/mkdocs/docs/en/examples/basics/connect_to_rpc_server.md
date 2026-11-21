---
title: Connect to RPC Server
---
# Connect to RPC Server

A [`MoneroRpcConnection`][monero.MoneroRpcConnection] is the connection to a daemon or to a wallet server: its URI, its credentials, a
proxy, and how long to wait for an answer.

```python
from monero import MoneroRpcConnection

# connect to a monerod or wallet rpc server
connection = MoneroRpcConnection("http://localhost:38081")

# set connection credentials if needed
connection.set_credentials("rpc_user", "rpc_password")

# check rpc connection
connection.check_connection()

if not connection.is_connected():
    raise Exception("Could not connect to RPC server.")

print("Connection established to RPC server.")
```

Once connected, it can also call a method of the JSON-RPC interface of the server directly, one that the library has no method for:

```python
# invoke JSON-RPC method `get_version`
result = connection.send_json_request("get_version")
print(f"get_version JSON-RPC response: {result}")
```

`MoneroRpcConnection` also takes a `proxy_uri`, in its constructor or later: the traffic goes through it, as through Tor to reach a
daemon at an onion address:

!!! note
    Setting a `proxy_uri` resets `MoneroRpcConnection` status.

```python
# setup TOR proxy uri by instance attribute
connection.proxy_uri = "127.0.0.1:9050"

# must recall `check_connection()` manually
connection.check_connection()
```
