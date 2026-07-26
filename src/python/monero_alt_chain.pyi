from .serializable_struct import SerializableStruct


class MoneroAltChain(SerializableStruct):
    """Models an alternative chain seen by the node."""

    block_hashes: list[str]
    """List of all block hashes in the alternative chain that are not in the main chain."""
    difficulty_low: int | None
    """Cumulative difficulty of all blocks in the alternative chain (Least-significant 64 bits of 128-bit integer)."""
    difficulty_high: int | None
    """Cumulative difficulty of all blocks in the alternative chain (Most-significant 64 bits of the 128-bit integer)."""
    height: int | None
    """The block height of the first diverging block of this alternative chain."""
    length: int | None
    """The length in blocks of this alternative chain, after divergence."""
    main_chain_parent_block_hash: str | None
    """The hash of the greatest height block that is shared between the alternative chain and the main chain."""

    def __init__(self) -> None:
        """Initialize a Monero alt chain info."""
        ...
