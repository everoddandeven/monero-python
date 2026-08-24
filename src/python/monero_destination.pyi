import typing
from .serializable_struct import SerializableStruct


class MoneroDestination(SerializableStruct):
    """Models an outgoing transfer destination."""

    address: str | None
    """Address of the receiver."""
    amount: int | None
    """Amount sent to this destination."""

    @staticmethod
    def deserialize(json: str) -> MoneroDestination:
        """
        Deserialize a MoneroDestination from a JSON string.

        :param str json: MoneroDestination in JSON format.
        :returns MoneroDestination: deserialized instance.
        """
        ...

    @typing.overload
    def __init__(self) -> None:
        """Initialize a Monero outgoing transfer destination."""
        ...

    @typing.overload
    def __init__(self, address: str) -> None:
        """
        Initialize a Monero outgoing transfer destination.

        :param str address: Address of the destination.
        """
        ...

    @typing.overload
    def __init__(self, address: str, amount: int) -> None:
        """
        Initialize a Monero outgoing transfer destination.

        :param str address: Address of the destination.
        :param int amount: Amount sent to the destination.
        """
        ...

    def copy(self) -> MoneroDestination:
        """
        Copy current outgoing transfer destination.

        :returns MoneroDestination: outgoing transfer destination copy.
        """
        ...
