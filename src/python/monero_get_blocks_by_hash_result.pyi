from .serializable_struct import SerializableStruct
from .monero_block import MoneroBlock


class MoneroGetBlocksByHashResult(SerializableStruct):
    """Models the result of getting blocks by hash."""

    blocks: list[MoneroBlock]
    """The retrieved blocks."""
    current_height: int | None
    """The daemon's chain height at request time."""

    @staticmethod
    def deserialize(json: str) -> MoneroGetBlocksByHashResult:
        """
        Deserialize a MoneroGetBlocksByHashResult from a JSON string.

        :param str json: MoneroGetBlocksByHashResult in JSON format.
        :returns MoneroGetBlocksByHashResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero get blocks by hash result."""
        ...
