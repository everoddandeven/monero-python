class MoneroBlockTemplate:
    """
    Monero block template to mine.
    """
    block_hashing_blob: str | None
    """Blob on which to try to find a valid nonce."""
    block_template_blob: str | None
    """Blob on which to try to mine a new block."""
    difficulty: int | None
    """Network difficulty."""
    expected_reward: int | None
    """Coinbase reward expected to be received if block is successfully mined."""
    height: int | None
    """Height on which to mine."""
    next_seed_hash: str | None
    """Hash of the next block to use as seed for Random-X proof-of-work."""
    prev_hash: str | None
    """Hash of the most recent block on which to mine the next block."""
    reserved_offset: int | None
    """Reserved offset."""
    seed_hash: str | None
    """Hash of block to use as seed for Random-X proof-of-work."""
    seed_height: int | None
    """Height of block to use as seed for Random-X proof-of-work."""
    def __init__(self) -> None:
        ...
