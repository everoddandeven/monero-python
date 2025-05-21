class MoneroOutputDistributionEntry:
    """
    Models a Monero output distribution entry.
    """
    amount: int | None
    """Output amount in atomic-units."""
    base: int | None
    """The total number of outputs of `amount` in the chain before, not including, the block at `start_height`."""
    distribution: list[int]
    """The output distibution."""
    start_height: int | None
    def __init__(self) -> None:
        ...
