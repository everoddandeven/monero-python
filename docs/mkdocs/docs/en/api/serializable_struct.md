
---
title: Serializable Struct
---
# Serializable Struct

Every class of the [data model](architecture.md#the-data-model) extends [`SerializableStruct`][monero.SerializableStruct]:
[`serialize`][monero.SerializableStruct.serialize] turns an object into JSON, with the names of monero-java (`keyImages`, `isConfirmed`),
and the `deserialize` of each class makes it again:

```python
from monero import MoneroKeyImageExportResult

def carry(result: MoneroKeyImageExportResult) -> MoneroKeyImageExportResult:
    json: str = result.serialize()                          # to a file, a QR code, another process
    return MoneroKeyImageExportResult.deserialize(json)
```

It is how an object goes from a process or a machine to another ([Signing Offline with a Cold Wallet](../examples/scenarios/cold_signing.md)).

Two objects of the same class are equal if they serialize the same, so `==` compares what they hold and not whether they are the
same object. Like with monero-java, the back references are left out: a tx does not compare its block, an output its tx. The
objects can be changed, so they are not hashable: they can not be keys of a `dict` or go in a `set`.

```python
assert wallet.get_tx(tx_hash) == wallet.get_tx(tx_hash)  # two objects, equal
print(repr(tx))                                          # MoneroTxWallet({"hash":"...",...})
```

The `repr` of an object is its class with its JSON. [`MoneroRpcConnection`][monero.MoneroRpcConnection] and
[`MoneroWalletConfig`][monero.MoneroWalletConfig] hide their password, seed and private keys there, while `serialize()` keeps
them. A connection equals another with the same uri, credentials, proxy, zmq uri and ssl verify, whatever its priority, its timeout
or its state.

::: monero.SerializableStruct
