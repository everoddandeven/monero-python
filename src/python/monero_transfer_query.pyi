import typing

from .monero_transfer import MoneroTransfer
from .monero_destination import MoneroDestination
from .monero_tx_query import MoneroTxQuery


class MoneroTransferQuery(MoneroTransfer):
    """
    Configures a query to retrieve transfers.
    
    All transfers are returned except those that do not meet the criteria defined in this query.
    """
    address: int | None
    addresses: list[str]
    destinations: list[MoneroDestination]
    has_destinations: bool | None
    incoming: bool | None
    subaddress_indices: list[int]
    tx_query: MoneroTxQuery | None
    @staticmethod
    def deserialize_from_block(transfer_query_json: str) -> MoneroTransferQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroTransferQuery, tgt: MoneroTransferQuery) -> MoneroTransferQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroTransferQuery:
        ...
    def meets_criteria(self, transfer: MoneroTransferQuery, query_parent: bool = True) -> bool:
        ...
