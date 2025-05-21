class MoneroMinerTxSum:
    """
    Model for the summation of miner emissions and fees.
    """
    emission_sum: int | None
    """The new coins emitted in atomic-units."""
    fee_sum: int | None
    """The sum of fees in atomic-units."""
    def __init__(self) -> None:
        """Initialize a Monero miner transaction sum."""
        ...
