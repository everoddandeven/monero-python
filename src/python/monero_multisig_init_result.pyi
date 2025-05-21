class MoneroMultisigInitResult:
    """
    Models the result of initializing a multisig wallet which results in the
    multisig wallet's address xor another multisig hex to share with
    participants to create the wallet.
    """
    address: str | None
    """The multisignature wallet address."""
    multisig_hex: str | None
    """The multisignature hex to share with other participants."""
    def __init__(self) -> None:
        """Initialize a Monero multisignature initializing result."""
        ...
