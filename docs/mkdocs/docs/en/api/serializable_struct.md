
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

Two objects of the same class are equal if they serialize the same, without their back references, and they are not hashable. Their
`repr` is their class with their JSON. [Equality and Identity](equality.md) says how `==` and `is` work on the model, and how they
differ from monero-java.

::: monero.SerializableStruct
