import typing

from .monero_tx import MoneroTx
from .monero_incoming_transfer import MoneroIncomingTransfer
from .monero_outgoing_transfer import MoneroOutgoingTransfer
from .monero_tx_set import MoneroTxSet
from .monero_output_query import MoneroOutputQuery
from .monero_output_wallet import MoneroOutputWallet
from .monero_transfer import MoneroTransfer
from .monero_transfer_query import MoneroTransferQuery


class MoneroTxWallet(MoneroTx):
    """
    Models a Monero transaction in the context of a wallet.
    """
    change_address: str | None
    """Address to which the change amount of the transaction was sent."""
    change_amount: int | None
    """Change amount of the transaction."""
    extra_hex: str | None
    """Extra information about the transaction in hexadecimal format."""
    incoming_transfers: list[MoneroIncomingTransfer]
    """List of incoming transfer."""
    input_sum: int | None
    """Total input sum."""
    is_incoming: bool | None
    """Indicates if the transaction has incoming transfers."""
    is_locked: bool | None
    """Indicates if the transaction is locked."""
    is_outgoing: bool | None
    """Indicated if the transaction has outgoing transfer."""
    note: str | None
    """Transaction note."""
    num_dummy_outputs: int | None
    """Number of decoys of the transactions."""
    outgoing_transfer: MoneroOutgoingTransfer | None
    """The outgoing transfer related to this transaction."""
    output_sum: int | None
    """The total output amount sum originated from this transaction."""
    tx_set: MoneroTxSet | None
    """The transaction set"""
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroTxWallet, tgt: MoneroTxWallet) -> MoneroTxWallet:
        ...
    @typing.overload
    def copy(self, src: MoneroTx, tgt: MoneroTx) -> MoneroTxWallet:
        ...
    def filter_outputs_wallet(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        ...
    def filter_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        ...
    @typing.overload
    def get_outputs_wallet(self) -> list[MoneroOutputWallet]:
        ...
    @typing.overload
    def get_outputs_wallet(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        ...
    @typing.overload
    def get_transfers(self) -> list[MoneroTransfer]:
        ...
    @typing.overload
    def get_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        ...
    @typing.overload
    def merge(self, _self: MoneroTxWallet, tgt: MoneroTxWallet) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroTx, tgt: MoneroTx) -> None: # type: ignore
        ...
