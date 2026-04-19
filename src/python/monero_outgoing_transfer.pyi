import typing

from .monero_transfer import MoneroTransfer
from .monero_destination import MoneroDestination


class MoneroOutgoingTransfer(MoneroTransfer):
    """Models an outgoing transfer of funds from the wallet."""

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
        """
        Copy current outgoing transfer.

        :returns MoneroOutgoingTransfer: outgoing transfer copy.
        """
        ...

    @typing.overload
    def merge(self, other: MoneroOutgoingTransfer) -> None:
        """
        Merge current outgoing transfer with another one.

        :param MoneroOutgoingTransfer other: other outgoing transfer to merge with.
        """
        ...

    @typing.overload
    def merge(self, other: MoneroTransfer) -> None:
        """
        Merge current outgoing transfer with another transfer.

        :param MoneroOutgoingTransfer other: other transfer to merge with.
        """
        ...
