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
        ...
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroTransfer:
        ...
    def is_incoming(self) -> bool | None:
        ...
    def is_outgoing(self) -> bool | None:
        ...
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
