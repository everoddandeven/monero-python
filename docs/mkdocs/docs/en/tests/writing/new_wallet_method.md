---
title: A New Wallet Method
---
# A New Wallet Method

A method added to `MoneroWallet`, in the bindings and in its stub `src/monero/monero_wallet.pyi`, needs two more things, or
`tests/wallet/test_support.py` fails:

1. A call of it in `WALLET_CALLS` of `tests/utils/wallet_calls.py`, one for each overload, with arguments of the right types:
    ```python
    WalletCall("get_tx", "tx_hash", lambda w: w.get_tx("")),
    ```
    `tests/wallet/test_interface.py` makes it on `MoneroWallet`, where it has to raise "not supported", and `test_support.py` on
    each wallet type. Two flags are for the calls that are different: `in_base=True` when `MoneroWallet` implements it on top of its
    other methods, `waits=True` when a wallet that implements it waits on the network, as `wait_for_next_block`.
2. A row in `tests/wallet/wallet_support.yml`, in its section, with the support of each wallet type:
    ```yaml
    get_tx: {full: supported, rpc: supported, keys: unsupported}
    ```
    The states are `supported`, `partial` (with a `note` that says which overloads), `todo` and `unsupported`. The test calls the
    method on a full wallet with no daemon, an rpc wallet with no server and a keys-only wallet, and fails when the row says
    otherwise. It tells implemented from not, `todo` and `unsupported` are the choice of the row.

The row is what the [Wallet Support](../../api/wallet_support.md) page shows.
