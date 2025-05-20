from .serializable_struct import SerializableStruct


class MoneroRequest(SerializableStruct):
    """
    Models a Monero HTTP request.
    """
    method: str | None
    def __init__(self) -> None:
        ...
