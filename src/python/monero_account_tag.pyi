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
        ...
    @typing.overload
    def __init__(self, tag: str, label: str) -> None:
        ...
    @typing.overload
    def __init__(self, tag: str, label: str, account_indices: list[int]) -> None:
        ...
