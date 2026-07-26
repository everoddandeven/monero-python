from .serializable_struct import SerializableStruct


class MoneroMinerTxSum(SerializableStruct):
    """Model for the sum of miner emissions and fees."""

    emission_sum_low: int | None
    """The new coins emitted in atomic-units. (Least significant 64 bits for 128 bit integer)"""
    emission_sum_high: int | None
    """The new coins emitted in atomic-units. (Most significant 64 bits for 128 bit integer)"""
    fee_sum_low: int | None
    """The sum of fees in atomic-units. (Least significant 64 bits for 128 bit integer)"""
    fee_sum_high: int | None
    """The sum of fees in atomic-units. (Most significant 64 bits for 128 bit integer)"""

    def __init__(self) -> None:
        """Initialize a Monero miner transaction sum."""
        ...
