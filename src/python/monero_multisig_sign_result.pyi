from .serializable_struct import SerializableStruct


class MoneroMultisigSignResult(SerializableStruct):
    """Models the result of signing multisig tx hex."""

    signed_multisig_tx_hex: str | None
    """Multisig transaction in hex format."""

    tx_hashes: list[str]
    """List of transaction hash."""

    @staticmethod
    def deserialize(json: str) -> MoneroMultisigSignResult:
        """
        Deserialize a MoneroMultisigSignResult from a JSON string.

        :param str json: MoneroMultisigSignResult in JSON format.
        :returns MoneroMultisigSignResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero multisignature signature result."""
        ...
