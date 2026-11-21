---
title: Escrow with a 2-of-3 Multisig
---
# Escrow with a 2-of-3 Multisig

A buyer pays a seller for goods that arrive later. Neither wants to go first: the buyer does not want to pay for what may not arrive,
the seller does not want to ship what may not be paid. An arbiter that both trust settles it, without holding the money alone.

The three make a 2-of-3 multisig wallet together, and the buyer pays into it. The money leaves it only with the signatures of two of the
three:

| What happens | Who signs | Where the money goes |
| --- | --- | --- |
| the goods arrive | the buyer and the seller | to the seller |
| the sale is cancelled | the buyer and the seller | back to the buyer |
| they disagree | the arbiter, with the one that it agrees with | to the one that the arbiter decides |

The arbiter alone can not take the money, nor can either party. Each of the three has a wallet of their own, on their own machine; the
code below runs them in one place, to show what each one sends to the others.

## Making the escrow wallet

Each party starts from a new, empty wallet, and runs the steps of [Multisig Wallets](../basics/multisig.md):

```python
from monero import MoneroMultisigInitResult, MoneroWallet

PASSWORD = "supersecretpassword123"


def make_escrow(buyer: MoneroWallet, seller: MoneroWallet, arbiter: MoneroWallet) -> str:
    """Makes the three wallets one 2-of-3 multisig wallet, and returns the address that the buyer pays."""
    parties = [buyer, seller, arbiter]
    prepared = [wallet.prepare_multisig() for wallet in parties]
    made = [wallet.make_multisig([h for j, h in enumerate(prepared) if j != i], 2, PASSWORD) for i, wallet in enumerate(parties)]

    # 3 - 2 + 1 = 2 rounds of exchanges of keys
    hexes = made
    address: str | None = None
    for _ in range(2):
        results: list[MoneroMultisigInitResult] = [
            wallet.exchange_multisig_keys([h for j, h in enumerate(hexes) if j != i], PASSWORD) for i, wallet in enumerate(parties)
        ]
        address = results[0].address
        hexes = [result.multisig_hex or "" for result in results]
    assert address is not None
    return address
```

The buyer checks that every party got the same address, and pays the price to it, from a wallet of their own. Its outputs can be spent
after 10 confirmations.

## Settling

Two parties settle the escrow: one makes the transaction that sends everything to where the money goes, the other signs it, and either
one submits it. Before that, the two share what each one knows of the outputs of the wallet:

```python
from monero import MoneroTxConfig, MoneroWallet


def settle(creator: MoneroWallet, cosigner: MoneroWallet, to_address: str) -> list[str]:
    """Sends everything of the escrow wallet to an address, with the signatures of two of its parties."""
    # each of the two imports what the other knows of the outputs of the wallet
    for wallet in (creator, cosigner):
        wallet.sync()
    creator_info, cosigner_info = creator.export_multisig_hex(), cosigner.export_multisig_hex()
    creator.import_multisig_hex([cosigner_info])
    cosigner.import_multisig_hex([creator_info])

    # the creator makes the transaction: everything that is unlocked, to the address
    config = MoneroTxConfig()
    config.address = to_address
    config.account_index = 0     # the account that the buyer paid
    txs = creator.sweep_unlocked(config)
    tx_set = txs[0].tx_set
    assert tx_set is not None and tx_set.multisig_tx_hex is not None

    # the cosigner reads what it pays before signing it, and submits it
    described = cosigner.describe_multisig_tx_set(tx_set.multisig_tx_hex)
    for tx in described.txs:
        print(f"pays {tx.get_outgoing_amount()} with a fee of {tx.fee}")
    signed = cosigner.sign_multisig_tx_hex(tx_set.multisig_tx_hex)
    assert signed.signed_multisig_tx_hex is not None
    return cosigner.submit_multisig_tx_hex(signed.signed_multisig_tx_hex)
```

The cosigner reads the transaction before signing it: it is the moment to refuse one that does not pay what was agreed.

## The three endings

```python
from monero import MoneroWalletRpc

buyer = MoneroWalletRpc("http://localhost:38082", "rpc_user", "abc123")
seller = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
arbiter = MoneroWalletRpc("http://localhost:38084", "rpc_user", "abc123")
# each one opens or creates a new wallet for the escrow, on its server

escrow_address = make_escrow(buyer, seller, arbiter)

seller_address = "..."      # an address of a wallet of the seller, not of the escrow
buyer_address = "..."       # an address of a wallet of the buyer

# the goods arrived: the seller asks for the money, the buyer signs
settle(seller, buyer, seller_address)

# or the sale is cancelled: the buyer asks for it back, the seller signs
settle(buyer, seller, buyer_address)

# or they disagree, and the arbiter sides with the buyer: it makes the refund, the buyer signs
settle(arbiter, buyer, buyer_address)
```

Only one of the endings happens: once the escrow is swept, it is empty.
