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
    @property
    def tx_query(self) -> MoneroTxQuery | None:
        """Related transaction query."""
        ...
    @staticmethod
    def deserialize_from_block(output_query_json: str) -> MoneroOutputQuery:
        ...
    def __init__(self) -> None:
        """Initialize a Monero output query."""
        ...
    @typing.override
    def copy(self) -> MoneroOutputQuery:
        ...
    def set_tx_query(self, tx_query: MoneroTxQuery | None, output_query: bool) -> None:
        """
        Set tx query.

        :param MoneroTxQuery | None tx_query: Tx query to set.
        :param bool output_query: If `True` sets outputs query in tx query, otherwise inputs query.
        """
    def meets_criteria(self, output: MoneroOutputWallet, query_parent: bool = True) -> bool:
        """
        Indicates if the output meets all the criteria defined within this query.

        :param MoneroOutputWallet output: Output to check.
        :param bool query_parent: Query also parent.
        """
        ...
