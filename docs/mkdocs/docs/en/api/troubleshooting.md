---
title: Troubleshooting
---
# Troubleshooting

What goes wrong most often, what it means, and what to do. The [log of monero](utils.md#logging) says more on what the wallet did.

## Installing and importing

| What happens | Why | What to do |
| --- | --- | --- |
| `pip`: *is not a supported wheel on this platform* | the wheel is built for another version of Python, the one of its name (`cp313` is 3.13) | install it with that Python, in a virtual environment of it ([Installation](../getting_started/installation.md#which-file)) |
| `import monero` imports another library | the `monero` package of PyPI is another project, with the same name | uninstall it from the environment ([Installation](../getting_started/installation.md#the-other-monero-package)) |
| `ModuleNotFoundError: No module named 'monero'` with a module built from source | the folder of the built module is not on the path | `pip install .`, or `PYTHONPATH` set to the folder with `monero.cpython-*.so` |

## Connecting

| What happens | Why | What to do |
| --- | --- | --- |
| `Network error: no response from http://.../json_rpc (timeout: 180000ms)` | the server is not at that address or port, or it does not answer in 3 minutes | check the URI and the port of the network ([Glossary](glossary.md#networks)); `timeout_ms` of the [connection](connection.md) waits less, or more |
| the connection is refused for its credentials | the server has `--rpc-login`, and the connection has another one, or none | the same `username` and `password` ([RPC Connection](connection.md)) |
| a call of the daemon is refused, the others work | a public node runs with `--restricted-rpc`, which refuses what administers the daemon | a daemon of your own ([Daemon Interface](daemon.md)) |

## Creating and opening wallets

| What happens | Why | What to do |
| --- | --- | --- |
| `Must provide wallet network type` | the config has no `network_type` | set it: mainnet, stagenet or testnet |
| `Network type must be mainnet when using regtest option` | a regtest wallet has the addresses of mainnet | `network_type = MAINNET` with `regtest = True` ([Developing on Regtest](../examples/scenarios/developing_on_regtest.md)) |
| `Wallet already exists: <path>` | there is a wallet at that path | open it, or choose another path |
| `Cannot specify restore height when creating random wallet` | a new wallet has no past to look in | no `restore_height`: it starts from the height of the daemon |
| `get_height() not supported`, and the like | the wallet type does not have that method | another wallet type ([Wallet Support](wallet_support.md)) |

## Balances and payments

| What happens | Why | What to do |
| --- | --- | --- |
| a restored wallet shows a balance of 0 | it is not synced yet, or its `restore_height` is after its payments | `sync()`; restore from an earlier height ([Backup and Recovery](../examples/scenarios/backup_and_recovery.md)) |
| a payment is seen, and the balance does not count it | it is in the pool: the balance counts a payment from its first block | wait for a block |
| the balance counts a payment, and it can not be spent | it is locked: 10 blocks after its block, or until its `unlock_time` | [When an output can be spent](glossary.md#when-an-output-can-be-spent) |
| a payment does not show at all | the wallet missed it, or it went to another network | [`scan_txs`][monero.MoneroWallet.scan_txs] with its hash |
| a transaction can not be created for the money | the unlocked balance of the account is less than the amount and the fee | wait for the locked outputs, or send less |

## Python

| What happens | Why | What to do |
| --- | --- | --- |
| the memory of a long-running application grows | the transactions, transfers and outputs that it got are never freed | [`MoneroUtils.free`][monero.MoneroUtils.free] once done with them ([Memory](architecture.md#memory)) |
| `output.tx` is `None` in an output that a listener kept | the wallet freed it after calling the listener | copy what is needed in the listener ([Listening to a Wallet](../examples/basics/listening_to_a_wallet.md)) |
| an exception raised in a listener is never seen | the wallet calls the listener from its own thread, and logs the error | catch it in the listener |
| `except MoneroError` does not catch an error | that call still raises a `RuntimeError` | `except RuntimeError` catches both ([Errors](errors.md)) |
