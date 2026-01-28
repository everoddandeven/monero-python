import typing

from .monero_block_header import MoneroBlockHeader
from .monero_tx import MoneroTx

class MoneroBlock(MoneroBlockHeader):
    """
    Models a Monero block in the blockchain.
    """
    hex: str | None
    """Hexadecimal blob of block information."""
    miner_tx: MoneroTx | None
    """Miner transaction information."""
    tx_hashes: list[str]
    """List of hashes of non-coinbase transactions in the block."""
    txs: list[MoneroTx]
    """List of non-coinbase transactions in the block."""
    def __init__(self) -> None:
        """Initialize a Monero block."""
        ...
    @typing.override
    def copy(self) -> MoneroBlock:
        ...
    @typing.overload
    def merge(self, other: MoneroBlock) -> None:
        ...
    @typing.overload
    def merge(self, other: MoneroBlockHeader) -> None:
        ...
