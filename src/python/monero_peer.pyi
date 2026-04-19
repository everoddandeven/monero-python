from .monero_connection_type import MoneroConnectionType


class MoneroPeer:
    """Models a peer to the daemon."""

    address: str | None
    """The peer's address, actually IPv4 & port."""
    avg_download: int | None
    """Average bytes of data downloaded by node."""
    avg_upload: int | None
    """Average bytes of data uploaded by node."""
    connection_type: MoneroConnectionType | None
    """Type of peer connection."""
    current_download: int | None
    """Current bytes downloaded by node."""
    current_upload: int | None
    """Current bytes uploaded by node."""
    hash: str | None
    """Peer hash."""
    height: int | None
    """The peer blockchain height."""
    host: str | None
    """The peer host."""
    id: str | None
    """The node's ID on the network."""
    is_incoming: bool | None
    """Indicates if peer is pulling blocks from node."""
    is_local_host: bool | None
    """Indicates if peer is localhost."""
    is_local_ip: bool | None
    """Indicates if peer has a local ip address."""
    is_online: bool | None
    """Indicates if the peer is online."""
    last_seen_timestamp: int | None
    """Last activity timestamp of this peer."""
    live_time: int | None
    """Length of time the peer has been online."""
    num_receives: int | None
    """Total number of messages received from this peer."""
    num_sends: int | None
    """Total number of messages sent to this peer."""
    num_support_flags: int | None
    """Support flags number."""
    port: int | None
    """The port that the node is using to connect to the network."""
    pruning_seed: int | None
    """Block height at which pruning began."""
    receive_idle_time: int | None
    """Seconds since last data was received from this peer."""
    rpc_credits_per_hash: int | None
    """Credits for every hash calculated by client."""
    rpc_port: int | None
    """Peer RPC port."""
    send_idle_time: int | None
    """Seconds since the last data sent to this peer."""
    state: str | None
    """Peer state."""

    def __init__(self) -> None:
        """Initialize a new Monero peer."""
        ...
