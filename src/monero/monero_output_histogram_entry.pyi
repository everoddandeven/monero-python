from .serializable_struct import SerializableStruct


class MoneroOutputHistogramEntry(SerializableStruct):
    """Models a Monero output histogram entry."""

    amount: int | None
    """Output amount in atomic-units."""
    num_instances: int | None
    """Number of outputs."""
    recent_instances: int | None
    """Number of recent outputs."""
    unlocked_instances: int | None
    """Number of unlocked outputs."""

    @staticmethod
    def deserialize(json: str) -> MoneroOutputHistogramEntry:
        """
        Deserialize a MoneroOutputHistogramEntry from a JSON string.

        :param str json: MoneroOutputHistogramEntry in JSON format.
        :returns MoneroOutputHistogramEntry: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero output histogram entry."""
        ...
