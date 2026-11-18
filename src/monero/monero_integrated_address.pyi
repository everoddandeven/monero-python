from .serializable_struct import SerializableStruct


class MoneroIntegratedAddress(SerializableStruct):
    """Models a Monero integrated address."""

    integrated_address: str
    """The integrated address."""
    payment_id: str
    """The payment id related to this integrated address."""
    standard_address: str
    """The standard address related to this integrated address."""

    @staticmethod
    def deserialize(json: str) -> MoneroIntegratedAddress:
        """
        Deserialize a MoneroIntegratedAddress from a JSON string.

        :param str json: MoneroIntegratedAddress in JSON format.
        :returns MoneroIntegratedAddress: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero integrated address."""
        ...
