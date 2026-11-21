---
title: Signing Offline with a Cold Wallet
---
# Signing Offline with a Cold Wallet

The spend key is the money: whoever has it spends. A cold wallet keeps it on a machine that is never online, and the wallet that is
online has only the view key:

| Wallet | Where | Has | Does |
| --- | --- | --- | --- |
| online, view-only | a machine on the network, with a daemon | the address and the view key | syncs, sees the payments, prepares the transactions |
| offline, cold | a machine that is never online | the seed, with the spend key | signs the transactions |

What passes between the two are hex strings, carried by hand: a USB stick, a QR code. None of them has the spend key.

## Once: the two wallets

The cold wallet is created, or restored from its seed, on the offline machine, without a daemon. Its address and view key make the
view-only wallet on the online one:

```python
from monero import MoneroNetworkType, MoneroRpcConnection, MoneroWalletConfig, MoneroWalletFull

# on the offline machine
cold_config = MoneroWalletConfig()
cold_config.path = "wallets/cold"
cold_config.password = "supersecretpassword123"
cold_config.network_type = MoneroNetworkType.STAGENET
cold_config.seed = "...the 25 words..."
cold = MoneroWalletFull.create_wallet(cold_config)
print(cold.get_primary_address(), cold.get_private_view_key())      # copy them to the online machine

# on the online machine
online_config = MoneroWalletConfig()
online_config.path = "wallets/view_only"
online_config.password = "supersecretpassword123"
online_config.network_type = MoneroNetworkType.STAGENET
online_config.server = MoneroRpcConnection("http://localhost:38081")
online_config.primary_address = "..."       # the address of the cold wallet
online_config.private_view_key = "..."      # and its view key
online_config.restore_height = 1500000      # before its first payment
online = MoneroWalletFull.create_wallet(online_config)
assert online.is_view_only()
```

## Each payment

### 1. Online: the outputs

The view-only wallet syncs, and exports the outputs that it found. The cold wallet needs them to sign: it sees no chain.

```python
online.sync()
outputs_hex: str = online.export_outputs()
# carry outputs_hex to the offline machine
```

### 2. Offline: the key images

The cold wallet imports the outputs, and exports their key images, which only the spend key makes. With them the view-only wallet knows
which outputs are spent, and its balance is right:

```python
cold.import_outputs(outputs_hex)
key_images_json: str = cold.export_key_images().serialize()
# carry key_images_json back to the online machine
```

```python
from monero import MoneroKeyImageExportResult

key_images = MoneroKeyImageExportResult.deserialize(key_images_json).key_images
online.import_key_images(key_images)
print(online.get_balance(), online.get_unlocked_balance())
```

### 3. Online: the unsigned transaction

The view-only wallet makes the transaction, which it can not sign:

```python
from monero import MoneroTxConfig

config = MoneroTxConfig()
config.address = "..."                      # where the payment goes
config.amount = 250000000000                # 0.25 XMR
unsigned = online.create_tx(config)
assert unsigned.tx_set is not None and unsigned.tx_set.unsigned_tx_hex is not None
unsigned_tx_hex: str = unsigned.tx_set.unsigned_tx_hex
# carry unsigned_tx_hex to the offline machine
```

### 4. Offline: reading and signing it

The cold wallet shows what the transaction pays, before it signs: a compromised online machine could have made it pay somebody else.

```python
described = cold.describe_unsigned_tx_set(unsigned_tx_hex)
for tx in described.txs:
    assert tx.outgoing_transfer is not None
    for destination in tx.outgoing_transfer.destinations:
        print(f"pays {destination.amount} to {destination.address}, fee {tx.fee}")

signed = cold.sign_txs(unsigned_tx_hex)
assert signed.signed_tx_hex is not None
signed_tx_hex: str = signed.signed_tx_hex
# carry signed_tx_hex back to the online machine
```

### 5. Online: submitting it

```python
tx_hashes: list[str] = online.submit_txs(signed_tx_hex)
print(f"sent: {tx_hashes}")
```

Before the next payment, the steps 1 and 2 again: the view-only wallet learns of the change of this one, and that its inputs are spent.
