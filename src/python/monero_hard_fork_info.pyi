class MoneroHardForkInfo:
    """
    Models a Monero look up information regarding hard fork voting and readiness.
    """
    credits: int | None
    """If payment for RPC is enabled, the number of credits available to the requesting client."""
    earliest_height: int | None
    """Block height at which hard fork would be enabled if voted in."""
    is_enabled: bool | None
    """Tells if hard fork is enforced."""
    num_votes: int | None
    """Number of votes towards hard fork."""
    state: int | None
    """
    Current hard fork state.
    `0` (There is likely a hard fork), `1` (An update is needed to fork properly), or `2` (Everything looks good).
    """
    threshold: int | None
    """Minimum percent of votes to trigger hard fork. Default is 80."""
    top_block_hash: str | None
    """If payment for RPC is enabled, the hash of the highest block in the chain. Otherwise, empty."""
    version: int | None
    """The major block version for the fork."""
    voting: int | None
    """Hard fork voting status."""
    window: int | None
    """Number of blocks over which current votes are cast. Default is `10080` blocks."""
    def __init__(self) -> None:
        """Initialize a Monero hard fork info."""
        ...
