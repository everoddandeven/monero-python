import typing

from .monero_transfer import MoneroTransfer


class MoneroIncomingTransfer(MoneroTransfer):
    """
    Models an incoming transfer of funds to the wallet.
    """
    address: str | None
    """The address that received funds within this transfer."""
    num_suggested_confirmations: int | None
    """The number of suggested confirmations before moving funds."""
    subaddress_index: int | None
    """The subaddress index that received funds within this transfer."""
    def __init__(self) -> None:
        """Initialize a Monero incoming transfer."""
        ...
    @typing.overload
    def copy(self, src: MoneroIncomingTransfer, tgt: MoneroIncomingTransfer) -> MoneroIncomingTransfer:
        ...
    @typing.overload
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroIncomingTransfer:
        ...
    @typing.overload
    def merge(self, _self: MoneroIncomingTransfer, other: MoneroIncomingTransfer) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
