---
title: Connect to RPC Server
---
# Connect to RPC Server

Developers can create and establish a connection to a rpc server conveniently with a `MoneroRpcConnection`:

```python
from monero import MoneroRpcConnection

# connect to a monerod or wallet rpc server
connection = MoneroRpcConnection("http:://rpc_server_uri:18089")

# set connection credentials if needed
connection.set_credentials("rpc_user", "rpc_password")

# check rpc connection
connection.check_connection()

if not connection.is_connected():
    raise Exception("Could not connect to RPC server.")

print("Connection established to RPC server.")
```

After successfully connecting to the rpc server, developers can also invoke methods of the JSON-RPC interface directly:

```python
# invoke JSON-RPC method `get_version`
result = connection.send_json_request("get_version")
print(f"get_version JSON-RPC response: {result}")
```

`MoneroRpcConnection` also accepts an optional `proxy_uri` parameter in its constructor, manageable even after a connection has been created. A prime example of use is to route your traffic via TOR:

!!! note
    Setting a `proxy_uri` resets `MoneroRpcConnection` status.

```python
# setup TOR proxy uri by instance attribute
connection.proxy_uri = "127.0.0.1:9050"

# must recall `check_connection()` manually
connection.check_connection()
```
