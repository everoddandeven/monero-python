from .serializable_struct import SerializableStruct
from .monero_key_image import MoneroKeyImage
from .monero_tx import MoneroTx


class MoneroOutput(SerializableStruct):
    """Models a Monero transaction output."""

    amount: int | None
    """Output amount in atomic-units."""
    index: int | None
    """Output index."""
    key_image: MoneroKeyImage | None
    """The key image of the output."""
    mask: str | None
    """The output commitment mask (pseudo-out blinding factor) as a hex string."""
    ring_output_indices: list[int]
    """Indices of ring outputs."""
    stealth_public_key: str | None
    """The public key of the output."""
    tx: MoneroTx
    """The transaction related to this output."""

    @staticmethod
    def deserialize(json: str) -> MoneroOutput:
        """
        Deserialize a MoneroOutput from a JSON string.

        :param str json: MoneroOutput in JSON format.
        :returns MoneroOutput: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero output."""
        ...

    def copy(self) -> MoneroOutput:
        """
        Copy current output.

        :returns MoneroOutput: output copy.
        """
        ...

    def merge(self, other: MoneroOutput) -> None:
        """
        Merge current output wallet with another output.

        :param MoneroOutput other: other output to merge with.
        """
        ...
