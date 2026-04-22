from .monero_peer import MoneroPeer
from .monero_rpc_payment_info import MoneroRpcPaymentInfo
from .monero_connection_span import MoneroConnectionSpan


class MoneroDaemonSyncInfo(MoneroRpcPaymentInfo):
    """Models daemon synchronization information."""

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

    def __init__(self) -> None:
        """Initialize a Monero daemon sync info."""
        ...
