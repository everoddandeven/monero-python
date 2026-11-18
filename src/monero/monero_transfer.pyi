from .serializable_struct import SerializableStruct
from .monero_tx_wallet import MoneroTxWallet


class MoneroTransfer(SerializableStruct):
    """Models a base transfer of funds to or from the wallet."""

    account_index: int | None
    """Index of the account related to this transfer."""
    amount: int | None
    """Transfer amount in atomic-units."""
    tx: MoneroTxWallet
    """Related wallet transaction."""

    def __init__(self) -> None:
        """Initialize a Monero transfer."""
        ...

    def copy(self) -> MoneroTransfer:
        """
        Copy current transfer.

        :returns MoneroTransfer: transfer copy.
        """
        ...

    def is_incoming(self) -> bool | None:
        """
        Indicates if it is an incoming transfer (`True`) or not (`False`). Default `None`.

        :returns bool | None: `True` if current transfer is incoming, `False` if outgoing, `None` if unkown.
        """
        ...

    def is_outgoing(self) -> bool | None:
        """
        Indicates if it is an outgoing transfer (`True`) or not (`False`). Default `None`.

        :returns bool | None: `True` if current transfer is outgoing, `False` if incoming, `None` if unkown.
        """
        ...

    def merge(self, other: MoneroTransfer) -> None:
        """
        Merge current transfer with another one.

        :param MoneroTransfer other: other transfer to merge with.
        """
        ...
