from .serializable_struct import SerializableStruct


class MoneroMinerTxSum(SerializableStruct):
    """Model for the sum of miner emissions and fees."""

    emission_sum: int | None
    """The new coins emitted in atomic-units."""
    fee_sum: int | None
    """The sum of fees in atomic-units."""

    def __init__(self) -> None:
        """Initialize a Monero miner transaction sum."""
        ...
