---
title: Glossary
---
# Glossary

The words of Monero that the API uses, and what they are in it.

## Amounts

Every amount of the API, a balance, the amount of a transfer or of an output, a fee, is an `int` of **atomic units**, the piconero:
1 XMR is 10¹² atomic units. [`MoneroUtils`][monero.MoneroUtils] converts between the two:

```python
from monero import MoneroUtils

amount: int = MoneroUtils.xmr_to_atomic_units(0.25)     # 250000000000
xmr: float = MoneroUtils.atomic_units_to_xmr(amount)    # 0.25
```

A `float` of XMR is for showing an amount, not for computing with it: the arithmetic of amounts is the one of the `int`.

## Networks

| Network | What it is | Port of the RPC of the daemon | Port of its peers |
| --- | --- | --- | --- |
| mainnet | the network of the real XMR | 18081 | 18080 |
| stagenet | a network for testing, with the same rules as mainnet, and coins of no value | 38081 | 38080 |
| testnet | a network for testing the rules of the next version of monero | 28081 | 28080 |

The network is [`MoneroNetworkType`][monero.MoneroNetworkType], and a wallet is of one of them: an address of one network is not
valid on another. **regtest** is a daemon of mainnet started with `--regtest`, with a chain of its own and blocks mined on demand: the
[network of the tests](../tests/environment/network.md) is one.

`monero-wallet-rpc` has no port of its own: it takes the one of `--rpc-bind-port`.

## Keys and addresses

| Term | What it is |
| --- | --- |
| seed | the 25 words that the keys of a wallet are made from: a wallet restored from it is the same wallet. `seed_offset` is a passphrase that changes the keys made from the seed |
| private spend key | the key that spends the outputs of the wallet |
| private view key | the key that finds the outputs of the wallet on the chain, and their amounts |
| view-only wallet | a wallet with the view key and no spend key: it sees what it receives, and can not spend it ([`is_view_only`][monero.MoneroWallet.is_view_only]) |
| primary address | the address of the keys, the first one of the wallet: account 0, subaddress 0 |
| account | a group of subaddresses with a balance of its own, by index: 0 is the first one |
| subaddress | an address of an account, by index: `get_address(account_index, subaddress_index)`. Payments to different subaddresses can not be linked to one another on the chain |
| integrated address | an address with a payment ID in it, which tells the receiver what a payment is for ([`MoneroIntegratedAddress`][monero.MoneroIntegratedAddress]) |

## Transactions

| Term | What it is |
| --- | --- |
| output | an amount received by the wallet, which a later transaction spends whole: what is left goes back to the wallet as a new output, the change |
| key image | the mark that a spent output leaves on the chain, the same for the same output: a daemon knows by it whether an output is spent, without knowing which output it is |
| transfer | what a transaction moves for the wallet: an incoming transfer to one of its subaddresses, an outgoing transfer from one of its accounts |
| pool | the transactions that a daemon knows and that are not in a block yet |
| relay | sending a transaction to the network. A transaction created with `relay = False` in its [`MoneroTxConfig`][monero.MoneroTxConfig] is only created: its fee can be shown before [`relay_tx`][monero.MoneroWallet.relay_tx] sends it |
| locked | an output received can not be spent for 10 blocks, about 20 minutes, and an output of mining for 60: the **balance** counts it, the **unlocked balance** does not yet |
| restore height | the height that a restored wallet syncs from: the blocks before it are not looked at, a payment received in them is not seen |
| trusted daemon | a daemon that the wallet trusts, its own: some operations need one, such as [`rescan_spent`][monero.MoneroWallet.rescan_spent] and [`start_mining`][monero.MoneroWallet.start_mining] |
