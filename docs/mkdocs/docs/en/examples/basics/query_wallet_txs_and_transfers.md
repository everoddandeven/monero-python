---
title: Query Wallet Txs and Transfers
---
# Query Wallet Txs and Transfers

A wallet returns its transactions, transfers and outputs from what it synced, with a query that selects them:

* ```MoneroWallet.get_txs(query: MoneroTxQuery) -> list[MoneroTxWallet]```
* ```MoneroWallet.get_transfers(query: MoneroTransferQuery) -> list[MoneroTransfer]```
* ```MoneroWallet.get_outputs(query: MoneroOutputQuery) -> list[MoneroOutputWallet]```

A query is the class that it selects with the fields to match: what does not match every field set is left out, and a field not set
matches anything ([Wallet Data Model](../../api/data_model/wallet.md#what-a-call-takes)).

Example of fetching wallet txs with a basic `MoneroTxQuery`:

```python
from monero import (
    MoneroWalletRpc, MoneroTxQuery,
    MoneroTxWallet
)

# open a wallet with txs data
wallet = MoneroWalletRpc("http://wallet_rpc_uri:18083")
wallet.open_wallet("wallet_name", "wallet_password")

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

# fetch the txs that match the query
txs: list[MoneroTxWallet] = wallet.get_txs(query)

# print fetched txs
for tx in txs:
    print(f"Found tx: {tx.serialize()}")
```

Example of fetching wallet transfers with a `MoneroTransferQuery`:

```python
from monero import (
    MoneroWalletRpc, MoneroTransferQuery,
    MoneroTransfer
)

# open a wallet with txs data
wallet = MoneroWalletRpc("http://wallet_rpc_uri:18083")
wallet.open_wallet("wallet_name", "wallet_password")

# create and setup a new transfer query
query = MoneroTransferQuery()

# fetch only incoming transfers
query.incoming = True

# filter by account and subaddress index
query.account_index = 1
query.subaddress_indices = [0, 1, 2, 3]

# fetch the transfers that match the query
transfers: list[MoneroTransfer] = wallet.get_transfers(query)

# print fetched txs
for transfer in transfers:
    print(f"Found transfer: {transfer.serialize()}")
```

Example of fetching the outputs of the wallet with a `MoneroOutputQuery`, the ones that it can spend:

```python
from monero import MoneroOutputQuery, MoneroOutputWallet, MoneroUtils

query = MoneroOutputQuery()
query.is_spent = False
query.is_frozen = False
query.account_index = 0

outputs: list[MoneroOutputWallet] = wallet.get_outputs(query)
for output in outputs:
    print(f"output of {output.amount} in {output.tx.hash}, subaddress {output.subaddress_index}")

# an application that runs for long frees what it got, once done with it
MoneroUtils.free(outputs)
```

[`MoneroUtils.free`][monero.MoneroUtils.free] matters in an application that queries again and again: [Memory](../../api/architecture.md#memory).
