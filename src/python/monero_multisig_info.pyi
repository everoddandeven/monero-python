from .serializable_struct import SerializableStruct


class MoneroMultisigInfo(SerializableStruct):
    """Models information about a multisig wallet."""

    is_multisig: bool
    """Indicates if the wallet is multisignature (`True`), or not (`False`)."""
    is_ready: bool
    """Indicates if the wallet is ready to support multisignature operations (`True`) or not (`False`)."""
    num_participants: int
    """Number of participants of the multisignature wallet."""
    threshold: int
    """Number of participants need in order to sign a transaction."""

    @staticmethod
    def deserialize(json: str) -> MoneroMultisigInfo:
        """
        Deserialize a MoneroMultisigInfo from a JSON string.

        :param str json: MoneroMultisigInfo in JSON format.
        :returns MoneroMultisigInfo: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero multisignature info."""
        ...
