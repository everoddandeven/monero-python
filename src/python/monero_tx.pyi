from .serializable_struct import SerializableStruct
from .monero_block import MoneroBlock
from .monero_output import MoneroOutput


class MoneroTx(SerializableStruct):
    """
    Models a Monero transaction on the blockchain.
    """
    DEFAULT_PAYMENT_ID: str
    """Default tx payment id"""
    block: MoneroBlock | None
    """Block including the transaction."""
    common_tx_sets: str | None
    """A hexadecimal string representing a set of unsigned transactions, or a set of signing keys used in a multisig transaction."""
    extra: list[int]
    """Usually called the `payment ID` but can be used to include any random 32 bytes."""
    fee: int | None
    """The amount of the mining fee included in the transaction, in atomic-units."""
    full_hex: str | None
    """Full transaction information as a hex string."""
    hash: str | None
    """The transaction hash."""
    in_tx_pool: bool | None
    """States if the transaction is in pool (`True`) or included in a block (`False`)."""
    inputs: list[MoneroOutput]
    """List of inputs into transaction."""
    is_confirmed: bool | None
    """States if the transaction included in a block (`True`) or is in pool (`False`)."""
    is_double_spend_seen: bool | None
    """States if the transaction is a double-spend (`True`) or not (`False`)."""
    is_failed: bool | None
    """Indicates if the transaction validation has previously failed."""
    is_kept_by_block: bool | None
    """States if the transaction was included in a block at least once (`True`) or not (`False`)."""
    is_miner_tx: bool | None
    """States if the transaction is a coinbase-transaction (`True`) or not (`False`)."""
    is_relayed: bool | None
    """States if the transaction was relayed (`True`) or not (`False`)."""
    key: str | None
    """The transaction key."""
    last_failed_hash: str | None
    """If the transaction validation has previously failed, this tells the previous transaction hash."""
    last_failed_height: int | None
    """If the transaction validation has previously failed, this tells at what height that occurred."""
    last_relayed_timestamp: int | None
    """Last unix time at which the transaction has been relayed."""
    max_used_block_hash: str | None
    """Tells the hash of the most recent block with an output used in this transaction."""
    max_used_block_height: int | None
    """Tells the height of the most recent block with an output used in this transaction."""
    metadata: str | None
    """Transaction metadata."""
    num_confirmations: int | None
    """Number of network confirmations."""
    output_indices: list[int]
    """Transaction indexes."""
    outputs: list[MoneroOutput]
    """Transaction outputs."""
    payment_id: str | None
    """Payment ID for this transaction."""
    prunable_hash: str | None
    """Keccak-256 hash of the prunable portion of the block."""
    prunable_hex: str | None
    """Prunable block encoded as a hex string."""
    pruned_hex: str | None
    """Pruned block encoded as hex string."""
    rct_sig_prunable: str | None
    """Prunable ring signature."""
    rct_signatures: str | None
    """Signatures used in ring signature to hide the true origin of the transaction."""
    received_timestamp: int | None
    """Unix time at chich the transaction has been received."""
    relay: bool | None
    """States if this transaction should be relayed (`True`) or not (`False`)."""
    ring_size: int | None
    """The ring size of this transaction."""
    signatures: list[str]
    """List of signatures used in ring signature to hide the true origin of the transaction."""
    size: int | None
    """Backward compatibility, same as `weight`, use that instead."""
    unlock_time: int | None
    """If not `0`, this tells when the transaction outputs are spendable."""
    version: int | None
    """Transaction version."""
    weight: int | None
    """The weight of this transaction in bytes."""
    def __init__(self) -> None:
        ...
    def copy(self) -> MoneroTx:
        ...
    def get_height(self) -> int | None:
        """
        Get the transaction height.

        :return int | None: The height of the transaction, if known.
        """
        ...
    def merge(self, other: MoneroTx) -> None:
        ...
