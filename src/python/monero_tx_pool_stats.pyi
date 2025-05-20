class MoneroTxPoolStats:
    """
    Models transaction pool statistics.
    """
    bytes_max: int | None
    bytes_med: int | None
    bytes_min: int | None
    bytes_total: int | None
    fee_total: int | None
    histo98pc: int | None
    num10m: int | None
    num_double_spends: int | None
    num_failing: int | None
    num_not_relayed: int | None
    num_txs: int | None
    oldest_timestamp: int | None
    def __init__(self) -> None:
        ...
