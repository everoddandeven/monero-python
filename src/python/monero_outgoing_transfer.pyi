import typing

from .monero_transfer import MoneroTransfer
from .monero_destination import MoneroDestination


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
    @typing.override
    def copy(self) -> MoneroOutgoingTransfer:
        ...
    @typing.overload
    def merge(self, other: MoneroOutgoingTransfer) -> None:
        ...
    @typing.overload
    def merge(self, other: MoneroTransfer) -> None:
        ...
