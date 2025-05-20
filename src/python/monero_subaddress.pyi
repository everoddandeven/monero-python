from .serializable_struct import SerializableStruct


class MoneroSubaddress(SerializableStruct):
    """
    Models a Monero subaddress.
    """
    account_index: int | None
    """The subaddress account index."""
    address: str | None
    """Public address."""
    balance: int | None
    """The subaddress balance."""
    index: int | None
    """The subaddress index."""
    is_used: bool | None
    """Indicates if subaddress has been used in receiving funds."""
    label: str | None
    """The subaddress label."""
    num_blocks_to_unlock: int | None
    """Number of blocks to unlock receveid outputs."""
    num_unspent_outputs: int | None
    """The number of unspent outputs in this subaddress."""
    unlocked_balance: int | None
    """The subaddress unlocked balance."""
    def __init__(self) -> None:
        ...
