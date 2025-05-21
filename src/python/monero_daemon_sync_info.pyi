from .monero_peer import MoneroPeer
from .monero_connection_span import MoneroConnectionSpan


class MoneroDaemonSyncInfo:
    """
    Models daemon synchronization information.
    """
    credits: int | None
    """If payment for RPC is enabled, the number of credits available to the requesting client."""
    height: int | None
    """Daemon blockchain height."""
    next_needed_pruning_seed: int | None
    """The next pruning seed needed for pruned sync."""
    overview: str | None
    """
    Overview of current block queue where each character in the string represents a block set in the queue.
    `'.' = requested but not received, 'o' = set received, 'm' = received set that matches the next blocks needed`
    """
    peers: list[MoneroPeer]
    """List of peers connected to the node"""
    spans: list[MoneroConnectionSpan]
    """Currently connected peers to download blocks from."""
    target_height: int | None
    """Target height the node is syncing from (will be 0 if node is fully synced)."""
    top_block_hash: str | None
    """Hash of the highest block in the chain."""
    def __init__(self) -> None:
        """Initialize a Monero daemon sync info."""
        ...
