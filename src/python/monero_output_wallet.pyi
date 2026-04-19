import typing

from .monero_output import MoneroOutput


class MoneroOutputWallet(MoneroOutput):
    """Models a Monero output with wallet extensions."""

    account_index: int | None
    """The index of the account that owns this output."""
    is_frozen: bool | None
    """Indicates if the output is frozen (`True`) or not (`False`)."""
    is_spent: bool | None
    """Indicates if the output is spent (`True`) or not (`False`)."""
    subaddress_index: int | None
    """The index of the subaddress that owns this output."""

    def __init__(self) -> None:
        """Initialize a Monero wallet output."""
        ...

    @typing.override
    def copy(self) -> MoneroOutputWallet:
        """
        Copy current output wallet.

        :returns MoneroOutputWallet: output wallet copy.
        """
        ...

    @typing.overload
    def merge(self, other: MoneroOutputWallet) -> None:
        """
        Merge current output wallet with another one.

        :param MoneroOutputWallet other: other output wallet to merge with.
        """
        ...

    @typing.overload
    def merge(self, other: MoneroOutput) -> None:
        """
        Merge current output wallet with another output.

        :param MoneroOutput other: other output to merge with.
        """
        ...
