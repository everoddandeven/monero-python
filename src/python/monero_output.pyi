from .serializable_struct import SerializableStruct
from .monero_key_image import MoneroKeyImage
from .monero_tx import MoneroTx


class MoneroOutput(SerializableStruct):
    """
    Models a Monero transaction output.
    """
    amount: int | None
    """Output amount in atomi-units."""
    index: int | None
    """Output"""
    key_image: MoneroKeyImage | None
    """The key image of the output."""
    ring_output_indices: list[int]
    """Indices of ring outputs."""
    stealth_public_key: str | None
    """The public key of the output."""
    tx: MoneroTx
    """The transaction related to this output."""
    def __init__(self) -> None:
        """Initialize a Monero output."""
        ...
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutput:
        ...
    def merge(self, _self: MoneroOutput, other: MoneroOutput) -> None:
        ...
