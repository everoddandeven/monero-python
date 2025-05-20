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
    change_amount: int | None
    extra_hex: str | None
    incoming_transfers: list[MoneroIncomingTransfer]
    input_sum: int | None
    is_incoming: bool | None
    is_locked: bool | None
    is_outgoing: bool | None
    note: str | None
    num_dummy_outputs: int | None
    outgoing_transfer: MoneroOutgoingTransfer | None
    output_sum: int | None
    tx_set: MoneroTxSet | None
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
