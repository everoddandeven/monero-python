class MoneroPruneResult:
    """
    Result of pruning the blockchain.
    """
    is_pruned: bool | None
    """Indicates if blockchain is pruned."""
    pruning_seed: int | None
    """Blockheight at which pruning began."""
    def __init__(self) -> None:
        """Initialize a Monero prune result."""
        ...
