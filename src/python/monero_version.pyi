from .serializable_struct import SerializableStruct


class MoneroVersion(SerializableStruct):
    """
    Models a Monero version.
    """
    is_release: bool | None
    """States if the monero software version corresponds to an official tagged release (`True`), or not (`False`)."""
    number: int | None
    """Number of the monero software version."""
    def __init__(self) -> None:
        ...
