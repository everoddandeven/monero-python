from .serializable_struct import SerializableStruct


class MoneroConnectionSpan(SerializableStruct):
    """Monero daemon connection span."""

    connection_id: str | None
    """Id of the P2P connection this span of blocks was (or is being) downloaded over."""
    num_blocks: int | None
    """Number of blocks in this span."""
    rate: int | None
    """Download rate for this span, in bytes per second."""
    remote_address: str | None
    """Peer address the node is downloading (or has downloaded) than span from."""
    size: int | None
    """Total number of bytes in that span's blocks (including txes)."""
    speed: int | None
    """Relative speed of this connection as a percentage (0-100) of the fastest peer currently downloading blocks."""
    start_height: int | None
    """Block height of the first block in that span."""

    @staticmethod
    def deserialize(json: str) -> MoneroConnectionSpan:
        """
        Deserialize a MoneroConnectionSpan from a JSON string.

        :param str json: MoneroConnectionSpan in JSON format.
        :returns MoneroConnectionSpan: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero connection span."""
        ...
