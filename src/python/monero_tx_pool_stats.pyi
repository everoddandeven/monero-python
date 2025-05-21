class MoneroTxPoolStats:
    """
    Models transaction pool statistics.
    """
    bytes_max: int | None
    """Max transaction size in pool."""
    bytes_med: int | None
    """Median transaction size in pool."""
    bytes_min: int | None
    """Min transaction size in pool."""
    bytes_total: int | None
    """Total size of all transactions in pool."""
    fee_total: int | None
    """The sum of the fees for all transactions currently in the transaction pool atomic-units."""
    histo98pc: int | None
    """The time 98% of txes are `younger` than."""
    num10m: int | None
    """Number of transactions in pool for more than 10 minutes."""
    num_double_spends: int | None
    """Number of double spend transactions."""
    num_failing: int | None
    """Number of failing transactions."""
    num_not_relayed: int | None
    """Number of non-relayed transactions."""
    num_txs: int | None
    """Total number of transactions."""
    oldest_timestamp: int | None
    """Unix time of the oldest transaction in the pool."""
    def __init__(self) -> None:
        ...
