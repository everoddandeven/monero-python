from __future__ import annotations

from .serializable_struct import SerializableStruct


class MoneroBlockHeader(SerializableStruct):
    """
    Models a Monero block header which contains information about the block.
    """
    cumulative_difficulty: int | None
    """Cumulative difficulty of all blocks up to the block in the reply."""
    depth: int | None
    """The number of blocks succeeding this block on the blockchain. A larger number means an older block."""
    difficulty: int | None
    """The strength of the Monero network based on mining power."""
    hash: str | None
    """The hash of this block."""
    height: int | None
    """The number of blocks preceding this block on the blockchain."""
    long_term_weight: int | None
    """The long term block weight, based on the median weight of the preceding 100000 blocks."""
    major_version: int | None
    """The major version of the monero protocol at this block height."""
    miner_tx_hash: str | None
    """The hash of this block's coinbase transaction."""
    minor_version: int | None
    """The minor version of the monero protocol at this block height."""
    nonce: int | None
    """A cryptographic random one-time number used in mining a Monero block."""
    num_txs: int | None
    """Number of transactions included in this block."""
    orphan_status: bool | None
    """If true, this block is not part of the longest chain."""
    pow_hash: str | None
    """The hash, as a hexadecimal string, calculated from the block as proof-of-work."""
    prev_hash: str | None
    """The hash of the block immediately preceding this block in the chain."""
    reward: int | None
    """The amount of atomic-units rewarded to the miner. The reward is the sum of new coins created (the emission) and fees paid by transactions in this block. Note: 1 XMR = 1e12 atomic-units."""
    size: int | None
    """Backward compatibility, same as `weight` , use that instead."""
    timestamp: int | None
    """The unix time at which the block was recorded into the blockchain."""
    weight: int | None
    """The adjusted block size, in bytes. This is the raw size, plus a positive adjustment for any Bulletproof transactions with more than 2 outputs."""
    def __init__(self) -> None:
        """Initialize a Monero block header."""
        ...
    def copy(self, src: MoneroBlockHeader, tgt: MoneroBlockHeader) -> MoneroBlockHeader:
        ...
    def merge(self, _self: MoneroBlockHeader, other: MoneroBlockHeader) -> None:
        ...
