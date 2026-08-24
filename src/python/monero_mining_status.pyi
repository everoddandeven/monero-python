from .serializable_struct import SerializableStruct


class MoneroMiningStatus(SerializableStruct):
    """Models a Monero daemon mining status."""

    address: str | None
    """Account address daemon is mining to. `None` if not mining."""
    is_active: bool | None
    """Indicates if mining is enabled."""
    is_background: bool | None
    """Indicates if mining is running in background."""
    num_threads: int | None
    """Number of running mining threads."""
    speed: int | None
    """Mining power in hashes per seconds."""

    @staticmethod
    def deserialize(json: str) -> MoneroMiningStatus:
        """
        Deserialize a MoneroMiningStatus from a JSON string.

        :param str json: MoneroMiningStatus in JSON format.
        :returns MoneroMiningStatus: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero daemon mining status."""
        ...
