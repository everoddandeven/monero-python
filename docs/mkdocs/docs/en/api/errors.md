---
title: Errors
---
# Errors

A call that fails raises an exception with the message of what failed:

| Exception | Raised for |
| --- | --- |
| [`MoneroRpcError`][monero.MoneroRpcError] | an error that a daemon or a wallet server returned to a request: its `code` is the one of the JSON-RPC error of the server |
| `RuntimeError` | anything else: a method that the wallet does not support, an argument that is not valid, a server that does not answer, a failure of the wallet |

!!! note "A work in progress"
    monero-cpp is moving its errors to `monero_error`, the error of C++ that [`MoneroError`][monero.MoneroError] stands for: its RPC
    clients already raise `monero_rpc_error`, which is `MoneroRpcError` here, the rest of it still raises the errors of the standard
    library, which are `RuntimeError` here. Catch the two as the table says.

```python
from monero import MoneroNetworkType, MoneroRpcError, MoneroWalletConfig, MoneroWalletKeys, MoneroWalletRpc

wallet = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
try:
    wallet.open_wallet("main", "wrong password")
except MoneroRpcError as e:
    print(f"the server refused it: {e} (code {e.code})")
except RuntimeError as e:
    print(f"it failed: {e}")

# a method that a wallet does not support raises a RuntimeError that says so
config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.MAINNET
keys = MoneroWalletKeys.create_wallet_random(config)
try:
    keys.get_height()
except RuntimeError as e:
    print(e)    # get_height() not supported
```

[Wallet Support](wallet_support.md) says which methods each wallet supports.

::: monero.MoneroError

::: monero.MoneroRpcError
