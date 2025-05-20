class MoneroAltChain:
    """
    Models an alternative chain seen by the node.
    """
    block_hashes: list[str]
    """List of all block hashes in the alternative chain that are not in the main chain."""
    difficulty: int | None
    """Cumulative difficulty of all blocks in the alternative chain."""
    height: int | None
    """The block height of the first diverging block of this alternative chain."""
    length: int | None
    """The length in blocks of this alternative chain, after divergence."""
    main_chain_parent_block_hash: str | None
    """The hash of the greatest height block that is shared between the alternative chain and the main chain."""
    def __init__(self) -> None:
        ...
