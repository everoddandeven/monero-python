class MoneroOutputDistributionEntry:
    """
    Models a Monero output distribution entry.
    """
    amount: int | None
    base: int | None
    distribution: list[int]
    start_height: int | None
    def __init__(self) -> None:
        ...
