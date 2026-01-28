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
    """Get transactions that have a payment id."""
    hashes: list[str]
    """Get transactions by hashes."""
    height: int | None
    """Get transactions by height."""
    include_outputs: int | None
    """Include outputs in transaction data."""
    input_query: MoneroOutputQuery | None
    """Query to apply on transaction inputs."""
    is_incoming: bool | None
    """Include incoming transactions."""
    is_outgoing: bool | None
    """Include outgoing transactions."""
    max_height: int | None
    """Get transactions below max height."""
    min_height: int | None
    """Get transactions above max height."""
    output_query: MoneroOutputQuery | None
    """Query to apply on transaction outputs."""
    payment_ids: list[str]
    """Get transactions with specific payment ids."""
    transfer_query: MoneroTransferQuery | None
    """Query to apply on transaction wallet transfer."""
    @staticmethod
    def deserialize_from_block(tx_query_json: str) -> MoneroTxQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.override
    def copy(self) -> MoneroTxQuery:
        ...
    def meets_criteria(self, tx: MoneroTxWallet, query_children: bool = False) -> bool:
        ...
