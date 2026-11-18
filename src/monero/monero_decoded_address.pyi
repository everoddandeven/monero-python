from __future__ import annotations

import typing

from .serializable_struct import SerializableStruct
from .monero_address_type import MoneroAddressType
from .monero_network_type import MoneroNetworkType


class MoneroDecodedAddress(SerializableStruct):
    """Maintains metadata for a decoded address."""

    address: str
    """The decoded address."""
    address_type: MoneroAddressType
    """Type of the decoded address."""
    network_type: MoneroNetworkType
    """Network type of the decoded address."""

    @staticmethod
    def deserialize(json: str) -> MoneroDecodedAddress:
        """
        Deserialize a MoneroDecodedAddress from a JSON string.

        :param str json: MoneroDecodedAddress in JSON format.
        :returns MoneroDecodedAddress: deserialized instance.
        """
        ...

    @typing.overload
    def __init__(self) -> None:
        """Initialize an empty Monero decoded address."""
        ...

    @typing.overload
    def __init__(self, address: str, address_type: MoneroAddressType, network_type: MoneroNetworkType) -> None:
        """
        Initialize a Monero decoded address.

        :param str address: The decoded address.
        :param MoneroAddressType address_type: The type of the decoded address.
        :param MoneroNetworkType network_type: Network type of the decoded address.
        """
        ...
