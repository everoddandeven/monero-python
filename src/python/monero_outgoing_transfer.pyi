import typing

from .monero_transfer import MoneroTransfer
from .monero_destination import MoneroDestination
from .monero_incoming_transfer import MoneroIncomingTransfer


class MoneroOutgoingTransfer(MoneroTransfer):
    """
    Models an outgoing transfer of funds from the wallet.
    """
    addresses: list[str]
    """Addresses from which the transfer originated."""
    destinations: list[MoneroDestination]
    """Outgoing transfer destinations."""
    subaddress_indices: list[int]
    """Subaddresses from which the transfer originated."""
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroOutgoingTransfer, tgt: MoneroIncomingTransfer) -> MoneroOutgoingTransfer:
        ...
    @typing.overload
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroOutgoingTransfer:
        ...
    @typing.overload
    def merge(self, _self: MoneroOutgoingTransfer, other: MoneroOutgoingTransfer) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
