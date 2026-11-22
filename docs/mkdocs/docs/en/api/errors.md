---
title: Errors
---
# Errors

!!! warning "Work in progress"
    monero-cpp is moving its errors to `monero_error`, which is `MoneroError` here, and `monero_rpc_error`, which is `MoneroRpcError`.
    Most of the calls of the module already raise them, the others still raise the errors of the standard library of C++, which are
    `RuntimeError`.

A call that fails raises an exception with the message of what failed:

| Exception | Raised for |
| --- | --- |
| [`MoneroRpcError`][monero.MoneroRpcError] | an error that a daemon or a wallet server returned to a request: its `code` is the one of the JSON-RPC error of the server |
| [`MoneroError`][monero.MoneroError] | an error of monero-cpp or of monero: a method that the wallet does not support, an argument that is not valid, a server that does not answer, a failure of the wallet |
| `RuntimeError` | an error of C++ that does not pass through the errors of monero-cpp yet |

`MoneroRpcError` is a `MoneroError`, and `MoneroError` is a `RuntimeError`: `except MoneroError` catches the first two,
`except RuntimeError` all of them.

```python
from monero import MoneroError, MoneroNetworkType, MoneroRpcError, MoneroWalletConfig, MoneroWalletKeys, MoneroWalletRpc

wallet = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
try:
    wallet.open_wallet("main", "wrong password")
except MoneroRpcError as e:
    print(f"the server refused it: {e} (code {e.code})")
except MoneroError as e:
    print(f"it failed: {e}")

# a method that a wallet does not support raises a MoneroError that says so
config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.MAINNET
keys = MoneroWalletKeys.create_wallet_random(config)
try:
    keys.get_height()
except MoneroError as e:
    print(e)    # get_height() not supported
```

[Wallet Support](wallet_support.md) says which methods each wallet supports.

::: monero.MoneroError

::: monero.MoneroRpcError
