
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

::: monero.SerializableStruct
