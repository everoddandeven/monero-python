class MoneroConnectionSpan:
    """
    Monero daemon connection span.
    """
    connection_id: str | None
    """Id of connection"""
    num_blocks: int | None
    """Number of blocks in this span"""
    rate: int | None
    """Connection rate"""
    remote_address: str | None
    """Peer address the node is downloading (or has downloaded) than span from."""
    size: int | None
    """Total number of bytes in that span's blocks (including txes)."""
    speed: int | None
    """Connection speed."""
    start_height: int | None
    """Block height of the first block in that span."""
    def __init__(self) -> None:
        ...
