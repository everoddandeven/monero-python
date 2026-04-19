class MoneroOutputDistributionEntry:
    """Models a Monero output distribution entry."""

    amount: int | None
    """Output amount in atomic-units."""
    base: int | None
    """The total number of outputs of `amount` in the chain before, not including, the block at `start_height`."""
    distribution: list[int]
    """The output distibution."""
    start_height: int | None
    """Not necessarily equal to `start_height` parameter especially for `amount = 0` where `start_height` will be no less than the height of the v4 hardfork."""

    def __init__(self) -> None:
        """Initialize a Monero output distribution entry."""
        ...
