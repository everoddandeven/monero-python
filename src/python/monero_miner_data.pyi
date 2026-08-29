from .monero_rpc_payment_info import MoneroRpcPaymentInfo
from .monero_tx import MoneroTx


class MoneroMinerData(MoneroRpcPaymentInfo):
    """Data needed to construct a block template for mining, e.g. for a pool that assembles its own block templates."""

    major_version: int | None
    """The next block's major version."""
    height: int | None
    """The height of the next block to mine."""
    prev_hash: str | None
    """The hash of the previous (current top) block."""
    seed_hash: str | None
    """The seed hash used to select the RandomX dataset/cache."""
    difficulty: str | None
    """The next block's difficulty as a hex string, e.g. "0x1f4"."""
    median_weight: int | None
    """The median block weight used for penalty calculations."""
    already_generated_coins: int | None
    """The total coins emitted so far, in atomic-units."""
    tx_pool_backlog: list[MoneroTx]
    """The transactions currently in the pool eligible for the next block."""

    @staticmethod
    def deserialize(json: str) -> MoneroMinerData:
        """
        Deserialize a MoneroMinerData from a JSON string.

        :param str json: MoneroMinerData in JSON format.
        :returns MoneroMinerData: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero miner data."""
        ...
