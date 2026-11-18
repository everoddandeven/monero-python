from .monero_check import MoneroCheck


class MoneroCheckReserve(MoneroCheck):
    """Models the results from checking a reserve proof."""

    total_amount: int | None
    """The reserve total amount."""
    unconfirmed_spent_amount: int | None
    """The reserve unconfirmed spent amount."""

    @staticmethod
    def deserialize(json: str) -> MoneroCheckReserve:
        """
        Deserialize a MoneroCheckReserve from a JSON string.

        :param str json: MoneroCheckReserve in JSON format.
        :returns MoneroCheckReserve: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero reserve check."""
        ...
