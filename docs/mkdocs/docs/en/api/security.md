---
title: Security
---
# Security

What an application that holds or receives Monero has to take care of: the keys, the servers it talks to, what its network shows, what
it gives away, and what it accepts as paid.

## The seed and the keys

The seed is the wallet: whoever has the 25 words has the money, on any machine, now and later. The keys are made from it.

- **Keep the seed offline**: on paper, not in a file, a database, a log, an environment variable or a message. Code that prints
  `get_seed()` to see that it works writes it to wherever its output goes.
- A **`seed_offset`** is a passphrase added to the seed: the same words with another offset are another wallet. It protects a seed that
  is found, if the offset is kept elsewhere.
- **The spend key spends**, the view key only sees. A machine that must stay online, a shop, a server, holds a
  [view-only wallet](glossary.md#keys-and-addresses), and the spend key stays on one that is not
  ([Signing Offline with a Cold Wallet](../examples/scenarios/cold_signing.md)).
- Funds that no single person should move are a [multisig wallet](../examples/basics/multisig.md): no participant alone has the
  money.

## The files of a wallet

A full wallet writes `<path>.keys`, its keys, encrypted with its password, and `<path>`, its cache, encrypted with a key made from the
keys: neither is read without the password. A weak password is guessed by whoever copies the files, so the files are kept as a secret too, and the password is not written next to them.
[`change_password`][monero.MoneroWallet.change_password] changes it; the seed does not change.

A wallet in memory, without a `path`, writes no file: what [`get_keys_file_buffer`][monero.MoneroWalletFull.get_keys_file_buffer] gives
is the same secret, wherever the application puts it.

## The RPC servers

A `monerod` or a `monero-wallet-rpc` answers whoever reaches its port, and a wallet server spends for them:

| Setting | What it does |
| --- | --- |
| `--rpc-bind-ip` | the address that the server listens on: `127.0.0.1` by default, the machine alone. Another address needs `--confirm-external-bind`, and exposes the server to that network |
| `--rpc-login user:password` | the credentials that a request needs. A wallet server without them, with `--disable-rpc-login`, spends for anyone that reaches it |
| `--rpc-ssl` and its certificates | TLS on the RPC: the credentials and the answers do not travel in clear. The connection checks the certificate unless `ssl_verify` is off ([RPC Connection](connection.md)) |
| `--restricted-rpc` | a daemon that answers what reads the chain and refuses what administers it: the one to expose, if one is exposed |

A wallet server stays on the machine of the application, or behind a network that only the application reaches. The connection of a
wallet server to its daemon has its own TLS, the [`SslOptions`][monero.SslOptions] of
[`MoneroWalletRpc.set_daemon_connection`][monero.MoneroWalletRpc.set_daemon_connection].

## The daemon, and what it learns

A wallet asks a daemon for the blocks and the transactions, and sends its own through it. The daemon learns from the requests:

- the **IP address** of the wallet, and when it is online;
- the **transactions that it sends**, from that IP address, at the moment they are sent;
- part of what it looks for, from the outputs that a transaction asks for.

A daemon of your own learns nothing that you do not know. A remote node, of somebody else, learns the above: enough to link the
transactions sent from one IP address. The [`proxy_uri`](connection.md) of the connection sends the requests through Tor:

```python
from monero import MoneroRpcConnection

connection = MoneroRpcConnection("http://<onion address>.onion:18081")
connection.proxy_uri = "127.0.0.1:9050"     # the SOCKS of Tor
```

A wallet treats its daemon as **trusted** or not (`is_trusted_daemon` of the [config](data_model/wallet/inputs.md)): with an untrusted
one it refuses what would show the daemon which outputs are its own, such as
[`rescan_spent`][monero.MoneroWallet.rescan_spent]. Only a daemon of your own is trusted.

## What each proof gives away

| Given | Shows to whoever gets it |
| --- | --- |
| the private view key | every payment received by the wallet, with its amount, from now and from the past; with the key images, also what it spends |
| the key of a transaction, [`get_tx_key`][monero.MoneroWallet.get_tx_key] | that the transaction paid an address, and how much: to anyone, for good |
| a transaction proof, [`get_tx_proof`][monero.MoneroWallet.get_tx_proof] | the same, for its message only ([Proving a Payment in a Dispute](../examples/scenarios/payment_dispute.md)) |
| a reserve proof | the outputs that hold the amount, and their key images: when they are spent, from then on ([Proof of Reserves](../examples/scenarios/proof_of_reserves.md)) |
| a signed message | that the signer has the keys of the address, for that message |

## What counts as paid

A payment seen is not a payment that can be spent:

- **In the pool** it can still be replaced by a double spend: a payment counts once it has the confirmations that its amount deserves.
- **An `unlock_time`** can lock it for centuries, with all its confirmations: a payment counts only with an `unlock_time` of `0`
  ([When an output can be spent](glossary.md#when-an-output-can-be-spent)).
- **The address** that it went to is the one of the order, of the right network: a subaddress for each order tells them apart
  ([Accepting Payments in a Shop](../examples/scenarios/accepting_payments.md)).

## The logs

The log of monero writes hashes of transactions and amounts, and more at the higher [levels](utils/logging.md): a log is kept as
private as the wallet, and the level of production is the lowest that serves.

## The library

The packages of a release are attested by the workflow that built them, and listed in its `SHA256SUMS`: a download is checked before it
is installed ([Installation](../getting_started/installation.md#checking-the-download)). A vulnerability of the library is reported
privately, as [Contributing](../contributing/index.md) says.
