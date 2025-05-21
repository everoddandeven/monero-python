from .monero_check import MoneroCheck


class MoneroCheckReserve(MoneroCheck):
    """
    Results from checking a reserve proof.
    """
    total_amount: int | None
    """The reserve total amount."""
    unconfirmed_spent_amount: int | None
    """The reserve unconfirmed spent amount."""
    def __init__(self) -> None:
        """Initialize a Monero reserve check."""
        ...
