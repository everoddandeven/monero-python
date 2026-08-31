from .serializable_struct import SerializableStruct


class MoneroCheck(SerializableStruct):
    """Base model for results from checking a transaction or reserve proof."""

    is_good: bool
    """Indicates if check was successfull."""

    @staticmethod
    def deserialize(json: str) -> MoneroCheck:
        """
        Deserialize a MoneroCheck from a JSON string.

        :param str json: MoneroCheck in JSON format.
        :returns MoneroCheck: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero check."""
        ...
