class MoneroMultisigInitResult:
    """
    Models the result of initializing a multisig wallet which results in the
    multisig wallet's address xor another multisig hex to share with
    participants to create the wallet.
    """
    address: str | None
    multisig_hex: str | None
    def __init__(self) -> None:
        ...
