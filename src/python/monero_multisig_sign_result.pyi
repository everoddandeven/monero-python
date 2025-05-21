class MoneroMultisigSignResult:
    """
    Models the result of signing multisig tx hex.
    """
    signed_multisig_tx_hex: str | None
    """Multisig transaction in hex format"""
    tx_hashes: list[str]
    """List of transaction hash"""
    def __init__(self) -> None:
        ...
