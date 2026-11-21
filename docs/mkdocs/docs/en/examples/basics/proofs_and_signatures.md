---
title: Proofs and Signatures
---
# Proofs and Signatures

A wallet proves what the chain does not show to everybody: that it sent a payment, that it has funds, that an address is its own. Each
proof is a string that the wallet makes and that anyone checks, with a wallet of their own, without the keys of the first.

## Signing a message

A message signed with an address proves that whoever signed it has the keys of that address:

```python
from monero import MoneroMessageSignatureType, MoneroNetworkType, MoneroWalletConfig, MoneroWalletKeys

config = MoneroWalletConfig()
config.network_type = MoneroNetworkType.MAINNET
wallet = MoneroWalletKeys.create_wallet_random(config)

message = "I am the owner of this address"
signature = wallet.sign_message(message, MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY)

result = wallet.verify_message(message, wallet.get_primary_address(), signature)
print(result.is_good, result.signature_type)
```

[`sign_message`][monero.MoneroWallet.sign_message] signs with the spend key, or with the view key, which a view-only wallet has, and
with the address of the account and subaddress given. Signing and checking work offline: a [keys-only wallet](../../api/wallet_keys.md) does
both.

## Proving a payment

The receiver of a payment, or a third party, checks that a transaction sent an amount to an address with the key of the transaction,
which only its sender has:

```python
from monero import MoneroWalletRpc

sender = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
receiver = MoneroWalletRpc("http://localhost:38084", "rpc_user", "abc123")

tx_hash = "..."             # the hash of the transaction sent
address = "..."             # the address that it paid

tx_key = sender.get_tx_key(tx_hash)
check = receiver.check_tx_key(tx_hash, tx_key, address)
print(check.is_good, check.received_amount, check.num_confirmations)
```

A key gives away the payment for good. A **proof** is made for a message, and can be made again for another:

| Proof | Made with | Checked with | Proves |
| --- | --- | --- | --- |
| of a transaction | [`get_tx_proof`][monero.MoneroWallet.get_tx_proof] | [`check_tx_proof`][monero.MoneroWallet.check_tx_proof] | that the transaction paid the address, made by the sender or by the receiver |
| of a spend | [`get_spend_proof`][monero.MoneroWallet.get_spend_proof] | [`check_spend_proof`][monero.MoneroWallet.check_spend_proof] | that the wallet that signed it sent the transaction |
| of reserve | [`get_reserve_proof_wallet`][monero.MoneroWallet.get_reserve_proof_wallet], [`get_reserve_proof_account`][monero.MoneroWallet.get_reserve_proof_account] | [`check_reserve_proof`][monero.MoneroWallet.check_reserve_proof] | that the wallet, or one of its accounts, has at least an amount that is not spent |

```python
from monero import MoneroWalletRpc

wallet = MoneroWalletRpc("http://localhost:38083", "rpc_user", "abc123")
checker = MoneroWalletRpc("http://localhost:38084", "rpc_user", "abc123")

# a proof that the wallet has funds, for a message that says what it is for
signature = wallet.get_reserve_proof_wallet("reserves of 2026-11-21")
reserve = checker.check_reserve_proof(wallet.get_primary_address(), "reserves of 2026-11-21", signature)
print(reserve.is_good, reserve.total_amount, reserve.unconfirmed_spent_amount)
```

The proofs of transactions and of reserve need a wallet that is synced with a daemon to be checked: the [full](../../api/wallet_full.md)
or the [RPC](../../api/wallet_rpc.md) wallet ([Wallet Support](../../api/wallet_support.md)).
