import typing

from .serializable_struct import SerializableStruct


class MoneroSyncResult(SerializableStruct):
    """
    Models a result of syncing a wallet.
    """
    num_blocks_fetched: int
    """Number of blocks fetched."""
    received_money: bool
    """Indicates if money was received."""
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, num_blocks_fetched: int, received_money: bool) -> None:
        ...
