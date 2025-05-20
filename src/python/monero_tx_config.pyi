import typing

from .serializable_struct import SerializableStruct
from .monero_destination import MoneroDestination
from .monero_tx_priority import MoneroTxPriority


class MoneroTxConfig(SerializableStruct):
    """
    Configures a transaction to send, sweep, or create a payment URI.
    """
    account_index: int | None
    address: str | None
    amount: int | None
    below_amount: int | None
    can_split: bool | None
    destinations: list[MoneroDestination]
    fee: int | None
    key_image: str | None
    note: str | None
    payment_id: str | None
    priority: MoneroTxPriority | None
    recipient_name: str | None
    relay: bool | None
    ring_size: int | None
    subaddress_indices: list[int]
    subtract_fee_from: list[int]
    sweep_each_subaddress: bool | None
    @staticmethod
    def deserialize(config_json: str) -> MoneroTxConfig:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, config: MoneroTxConfig) -> None:
        ...
    def copy(self) -> MoneroTxConfig:
        ...
    def get_normalized_destinations(self) -> list[MoneroDestination]:
        ...
