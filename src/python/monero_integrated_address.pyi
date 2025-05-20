from .serializable_struct import SerializableStruct


class MoneroIntegratedAddress(SerializableStruct):
    """
    Monero integrated address model.
    """
    integrated_address: str
    payment_id: str
    standard_address: str
    def __init__(self) -> None:
        ...
