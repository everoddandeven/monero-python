from __future__ import annotations

import logging
from configparser import ConfigParser

import pytest

from utils import AddressBook, BaseTestClass, KeysBook

logger: logging.Logger = logging.getLogger("TestMoneroUtils")


class BaseTestMoneroUtils(BaseTestClass):
    """Monero utilities unit tests."""

    class Config:
        """Utils tests configuration."""
        mainnet: AddressBook = AddressBook()
        """Mainnet address book."""
        testnet: AddressBook = AddressBook()
        """Testnet address book."""
        stagenet: AddressBook = AddressBook()
        """Stagenet address book."""
        keys: KeysBook = KeysBook()
        """Wallet keys book."""
        serialization_msg: str = ''
        """Message to serialize."""

        @classmethod
        def parse(cls, parser: ConfigParser) -> BaseTestMoneroUtils.Config:
            """Parse utils tests configuration.

            :param ConfigParser parser: configuration parser.
            :returns BaseTestMoneroUtils.Config: parsed test utils configuration.
            """
            config: BaseTestMoneroUtils.Config = cls()
            # check section
            assert parser.has_section("serialization"), "Section [serialization] not found in test config"
            # load address books
            config.mainnet = AddressBook.parse(parser, "mainnet")
            config.testnet = AddressBook.parse(parser, "testnet")
            config.stagenet = AddressBook.parse(parser, "stagenet")
            # load keys book
            config.keys = KeysBook.parse(parser)
            config.serialization_msg = parser.get("serialization", "msg")
            return config

    @pytest.fixture(scope="class")
    @classmethod
    def config(cls) -> BaseTestMoneroUtils.Config:
        parser: ConfigParser = ConfigParser()
        parser.read('tests/config/test_monero_utils.ini')
        return BaseTestMoneroUtils.Config.parse(parser)
