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
    """
    Serialized multisig transaction data produced when a multisig wallet creates transactions;
    passed to the other cosigners' `MoneroWallet.sign_multisig_tx_hex()` and finally to
    `submit_multisig_tx_hex()` once enough signatures are collected.
    """
    signed_tx_hex: str | None
    """
    Serialized fully-signed transaction data returned by `MoneroWallet.sign_txs()` on the offline
    spend wallet; pass it to `submit_txs()` on an online wallet to broadcast.
    """
    txs: list[MoneroTxWallet]
    """The structured transactions in this set (populated when the set is created locally or by `describe_tx_set()`)."""
    unsigned_tx_hex: str | None
    """
    Serialized unsigned transaction data produced by a view-only wallet's `create_tx()` /
    `create_txs()`; transfer it to the offline spend wallet and call `MoneroWallet.sign_txs()`.
    """
    @staticmethod
    def deserialize(tx_set_json: str) -> MoneroTxSet:
        """
        Deserialize a Monero transaction set from a JSON string.

        :param str tx_set_json: tx set as JSON string.
        :returns MoneroTxSet: The deseriliazed transaction set.
        """
        ...
    def __init__(self) -> None:
        """Initialize a Monero transaction set."""
        ...
