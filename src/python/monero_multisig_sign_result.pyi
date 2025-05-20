class MoneroMultisigSignResult:
    """
    Models the result of signing multisig tx hex.
    """
    signed_multisig_tx_hex: str | None
    tx_hashes: list[str]
    def __init__(self) -> None:
        ...
