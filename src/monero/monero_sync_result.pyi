import typing

from .serializable_struct import SerializableStruct


class MoneroSyncResult(SerializableStruct):
    """Models a result of syncing a wallet."""

    num_blocks_fetched: int
    """Number of blocks fetched."""
    received_money: bool
    """Indicates if money was received."""

    @staticmethod
    def deserialize(json: str) -> MoneroSyncResult:
        """
        Deserialize a MoneroSyncResult from a JSON string.

        :param str json: MoneroSyncResult in JSON format.
        :returns MoneroSyncResult: deserialized instance.
        """
        ...

    @typing.overload
    def __init__(self) -> None:
        """Initialize a Monero sync result."""
        ...

    @typing.overload
    def __init__(self, num_blocks_fetched: int, received_money: bool) -> None:
        """
        Initialize a Monero sync result.

        :param int num_blocks_fetched: Number of blocks fetched.
        :param bool received_money: Indicates if wallet receveid money during last sync.
        """
        ...
