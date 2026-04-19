---
title: Create Local Full Wallet
---
# Create Local Full Wallet

`MoneroWalletFull` is another `MoneroWallet` implementation that fully wraps [wallet2 API](https://github.com/monero-project/monero/blob/master/src/wallet/wallet2.h). With a full wallet developers can create wallet files and manage them locally.

Creating a `MoneroWalletFull` is very simple:

```python
from monero import MoneroWalletConfig, MoneroWalletFull, MoneroNetworkType

# setup wallet configuration
config = MoneroWalletConfig()

# setup wallet path
config.path = "test_wallet_full"

# setup wallet password
config.password = "supersecretpassword123"

# setup wallet network type
config.network_type = MoneroNetworkType.TESTNET

wallet = MoneroWalletFull.create_wallet(config)
```

Check if a Monero wallet exists at specific path:

```python
if MoneroWalletFull.wallet_exists("test_wallet_full"):
    wallet = MoneroWalletFull.open_wallet("test_wallet_full", "supersecretpassword123", MoneroNetworkType.TESTNET)
```
