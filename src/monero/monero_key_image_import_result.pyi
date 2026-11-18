from .serializable_struct import SerializableStruct


class MoneroKeyImageImportResult(SerializableStruct):
    """Models results from importing key images."""

    height: int | None
    """Height at which the last key image was imported. Can be `0` if blockchain height is not known."""
    spent_amount: int | None
    """Amount (in atomic-units) spent from those key images."""
    unspent_amount: int | None
    """Amount (in atomic-units) still available from those key images."""

    @staticmethod
    def deserialize(json: str) -> MoneroKeyImageImportResult:
        """
        Deserialize a MoneroKeyImageImportResult from a JSON string.

        :param str json: MoneroKeyImageImportResult in JSON format.
        :returns MoneroKeyImageImportResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero key image import result."""
        ...
