from __future__ import annotations

from configparser import ConfigParser
from monero import MoneroNetworkType

from .daemon_utils import DaemonUtils


class AddressBook:
    """Address book to use in tests."""
    network_type: MoneroNetworkType = MoneroNetworkType.MAINNET
    primary_address_1: str = ""
    """First test primary address."""
    primary_address_2: str = ""
    """Second test primary address."""
    primary_address_3: str = ""
    """Third test primary address."""
    primary_address_4: str = ""
    """Fourth test primary address."""
    subaddress_1: str = ""
    """First test subaddress."""
    subaddress_2: str = ""
    """Second test subaddress."""
    subaddress_3: str = ""
    """Third test subaddress."""
    subaddress_4: str = ""
    """Fourth test subaddress."""
    integrated_1: str = ""
    integrated_2: str = ""
    integrated_3: str = ""
    integrated_4: str = ""
    invalid_1: str = ""
    """First invalid address."""
    invalid_2: str = ""
    """Second invalid address."""
    invalid_3: str = ""
    """Third invalid address."""

    @classmethod
    def parse(cls, parser: ConfigParser, section: str) -> AddressBook:
        """Parse address book configuration.

        :param ConfigParser parser: configuration parser.
        :param str section: configuration section to parse.
        :returns AddressBook: parsed address book.
        """
        if not parser.has_section(section):
            raise Exception(f"Cannot parse address book entry, invalid section '{section}'")
        entry = cls()
        entry.primary_address_1 = parser.get(section, 'primary_address_1')
        entry.primary_address_2 = parser.get(section, 'primary_address_2')
        entry.primary_address_3 = parser.get(section, 'primary_address_3')
        entry.primary_address_4 = parser.get(section, 'primary_address_4', fallback='')
        entry.subaddress_1 = parser.get(section, 'subaddress_1')
        entry.subaddress_2 = parser.get(section, 'subaddress_2')
        entry.subaddress_3 = parser.get(section, 'subaddress_3')
        entry.subaddress_4 = parser.get(section, 'subaddress_4', fallback='')
        entry.integrated_1 = parser.get(section, 'integrated_1')
        entry.integrated_2 = parser.get(section, 'integrated_2')
        entry.integrated_3 = parser.get(section, 'integrated_3')
        entry.integrated_4 = parser.get(section, 'integrated_4', fallback='')
        entry.invalid_1 = parser.get(section, 'invalid_1')
        entry.invalid_2 = parser.get(section, 'invalid_2')
        entry.invalid_3 = parser.get(section, 'invalid_3')
        entry.network_type = DaemonUtils.parse_network_type(section)
        return entry
