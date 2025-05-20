class MoneroBan:
    """
     Monero banhammer.
    """
    host: str | None
    ip: int | None
    is_banned: bool | None
    seconds: int | None
    def __init__(self) -> None:
        ...
