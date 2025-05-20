from .serializable_struct import SerializableStruct


class MoneroKeyImageImportResult(SerializableStruct):
    """
    Models results from importing key images.
    """
    height: int | None
    spent_amount: int | None
    unspent_amount: int | None
    def __init__(self) -> None:
        ...
