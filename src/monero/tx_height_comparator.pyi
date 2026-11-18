from .monero_tx import MoneroTx


class TxHeightComparator:
    """Compares two transactions by their height."""

    @staticmethod
    def compare(tx1: MoneroTx, tx2: MoneroTx) -> bool:
        """
        Compare two transactions by height.

        Unconfirmed transactions (no block) sort after confirmed ones; when
        both are unconfirmed or share the same height and block, their
        original order within the block's tx list is preserved.

        :param MoneroTx tx1: first transaction to compare.
        :param MoneroTx tx2: second transaction to compare.

        :returns bool: `True` if tx1 sorts before tx2, `False` otherwise.
        """
        ...
