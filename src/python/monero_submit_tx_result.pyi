class MoneroSubmitTxResult:
    """
    Models the result from submitting a tx to a daemon.
    """
    credits: int | None
    has_invalid_input: bool | None
    """Indicates if the transaction has an invalid input."""
    has_invalid_output: bool | None
    """Indicates if the transaction has an invalid output."""
    has_too_few_outputs: bool | None
    """Indicates if the transaction has too few outputs."""
    is_double_spend: bool | None
    """Indicates if the transaction is double spend."""
    is_fee_too_low: bool | None
    """Indicates if the transaction fee is too low."""
    is_good: bool | None
    """Indicates if the submission of the transaction was successfull."""
    is_mixin_too_low: bool | None
    """Indicates if the transaction mixin count is too low."""
    is_nonzero_unlock_time: bool | None
    is_overspend: bool | None
    """Indicates if the transaction uses more money than available"""
    is_relayed: bool | None
    """Indicates if the transaction has been relayed."""
    is_too_big: bool | None
    """Indicates if the transaction size is too big."""
    is_tx_extra_too_big: bool | None
    """Indicates if the transaction extra size is too big."""
    reason: str | None
    """Additional information. Currently empty or `Not relayed` if transaction was accepted but not relayed."""
    sanity_check_failed: bool | None
    """Indicates if the transaction sanity check has failed."""
    top_block_hash: str | None
    def __init__(self) -> None:
        ...
