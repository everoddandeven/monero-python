import typing

from .monero_transfer import MoneroTransfer


class MoneroIncomingTransfer(MoneroTransfer):
    """
    Models an incoming transfer of funds to the wallet.
    """
    address: str | None
    num_suggested_confirmations: int | None
    subaddress_index: int | None
    def __init__(self) -> None:
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
