from .monero_rpc_payment_info import MoneroRpcPaymentInfo


class MoneroHardForkInfo(MoneroRpcPaymentInfo):
    """Models a Monero look up information regarding hard fork voting and readiness."""

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
    version: int | None
    """The major block version for the fork."""
    voting: int | None
    """Hard fork voting status."""
    window: int | None
    """Number of blocks over which current votes are cast. Default is `10080` blocks."""

    def __init__(self) -> None:
        """Initialize a Monero hard fork info."""
        ...
