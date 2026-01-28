import typing

from .monero_transfer import MoneroTransfer
from .monero_destination import MoneroDestination
from .monero_tx_query import MoneroTxQuery


class MoneroTransferQuery(MoneroTransfer):
    """
    Configures a query to retrieve transfers.
    
    All transfers are returned except those that do not meet the criteria defined in this query.
    """
    address: str | None
    """Select transfers involving particular address. Empty for all."""
    addresses: list[str]
    """Select transfers involving particular addresses. Empty for all."""
    destinations: list[MoneroDestination]
    """Select transfers involving particular destinations. Empty for all."""
    has_destinations: bool | None
    """Filter transfers with or without destinations. `None` for all."""
    incoming: bool | None
    """Filter incoming or outgoing transfers. `None` for all."""
    subaddress_indices: list[int]
    """Select transfers involving particular subaddresses. Empty for all."""
    tx_query: MoneroTxQuery | None
    """Related transaction query."""
    @staticmethod
    def deserialize_from_block(transfer_query_json: str) -> MoneroTransferQuery:
        ...
    def __init__(self) -> None:
        """Initialize a Monero transfer query."""
        ...
    @typing.override
    def copy(self) -> MoneroTransferQuery:
        ...
    def meets_criteria(self, transfer: MoneroTransferQuery, query_parent: bool = True) -> bool:
        ...
