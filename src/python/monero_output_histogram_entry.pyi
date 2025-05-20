class MoneroOutputHistogramEntry:
    """
    Models a Monero output histogram entry.
    """
    amount: int | None
    num_instances: int | None
    recent_instances: int | None
    unlocked_instances: int | None
    def __init__(self) -> None:
        ...
