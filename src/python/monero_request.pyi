from .serializable_struct import SerializableStruct


class MoneroRequest(SerializableStruct):
    """
    Models a Monero HTTP request.
    """
    method: str | None
    """The HTTP method to invoke."""
    def __init__(self) -> None:
        """Initialize a Monero request."""
        ...
