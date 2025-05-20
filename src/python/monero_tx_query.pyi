import typing

from .monero_tx_wallet import MoneroTxWallet
from .monero_output_query import MoneroOutputQuery
from .monero_transfer_query import MoneroTransferQuery


class MoneroTxQuery(MoneroTxWallet):
    """
    Configures a query to retrieve transactions.
   
    All transactions are returned except those that do not meet the criteria defined in this query.
    """
    has_payment_id: bool | None
    hashes: list[str]
    height: int | None
    include_outputs: int | None
    input_query: MoneroOutputQuery | None
    is_incoming: bool | None
    is_outgoing: bool | None
    max_height: int | None
    min_height: int | None
    output_query: MoneroOutputQuery | None
    payment_ids: list[str]
    transfer_query: MoneroTransferQuery | None
    @staticmethod
    def deserialize_from_block(tx_query_json: str) -> MoneroTxQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroTxQuery, tgt: MoneroTxQuery) -> MoneroTxQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroTxWallet, tgt: MoneroTxWallet) -> MoneroTxQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroTx, tgt: MoneroTx) -> MoneroTxQuery: # type: ignore
        ...
    def meets_criteria(self, tx: MoneroTxWallet, query_children: bool = False) -> bool:
        ...
