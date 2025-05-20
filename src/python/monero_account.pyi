from .serializable_struct import SerializableStruct
from .monero_subaddress import MoneroSubaddress


class MoneroAccount(SerializableStruct):
    """
    Models a Monero account.
    """
    balance: int | None
    """The account balance."""
    index: int | None
    """The account index."""
    primary_address: str | None
    """The account primary address."""
    subaddresses: list[MoneroSubaddress]
    """List of account subaddresses."""
    tag: str | None
    """The account tag."""
    unlocked_balance: int | None
    """The account unlocked balance."""
    def __init__(self) -> None:
        ...