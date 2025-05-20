from .serializable_struct import SerializableStruct
from .monero_block import MoneroBlock
from .monero_output import MoneroOutput


class MoneroTx(SerializableStruct):
    """
    Models a Monero transaction on the blockchain.
    """
    block: MoneroBlock | None
    common_tx_sets: str | None
    extra: list[int]
    fee: int | None
    full_hex: str | None
    hash: str | None
    in_tx_pool: bool | None
    inputs: list[MoneroOutput]
    is_confirmed: bool | None
    is_double_spend_seen: bool | None
    is_failed: bool | None
    is_kept_by_block: bool | None
    is_miner_tx: bool | None
    is_relayed: bool | None
    key: str | None
    last_failed_hash: str | None
    last_failed_height: int | None
    last_relayed_timestamp: int | None
    max_used_block_hash: str | None
    max_used_block_height: int | None
    metadata: str | None
    num_confirmations: int | None
    output_indices: list[int]
    outputs: list[MoneroOutput]
    payment_id: str | None
    prunable_hash: str | None
    prunable_hex: str | None
    pruned_hex: str | None
    rct_sig_prunable: str | None
    rct_signatures: str | None
    received_timestamp: int | None
    relay: bool | None
    ring_size: int | None
    signatures: list[str]
    size: int | None
    unlock_time: int | None
    version: int | None
    weight: int | None
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroTx, tgt: MoneroTx) -> MoneroTx:
        ...
    def get_height(self) -> int | None:
        ...
    def merge(self, _self: MoneroTx, other: MoneroTx) -> None:
        ...
