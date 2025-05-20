import typing


class MoneroAddressBookEntry:
    """
    Monero address book entry model.
    """
    address: str | None
    description: str | None
    index: int | None
    payment_id: str | None
    
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, index: int, address: str, description: str) -> None:
        ...
    @typing.overload
    def __init__(self, index: int, address: str, description: str, payment_id: str) -> None:
        ...
