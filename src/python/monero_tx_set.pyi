from .serializable_struct import SerializableStruct
from .monero_tx_wallet import MoneroTxWallet


class MoneroTxSet(SerializableStruct):
    """
    Groups transactions who share common hex data which is needed in order to
    sign and submit the transactions.

    For example, multisig transactions created from create_txs() share a common
    hex string which is needed in order to sign and submit the multisig
    transactions.
    """
    multisig_tx_hex: str | None
    signed_tx_hex: str | None
    txs: list[MoneroTxWallet]
    unsigned_tx_hex: str | None
    @staticmethod
    def deserialize(tx_set_json: str) -> MoneroTxSet:
        ...
    def __init__(self) -> None:
        ...
