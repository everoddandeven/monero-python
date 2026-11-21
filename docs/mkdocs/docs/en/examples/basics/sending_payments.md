---
title: Sending Payments
---
# Sending Payments

A payment is a [`MoneroTxConfig`][monero.MoneroTxConfig]: where it goes, how much, from which account, and whether to send it at once.

```python
from monero import MoneroTxConfig, MoneroTxWallet, MoneroWalletRpc

# the wallet to send from
wallet = MoneroWalletRpc("http://wallet_rpc_uri:18083")
wallet.open_wallet("wallet_name", "wallet_password")

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

With `relay = False` the transactions are created and not sent: their fee can be shown first, and
[`relay_tx`][monero.MoneroWallet.relay_tx] sends them later ([Checking Out as a Customer](../scenarios/checkout.md)).

A transaction can pay more destinations at once, up to 15: a transaction has at most 16 outputs, one of them the change.
`can_split` lets the wallet make more transactions when one is not enough:

```python
from monero import MoneroDestination, MoneroTxConfig

batch = MoneroTxConfig()
batch.account_index = 0
batch.destinations = [
    MoneroDestination("...destination address 1...", 1000000000),
    MoneroDestination("...destination address 2...", 2500000000),
    MoneroDestination("...destination address 3...", 500000000),
]
batch.can_split = True      # more transactions, if one is not enough
batch.relay = True
txs = wallet.create_txs(batch)
```

[Batch Withdrawals](../scenarios/batch_withdrawals.md) pays many destinations in batches.
