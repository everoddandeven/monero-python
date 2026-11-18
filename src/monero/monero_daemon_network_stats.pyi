from .monero_rpc_payment_info import MoneroRpcPaymentInfo


class MoneroDaemonNetworkStats(MoneroRpcPaymentInfo):
    """Models daemon network (bandwidth) statistics since the daemon started."""

    start_time: int | None
    """Unix timestamp when the statistics window started."""
    total_packets_in: int | None
    """Total number of packets received."""
    total_bytes_in: int | None
    """Total number of bytes received."""
    total_packets_out: int | None
    """Total number of packets sent."""
    total_bytes_out: int | None
    """Total number of bytes sent."""

    @staticmethod
    def deserialize(json: str) -> MoneroDaemonNetworkStats:
        """
        Deserialize a MoneroDaemonNetworkStats from a JSON string.

        :param str json: MoneroDaemonNetworkStats in JSON format.
        :returns MoneroDaemonNetworkStats: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero daemon network stats."""
        ...
