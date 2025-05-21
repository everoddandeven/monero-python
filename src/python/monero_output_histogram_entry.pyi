class MoneroOutputHistogramEntry:
    """
    Models a Monero output histogram entry.
    """
    amount: int | None
    """Output amount in atomic-units."""
    num_instances: int | None
    """Number of outputs."""
    recent_instances: int | None
    """Number of recent outputs."""
    unlocked_instances: int | None
    """Number of unlocked outputs."""
    def __init__(self) -> None:
        ...
