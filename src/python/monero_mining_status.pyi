class MoneroMiningStatus:
    """
    Monero daemon mining status.
    """
    address: str | None
    """Account address daemon is mining to. Empty if not mining."""
    is_active: bool | None
    """Indicates if mining is enabled."""
    is_background: bool | None
    """Indicates if mining is running in background."""
    num_threads: int | None
    """Number of running mining threads."""
    speed: int | None
    """Mining power in hashes per seconds."""
    def __init__(self) -> None:
        ...
