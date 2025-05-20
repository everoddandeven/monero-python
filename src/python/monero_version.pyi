from .serializable_struct import SerializableStruct


class MoneroVersion(SerializableStruct):
    """
    Models a Monero version.
    """
    is_release: bool | None
    number: int | None
    def __init__(self) -> None:
        ...
