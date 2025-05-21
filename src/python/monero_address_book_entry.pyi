import typing


class MoneroAddressBookEntry:
    """
    Monero address book entry model.
    """
    address: str | None
    """The book entry address."""
    description: str | None
    """The book entry description."""
    index: int | None
    """The book entry index."""
    payment_id: str | None
    """The book entry payment id."""
    
    @typing.overload
    def __init__(self) -> None:
        """Initialize an empty Monero address book entry."""
        ...
    @typing.overload
    def __init__(self, index: int, address: str, description: str) -> None:
        """
        Initialize a Monero address book entry.

        :param int index: The book entry index.
        :param str address: The book entry address.
        :param str description: The book entry description.
        """
        ...
    @typing.overload
    def __init__(self, index: int, address: str, description: str, payment_id: str) -> None:
        """
        Initialize a Monero address book entry.

        :param int index: The book entry index.
        :param str address: The book entry address.
        :param str description: The book entry description.
        :param str payment_id: The book entry payment id.
        """
        ...
