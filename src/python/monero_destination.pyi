import typing


class MoneroDestination:
    """
    Models an outgoing transfer destination.
    """
    address: str | None
    """Address of the receiver."""
    amount: int | None
    """Amount sent to this destination."""
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
    def copy(self, src: MoneroDestination, tgt: MoneroDestination) -> MoneroDestination:
        """
        Copy a Monero outgoing transfer destination.

        :param MoneroDestination src: Source.
        :param MoneroDestination target: Target.
        :return MoneroDestination: The copied destination.
        """
        ...
