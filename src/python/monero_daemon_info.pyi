from .monero_network_type import MoneroNetworkType


class MoneroDaemonInfo:
    """
    Monero daemon info.
    """
    adjusted_timestamp: int | None
    """Current time approximated from chain data, as Unix time."""
    block_size_limit: int | None
    """Backward compatibility, same as `block_weight_limit`, use that instead."""
    block_size_median: int | None
    """Backward compatibility, same as `block_weight_median`, use that instead."""
    block_weight_limit: int | None
    """Maximum allowed adjusted block size based on latest `100000` blocks."""
    block_weight_median: int | None
    """Median adjusted block size of latest `100000` blocks."""
    bootstrap_daemon_address: str | None
    """Bootstrap-node to give immediate usability to wallets while syncing by proxying RPC to it."""
    credits: int | None
    cumulative_difficulty: int | None
    """Cumulative difficulty."""
    database_size: int | None
    """The size of the blockchain database, in bytes."""
    difficulty: int | None
    """The network difficulty."""
    free_space: int | None
    """Available disk space on the node."""
    height: int | None
    """Current length of longest chain known to daemon."""
    height_without_bootstrap: int | None
    """Current length of the local chain of the daemon."""
    is_busy_syncing: bool | None
    """States if new blocks are being added (`True`) or not (`False`)."""
    is_offline: bool | None
    """States if the node is offline (`True`) or online (`False`)."""
    is_restricted: bool | None
    is_synchronized: bool | None
    """States if the node is synchronized (`True`) or not (`False`)."""
    network_type: MoneroNetworkType | None
    """Network type (`MAINNET`, `TESTNET`, or `STAGENET`)."""
    num_alt_blocks: int | None
    """Number of alternative blocks to main chain."""
    num_incoming_connections: int | None
    """Number of peers connected to and pulling from your node."""
    num_offline_peers: int | None
    """Number of peers that are marked as not reacheable on the network."""
    num_online_peers: int | None
    """Number of peers that are marked as reacheble on the network."""
    num_outgoing_connections: int | None
    """Number of peers that you are connected to and getting information from."""
    num_rpc_connections: int | None
    """Number of RPC client connected to the daemon (Including this RPC request)."""
    num_txs: int | None
    """Total number of non-coinbase transactions in the chain."""
    num_txs_pool: int | None
    """Number of transactions that have been broadcast but not included in a block."""
    start_timestamp: int | None
    """Start time of the daemon, as UNIX time."""
    target: int | None
    """Current target for next proof of work."""
    target_height: int | None
    """The height of the next block in the chain."""
    top_block_hash: str | None
    """Hash of the highest block in the chain."""
    update_available: bool | None
    """States if a newer Monero software version is available."""
    version: str | None
    """The version of the Monero software the node is running."""
    was_bootstrap_ever_used: bool | None
    """States if a bootstrap node has ever been used since the daemon started."""
    def __init__(self) -> None:
        """Initiliaze a Monero daemon info."""
        ...
