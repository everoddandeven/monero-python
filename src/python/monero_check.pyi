from .serializable_struct import SerializableStruct


class MoneroCheck(SerializableStruct):
    """
    Base class for results from checking a transaction or reserve proof.
    """
    is_good: bool
    """Indicates if check was successfull."""
    def __init__(self) -> None:
        ...
