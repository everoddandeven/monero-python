from .monero_check import MoneroCheck


class MoneroCheckTx(MoneroCheck):
    """
    Results from checking a transaction key.
    """
    in_tx_pool: bool | None
    """States if the transaction is in pool (`True`) or included in a block (`False`)"""
    num_confirmations: int | None
    """Transaction network confirmations."""
    received_amount: int | None
    """Amount received in the transaction."""
    def __init__(self) -> None:
        """Initialize a Monero transaction check."""
        ...
