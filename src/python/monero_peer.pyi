from .monero_connection_type import MoneroConnectionType


class MoneroPeer:
    """
    Models a peer to the daemon.
    """
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
    height: int | None
    """The peer blockchain height."""
    host: str | None
    """The peer host."""
    id: str | None
    """The node's ID on the network."""
    is_incoming: bool | None
    is_local_host: bool | None
    is_local_ip: bool | None
    is_online: bool | None
    last_seen_timestamp: int | None
    live_time: int | None
    num_receives: int | None
    num_sends: int | None
    num_support_flags: int | None
    port: int | None
    """The port that the node is using to connect to the network."""
    pruning_seed: int | None
    receive_idle_time: int | None
    rpc_credits_per_hash: int | None
    rpc_port: int | None
    send_idle_time: int | None
    state: str | None
    def __init__(self) -> None:
        ...
