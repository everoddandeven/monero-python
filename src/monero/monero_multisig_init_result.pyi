from .serializable_struct import SerializableStruct


class MoneroMultisigInitResult(SerializableStruct):
    """
    Models the result of initializing a multisig wallet which results in the
    multisig wallet's address xor another multisig hex to share with
    participants to create the wallet.
    """

    address: str | None
    """The multisignature wallet address."""
    multisig_hex: str | None
    """The multisignature hex to share with other participants."""

    @staticmethod
    def deserialize(json: str) -> MoneroMultisigInitResult:
        """
        Deserialize a MoneroMultisigInitResult from a JSON string.

        :param str json: MoneroMultisigInitResult in JSON format.
        :returns MoneroMultisigInitResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero multisignature initializing result."""
        ...
