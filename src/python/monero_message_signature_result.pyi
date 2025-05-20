from .serializable_struct import SerializableStruct
from .monero_message_signature_type import MoneroMessageSignatureType


class MoneroMessageSignatureResult(SerializableStruct):
    """
    Models results from message verification.
    """
    is_good: bool
    is_old: bool
    signature_type: MoneroMessageSignatureType
    version: int
    def __init__(self) -> None:
        ...
