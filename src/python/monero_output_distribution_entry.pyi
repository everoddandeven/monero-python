from .serializable_struct import SerializableStruct


class MoneroOutputDistributionEntry(SerializableStruct):
    """Models a Monero output distribution entry."""

    amount: int | None
    """Output amount in atomic-units."""
    base: int | None
    """The total number of outputs of `amount` in the chain before, not including, the block at `start_height`."""
    distribution: list[int]
    """
    Per-block counts of outputs of `amount` starting at `start_height`: element `i` is the number
    created in block `start_height + i`, or the running total up to that block when the distribution
    was requested as cumulative. Wallets use this to weight decoy selection by output age.
    """
    start_height: int | None
    """
    Not necessarily equal to the `start_height` parameter, especially for `amount = 0` where it will
    be no less than the height of the v4 hard fork.
    """

    @staticmethod
    def deserialize(json: str) -> MoneroOutputDistributionEntry:
        """
        Deserialize a MoneroOutputDistributionEntry from a JSON string.

        :param str json: MoneroOutputDistributionEntry in JSON format.
        :returns MoneroOutputDistributionEntry: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero output distribution entry."""
        ...
