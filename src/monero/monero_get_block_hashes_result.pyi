from .serializable_struct import SerializableStruct


class MoneroGetBlockHashesResult(SerializableStruct):
    """Models the result of getting block hashes."""

    hashes: list[str]
    """The requested block hashes, starting at (and including) the last block in common with the request."""
    start_height: int | None
    """The height of the first hash in `hashes`."""
    current_height: int | None
    """The daemon's chain height at request time."""

    @staticmethod
    def deserialize(json: str) -> MoneroGetBlockHashesResult:
        """
        Deserialize a MoneroGetBlockHashesResult from a JSON string.

        :param str json: MoneroGetBlockHashesResult in JSON format.
        :returns MoneroGetBlockHashesResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero get block hashes result."""
        ...
