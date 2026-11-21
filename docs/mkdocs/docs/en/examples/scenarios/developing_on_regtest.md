---
title: Developing on Regtest
---
# Developing on Regtest

An application that moves money is tried before it moves real money. Stagenet is a public network for that, but its blocks come every
2 minutes, and its coins come from a faucet. **Regtest** is a chain of your own, on your machine: blocks are mined on demand, as many as
needed, and their coins are yours. The [tests of this library](../../tests/environment/network.md) run on it.

## The daemon

A daemon of mainnet started with `--regtest` has a chain of its own, which starts empty. `--fixed-difficulty` makes mining a block
instant, and `--offline` keeps it away from the real network:

```bash
monerod --regtest --offline --fixed-difficulty 1 \
    --rpc-bind-port 18081 --data-dir ./regtest
```

Its addresses are the ones of mainnet: a wallet for regtest has the network type `MAINNET`, and `regtest = True`.

## A wallet with coins

[`generate_blocks`][monero.MoneroDaemon.generate_blocks] mines blocks, and their rewards go to an address. A reward is locked for 60
blocks ([When an output can be spent](../../api/glossary.md#when-an-output-can-be-spent)): mining 60 more after it unlocks it.

```python
from monero import MoneroDaemonRpc, MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletFull

daemon = MoneroDaemonRpc("http://localhost:18081")

config = MoneroWalletConfig()
config.path = "regtest/miner"
config.password = "supersecretpassword123"
config.network_type = MoneroNetworkType.MAINNET
config.regtest = True
config.server = MoneroRpcConnection("http://localhost:18081")
miner = MoneroWalletFull.create_wallet(config)

daemon.generate_blocks(miner.get_primary_address(), 100)     # 100 rewards
daemon.generate_blocks(miner.get_primary_address(), 60)      # which unlock the first 100
miner.sync()
print(f"unlocked: {miner.get_unlocked_balance()}")
```

## Trying a payment

A second wallet receives, and a block mined on demand confirms the payment: a test of the application does in a second what takes 20
minutes on another network.

```python
from monero import MoneroTxConfig, MoneroUtils

config.path = "regtest/customer"
customer = MoneroWalletFull.create_wallet(config)

payment = MoneroTxConfig()
payment.address = customer.get_primary_address()
payment.amount = MoneroUtils.xmr_to_atomic_units(1.5)
payment.relay = True
tx = miner.create_tx(payment)

# the payment is in the pool: the wallet sees the transaction, the balance does not count it yet
customer.sync()
print(customer.get_tx(tx.hash or "") is not None, customer.get_balance())   # True, 0

# 1 block: it is confirmed, in the balance and locked
daemon.generate_blocks(miner.get_primary_address(), 1)
customer.sync()
print(customer.get_balance(), customer.get_unlocked_balance())              # 1.5 XMR, 0

# 9 more: 10 blocks on it, it is unlocked
daemon.generate_blocks(miner.get_primary_address(), 9)
customer.sync()
print(customer.get_unlocked_balance())                                      # 1.5 XMR
```

Each state of a payment, in the pool, confirmed, unlocked, is a number of blocks away: the code that handles each one is tried by mining
up to it. A chain that a test spoiled is thrown away with the folder of `--data-dir`.

## The network of the tests

The [docker network of the tests](../../tests/environment/network.md) is a ready regtest: two daemons that are peers, and three
`monero-wallet-rpc`, started with one command. An application can use it as it is, for its own tests.
