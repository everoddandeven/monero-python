from .serializable_struct import SerializableStruct
from .monero_key_image import MoneroKeyImage
from .monero_tx import MoneroTx


class MoneroOutput(SerializableStruct):
    """
    Models a Monero transaction output.
    """
    amount: int | None
    index: int | None
    key_image: MoneroKeyImage | None
    ring_output_indices: list[int]
    stealth_public_key: str | None
    tx: MoneroTx
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutput:
        ...
    def merge(self, _self: MoneroOutput, other: MoneroOutput) -> None:
        ...
