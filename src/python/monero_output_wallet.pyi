import typing

from .monero_output import MoneroOutput


class MoneroOutputWallet(MoneroOutput):
    """
    Models a Monero output with wallet extensions.
    """
    account_index: int | None
    """The index of the account that owns this output."""
    is_frozen: bool | None
    """Indicates if the output is frozen (`True`) or not (`False`)."""
    is_spent: bool | None
    """Indicates if the output is spent (`True`) or not (`False`)."""
    subaddress_index: int | None
    """The index of the subaddress that owns this output."""
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroOutputWallet, tgt: MoneroOutputWallet) -> MoneroOutputWallet:
        ...
    @typing.overload
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutputWallet:
        ...
    @typing.overload
    def merge(self, _self: MoneroOutputWallet, other: MoneroOutputWallet) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroOutput, other: MoneroOutput) -> None:
        ...
