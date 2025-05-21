class MoneroMultisigInfo:
    """
    Models information about a multisig wallet.
    """
    is_multisig: bool
    """Indicates if the wallet is multisignature (`True`), or not (`False`)."""
    is_ready: bool
    num_participants: int
    """Number of participants of the multisignature wallet."""
    threshold: int
    """Number of participants need in order to sign a transaction."""
    def __init__(self) -> None:
        """Initialize a Monero multisignature info."""
        ...
