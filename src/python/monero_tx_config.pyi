import typing

from .serializable_struct import SerializableStruct
from .monero_destination import MoneroDestination
from .monero_tx_priority import MoneroTxPriority


class MoneroTxConfig(SerializableStruct):
    """Configures a transaction to send, sweep, or create a payment URI."""
    account_index: int | None
    """Account index to send funds from."""
    address: str | None
    """Transaction address destination."""
    amount: int | None
    """Transaction amount."""
    below_amount: int | None
    """Ignore output amount below."""
    can_split: bool | None
    """Indicates if transaction can be splitted in multiple transactions."""
    destinations: list[MoneroDestination]
    """Transaction outgoing destinations."""
    fee: int | None
    """Transaction fee."""
    key_image: str | None
    """Use a particular key image as input for transaction."""
    note: str | None
    """Transaction note."""
    payment_id: str | None
    """Transaction payment id."""
    priority: MoneroTxPriority | None
    """Transaction priority."""
    recipient_name: str | None
    """Recipient name."""
    relay: bool | None
    """Indicates if transaction should be relayed (`True`) or not (`False`)."""
    ring_size: int | None
    """Transaction ring size"""
    subaddress_indices: list[int]
    """Account subaddresses indices to send funds from."""
    subtract_fee_from: list[int]
    """Subtract fee from outputs."""
    sweep_each_subaddress: bool | None
    """Sweep each wallet subbaddress."""
    @staticmethod
    def deserialize(config_json: str) -> MoneroTxConfig:
        """
        Deserialize tx config from JSON string.

        :param str config_json: tx config in JSON format.
        :returns MoneroTxConfig: deserialized tx config.
        """
        ...
    @typing.overload
    def __init__(self) -> None:
        """Initialize a new tx config."""
        ...
    @typing.overload
    def __init__(self, config: MoneroTxConfig) -> None:
        """
        Initialize a new tx config.

        :param MoneroTxConfig config: tx config to copy.
        """
        ...
    def copy(self) -> MoneroTxConfig:
        """
        Copy current tx config.

        :returns MoneroTxConfig: tx config copy.
        """
        ...
    def get_normalized_destinations(self) -> list[MoneroDestination]:
        """
        Get all destinations set in current tx config.

        :returns list[MoneroDestination]: normalized tx config destinations.
        """
        ...
    def set_address(self, address: str) -> None:
        """
        Set the address of a single-destination configuration.

        :param str address: the address to set for the single destination.
        """
        ...