import typing

class MoneroAccountTag:
    """
    Models a Monero account tag.
    """
    account_indices: list[int]
    """Account indices with this tag."""
    label: str | None
    """The account tag label."""
    tag: str | None
    """The account tag."""
    @typing.overload
    def __init__(self) -> None:
        """
        Initialize a new Monero account tag.

        :param Optional[str] tag: Account tag.
        :param Optional[str] label: Account label.
        :param Optional[list[int]] account_indices: Account indices
        """
        ...
    @typing.overload
    def __init__(self, tag: str, label: str) -> None:
        """
        Initialize a new Monero account tag.

        :param str tag: Account tag.
        :param str label: Account label.
        """
        ...
    @typing.overload
    def __init__(self, tag: str, label: str, account_indices: list[int]) -> None:
        """
        Initialize a new Monero account tag.

        :param str tag: Account tag.
        :param str label: Account label.
        :param list[int] account_indices: Account indices.
        """
        ...
