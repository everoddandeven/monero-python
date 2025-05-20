class MoneroMultisigInfo:
    """
    Models information about a multisig wallet.
    """
    is_multisig: bool
    is_ready: bool
    num_participants: int
    threshold: int
    def __init__(self) -> None:
        ...
