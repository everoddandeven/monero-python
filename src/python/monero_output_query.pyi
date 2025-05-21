import typing

from .monero_output_wallet import MoneroOutputWallet
from .monero_tx_query import MoneroTxQuery


class MoneroOutputQuery(MoneroOutputWallet):
    """
    Configures a query to retrieve wallet outputs (i.e. outputs that the wallet has or had the
    ability to spend).
   
    All outputs are returned except those that do not meet the criteria defined in this query.
    """
    max_amount: int | None
    """Filter outputs above this amount."""
    min_amount: int | None
    """Filter outputs below this amount."""
    subaddress_indices: list[int]
    """Subadress indices to select (empty for all)."""
    tx_query: MoneroTxQuery | None
    """Related transaction query."""
    @staticmethod
    def deserialize_from_block(output_query_json: str) -> MoneroOutputQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroOutputQuery, tgt: MoneroOutputQuery) -> MoneroOutputQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroOutputWallet, tgt: MoneroOutputWallet) -> MoneroOutputQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutputQuery: # type: ignore
        ...
    def meets_criteria(self, output: MoneroOutputWallet, query_parent: bool = True) -> bool:
        """
        Indicates if the output meets all the criteria defined within this query.

        :param MoneroOutputWallet output: Output to check.
        :param bool query_parent: Query also parent.
        """
        ...
