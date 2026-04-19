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
    """Models a Monero transaction in the context of a wallet."""

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
    """Set of transactions related to current tx."""
    def __init__(self) -> None:
        """Initialize a new Monero tx wallet."""
        ...
    @typing.override
    def copy(self) -> MoneroTxWallet:
        """
        Copy current tx wallet.

        :returns MoneroTxWallet: tx wallet copy.
        """
        ...
    def filter_outputs_wallet(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        """
        Get outputs filtered by query.

        :param MoneroOutputQuery query: query to filter outputs with.
        :returns list[MoneroOutputWallet]: outputs that meets all criteria defined in `query`.
        """
        ...
    def filter_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        """
        Get transfers filtered by query.

        :param MoneroTransferQuery query: query to filter transfers with.
        :returns list[MoneroTransfer]: transfers that meets all criteria defined in `query`.
        """
        ...
    @typing.overload
    def get_outputs_wallet(self) -> list[MoneroOutputWallet]:
        """
        Get wallet outputs from current wallet tx.

        :returns list[MoneroOutputWallet]: wallet outputs defined in current tx.
        """
        ...
    @typing.overload
    def get_outputs_wallet(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        """
        Get wallet outputs filtered by query.

        :params MoneroOutputQuery query: query to filter outputs with.
        :returns list[MoneroOutputWallet]: wallet outputs filtered by query.
        """
        ...
    def get_inputs_wallet(self, query: MoneroOutputQuery | None = None) -> list[MoneroOutputWallet]:
        """
        Get wallet inputs filtered by query.

        :params MoneroOutputQuery query: query to filter outputs with.
        :returns list[MoneroOutputWallet]: wallet outputs filtered by query.
        """
        ...
    @typing.overload
    def get_transfers(self) -> list[MoneroTransfer]:
        """
        Get all transfers defined in current wallet tx.

        :returns list[MoneroTransfer]: transfers from tx.
        """
        ...
    @typing.overload
    def get_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        """
        Get wallet transfers filtered by query.

        :params MoneroTransferQuery query: query to filter transfers with.
        :returns list[MoneroTransfer]: wallet transfers filtered by query.
        """
        ...
    def get_incoming_amount(self) -> int:
        """
        Get total amount received in current tx.

        :returns int: total amount received in current wallet tx.
        """
        ...
    def get_outgoing_amount(self) -> int:
        """
        Get total amount spent in current tx.

        :returns int: total amount spent in current wallet tx.
        """
        ...
    @typing.overload
    def merge(self, tgt: MoneroTxWallet) -> None:
        """
        Merge current wallet tx with another one.

        :param MoneroTxWallet tgt: another wallet tx to merge with.
        """
        ...
    @typing.overload
    def merge(self, tgt: MoneroTx) -> None: # type: ignore
        """
        Merge current wallet tx with another tx.

        :param MoneroTx tgt: another tx to merge with.
        """
        ...
