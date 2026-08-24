from .monero_check import MoneroCheck


class MoneroCheckTx(MoneroCheck):
    """Models the results from checking a transaction key."""

    in_tx_pool: bool | None
    """States if the transaction is in pool (`True`) or included in a block (`False`)"""
    num_confirmations: int | None
    """Transaction network confirmations."""
    received_amount: int | None
    """Amount received in the transaction."""

    @staticmethod
    def deserialize(json: str) -> MoneroCheckTx:
        """
        Deserialize a MoneroCheckTx from a JSON string.

        :param str json: MoneroCheckTx in JSON format.
        :returns MoneroCheckTx: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero transaction check."""
        ...
