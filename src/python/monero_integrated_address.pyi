from .serializable_struct import SerializableStruct


class MoneroIntegratedAddress(SerializableStruct):
    """
    Monero integrated address model.
    """
    integrated_address: str
    """The integrated address."""
    payment_id: str
    """The payment id related to this integrated address."""
    standard_address: str
    """The standard address related to this integrated address."""
    def __init__(self) -> None:
        """Initialize a Monero integrated address."""
        ...
