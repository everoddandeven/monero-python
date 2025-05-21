from .serializable_struct import SerializableStruct
from .monero_message_signature_type import MoneroMessageSignatureType


class MoneroMessageSignatureResult(SerializableStruct):
    """
    Models results from message verification.
    """
    is_good: bool
    """Indicates if the message verification was successfull."""
    is_old: bool
    """Indicates if the message verification used old monero software."""
    signature_type: MoneroMessageSignatureType
    """Signature type used in the message verification."""
    version: int
    """Message signature version."""
    def __init__(self) -> None:
        """Initialize a Monero message signature result."""
        ...
