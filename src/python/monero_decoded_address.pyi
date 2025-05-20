from .monero_address_type import MoneroAddressType
from .monero_network_type import MoneroNetworkType


class MoneroDecodedAddress:
    """
    Maintains metadata for a decoded address.
    """
    address: str
    address_type: MoneroAddressType
    network_type: MoneroNetworkType
    def __init__(self, address: str, address_type: MoneroAddressType, network_type: MoneroNetworkType) -> None:
        ...
