from .serializable_struct import SerializableStruct


class MoneroVersion(SerializableStruct):
    """Models a Monero version."""

    is_release: bool | None
    """States if the monero software version corresponds to an official tagged release (`True`), or not (`False`)."""
    number: int | None
    """Number of the monero software version."""

    @staticmethod
    def deserialize(json: str) -> MoneroVersion:
        """
        Deserialize a MoneroVersion from a JSON string.

        :param str json: MoneroVersion in JSON format.
        :returns MoneroVersion: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a new Monero version."""
        ...
