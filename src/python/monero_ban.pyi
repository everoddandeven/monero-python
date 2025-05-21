class MoneroBan:
    """
     Monero banhammer.
    """
    host: str | None
    """Host ban."""
    ip: int | None
    """IP ban."""
    is_banned: bool | None
    """Indicates if ban on the `host` is active (`True`) or not (`False`)."""
    seconds: int | None
    """Indicates the duration of the ban in seconds."""
    def __init__(self) -> None:
        """Initialize a Monero banhammer."""
        ...
