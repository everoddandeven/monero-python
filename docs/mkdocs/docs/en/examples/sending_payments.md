---
title: Sending Payments
---
# Sending Payments

In order to send payments with a `MoneroWallet`, developers must setup a `MoneroTxConfig`:

```python
from monero import MoneroTxConfig

# create and setup transaction configuration
tx_config = MoneroTxConfig()

# specify source account index
tx_config.account_index = 0

# specify address and destination amount
tx_config.address = "...destination address..."
tx_config.amount = 1000000000

# relay tx to the network
tx_config.relay = True

# create txs with configuration
txs: list[MoneroTxWallet] = wallet.create_txs(tx_config)

for tx in txs:
    print(f"Created tx: {tx.serialize()}")
```

Is possible to setup also multiple destinations in transaction configuration:

```python
tx_config.destinations.append(MoneroDestination("...destination address1...", 1000000000))

...

tx_config.destinations.append(MoneroDestination("...destination addressN...", 1000000000))

# split into multiple txs
tx_config.can_split = True

```
