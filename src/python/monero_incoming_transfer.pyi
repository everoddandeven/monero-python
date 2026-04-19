import typing

from .monero_transfer import MoneroTransfer


class MoneroIncomingTransfer(MoneroTransfer):
    """Models an incoming transfer of funds to the wallet."""

    address: str | None
    """The address that received funds within this transfer."""
    num_suggested_confirmations: int | None
    """The number of suggested confirmations before moving funds."""
    subaddress_index: int | None
    """The subaddress index that received funds within this transfer."""

    def __init__(self) -> None:
        """Initialize a Monero incoming transfer."""
        ...

    @typing.override
    def copy(self) -> MoneroIncomingTransfer:
        """
        Copy current incoming transfer.

        :returns MoneroIncomingTransfer: incoming transfer copy.
        """
        ...

    @typing.overload
    def merge(self, other: MoneroIncomingTransfer) -> None:
        """
        Merge current incoming transfer with another one.

        :param MoneroIncomingTransfer other: other incoming transfer to merge with.
        """
        ...

    @typing.overload
    def merge(self, other: MoneroTransfer) -> None:
        """
        Merge current incoming transfer with another transfer.

        :param MoneroTransfer other: other transfer to merge with.
        """
        ...
