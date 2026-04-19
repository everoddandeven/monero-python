---
title: Query Wallet Txs and Transfers
---
# Query Wallet Txs and Transfers

The `MoneroWallet` interface offers methods for fetching transactions, transfers and outputs from wallet's cache:

* ```MoneroWallet.get_txs(query: MoneroTxQuery) -> list[MoneroTxWallet]```
* ```MoneroWallet.get_transfers(query: MoneroTransferQuery) -> list[MoneroTransfer]```
* ```MoneroWallet.get_outputs(query: MoneroOutputQuery) -> list[MoneroOutputWallet]```

This methods can be used with a `MoneroTxQuery`, `MoneroTransferQuery`, `MoneroOutputQuery`, wich will filter all records that doesn't match criteria defined in the query.

Example of fetching wallet txs with a basic `MoneroTxQuery`:

```python
from monero import (
    MoneroWallet, MoneroTxQuery,
    MoneroTxWallet
)

# open a wallet with txs data
wallet: MoneroWallet = ...

# create and setup a new tx query to filter txs with
query = MoneroTxQuery()

# fetch only outgoing txs
query.is_incoming = False
query.is_outgoing = True

# include outputs in tx data
query.include_outputs = True

# filter tx by height range
query.min_height = 150000
query.max_height = 300000

# or get txs at specific height
query.height = 152000

# fetch txs that meets criteria from wallet
txs: list[MoneroTxWallet] = wallet.get_txs(query)

# print fetched txs
for tx in txs:
    print(f"Found tx: {tx.serialize()}")
```

Example of fetching wallet transfers with a `MoneroTransferQuery`:

```python
from monero import (
    MoneroWallet, MoneroTransferQuery,
    MoneroTransfer
)

# open a wallet with txs data
wallet: MoneroWallet = ...

# create and setup a new tx query to filter transfers with
query = MoneroTransferQuery()

# fetch only incoming transfers
query.is_incoming = True
query.is_outgoing = False

# filter by account and subaddress index
query.account_index = 1
query.subaddress_indices = [0, 1, 2, 3]

# fetch transfers that meets criteria from wallet
transfers: list[MoneroTransferWallet] = wallet.get_transfers(query)

# print fetched txs
for transfer in transfers:
    print(f"Found transfer: {transfer.serialize()}")
```

