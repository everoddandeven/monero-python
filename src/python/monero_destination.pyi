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
        ...
    @typing.overload
    def __init__(self, address: str) -> None:
        ...
    @typing.overload
    def __init__(self, address: str, amount: int) -> None:
        ...
    def copy(self, src: MoneroDestination, tgt: MoneroDestination) -> MoneroDestination:
        ...
