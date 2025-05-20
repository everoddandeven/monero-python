class MoneroFeeEstimate:
    """
    Models a Monero fee estimate.
    """
    fee: int | None
    """Amount of fees estimated per byte in atomic-units."""
    fees: list[int]
    """Represents the base fees at different priorities `[slow, normal, fast, fastest]`."""
    quantization_mask: int | None
    """Final fee should be rounded up to an even multiple of this value."""
    def __init__(self) -> None:
        ...
