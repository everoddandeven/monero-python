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
    "Multisignature transaction hex."
    signed_tx_hex: str | None
    "Signed transaction hex."
    txs: list[MoneroTxWallet]
    ""
    unsigned_tx_hex: str | None
    "Unsigned transaction hex."
    @staticmethod
    def deserialize(tx_set_json: str) -> MoneroTxSet:
        """
        Deserialize a Monero transaction set from a JSON string.

        :param str tx_set_json: JSON string.
        :return MoneroTxSet: The deseriliazed transaction set.
        """
        ...
    def __init__(self) -> None:
        """Initialize a Monero transaction set.s"""
        ...
