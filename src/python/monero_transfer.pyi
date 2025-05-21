from .monero_tx_wallet import MoneroTxWallet


class MoneroTransfer:
    """
    Models a base transfer of funds to or from the wallet.
    """
    account_index: int | None
    """Index of the account related to this transfer."""
    amount: int | None
    """Transfer amount in atomic-units."""
    tx: MoneroTxWallet
    """Related wallet transaction."""
    def __init__(self) -> None:
        """Initialize a Monero transfer."""
        ...
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroTransfer:
        ...
    def is_incoming(self) -> bool | None:
        """
        Indicates if it is an incoming transfer (`True`) or not (`False`). Default `None`.

        :return Optional[bool]:
        """
        ...
    def is_outgoing(self) -> bool | None:
        """
        Indicates if it is an outgoing transfer (`True`) or not (`False`). Default `None`.

        :return Optional[bool]:
        """
        ...
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
