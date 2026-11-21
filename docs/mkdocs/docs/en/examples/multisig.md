---
title: Multisig Wallets
---
# Multisig Wallets

A multisig wallet is shared by N participants, and spends only with the signatures of M of them: a 2/3 wallet has three participants,
any two of which spend. Each participant has a wallet of their own, [full](../api/wallet_full.md) or [RPC](../api/wallet_rpc.md),
made multisig together with the others. The wallets exchange hex strings, which each participant passes to the others, by any channel.

The code below runs every participant in one place, to show what each one sends and receives: in practice each part runs on the
machine of its participant.

## Making the wallet

Each participant starts from a new, empty wallet:

```python
from monero import MoneroMultisigInitResult, MoneroWallet


def make_multisig(participants: list[MoneroWallet], m: int, password: str) -> str:
    """Makes the wallets of the participants one m/n multisig wallet, and returns its address."""
    n = len(participants)

    # 1. each participant prepares its wallet, and sends the result to the others
    prepared = [wallet.prepare_multisig() for wallet in participants]

    # 2. each one makes its wallet multisig with what the others sent
    made: list[str] = []
    for i, wallet in enumerate(participants):
        peers = [h for j, h in enumerate(prepared) if j != i]
        made.append(wallet.make_multisig(peers, m, password))

    # 3. n - m + 1 rounds of exchanges of keys: the last one gives the address of the wallet
    address: str | None = None
    hexes = made
    for _ in range(n - m + 1):
        results: list[MoneroMultisigInitResult] = []
        for i, wallet in enumerate(participants):
            peers = [h for j, h in enumerate(hexes) if j != i]
            results.append(wallet.exchange_multisig_keys(peers, password))
        address = results[0].address
        hexes = [result.multisig_hex or "" for result in results]

    assert address is not None
    return address
```

After it, [`get_multisig_info`][monero.MoneroWallet.get_multisig_info] of each wallet says `is_ready`, with its threshold and its number of
participants, and every wallet has the same primary address: the one that receives the funds.

## Spending

A multisig wallet does not know which of its outputs are spent until the participants share what they know: before creating a
transaction, each one exports its multisig info and imports the one of the others.

```python
from monero import MoneroTxConfig, MoneroWallet


def share_multisig_info(participants: list[MoneroWallet]) -> None:
    for wallet in participants:
        wallet.sync()
    exported = [wallet.export_multisig_hex() for wallet in participants]
    for i, wallet in enumerate(participants):
        wallet.import_multisig_hex([h for j, h in enumerate(exported) if j != i])


def send(participants: list[MoneroWallet], m: int, address: str, amount: int) -> list[str]:
    share_multisig_info(participants)

    # one participant creates the transaction, which is not signed enough to be relayed
    config = MoneroTxConfig()
    config.address = address
    config.amount = amount
    tx = participants[0].create_tx(config)
    assert tx.tx_set is not None and tx.tx_set.multisig_tx_hex is not None
    tx_hex: str = tx.tx_set.multisig_tx_hex

    # m - 1 others sign it, one after the other
    for wallet in participants[1:m]:
        signed = wallet.sign_multisig_tx_hex(tx_hex)
        assert signed.signed_multisig_tx_hex is not None
        tx_hex = signed.signed_multisig_tx_hex

    # and any of them submits it: the hashes of the transactions relayed
    return participants[0].submit_multisig_tx_hex(tx_hex)
```

[`describe_multisig_tx_set`][monero.MoneroWallet.describe_multisig_tx_set] shows what a transaction to sign pays, before signing it.
[`is_multisig_import_needed`][monero.MoneroWallet.is_multisig_import_needed] says when a wallet needs the info of the others again: after
it receives or spends.
