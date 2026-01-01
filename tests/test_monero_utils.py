from __future__ import annotations
import pytest
from typing import Any
from configparser import ConfigParser
from monero import (
    MoneroNetworkType, MoneroIntegratedAddress, MoneroUtils, MoneroTxConfig
)
from utils import MoneroTestUtils, AddressBook, KeysBook


class TestMoneroUtils:

    class Config:
        mainnet: AddressBook = AddressBook()
        testnet: AddressBook = AddressBook()
        stagenet: AddressBook = AddressBook()
        keys: KeysBook = KeysBook()
        serialization_msg: str = ''
        
        @classmethod
        def parse(cls, parser: ConfigParser) -> TestMoneroUtils.Config:
            config = cls()
            if not parser.has_section("serialization"):
                raise Exception("Cannot find section [serialization] in test_monero_utils.ini")
            config.mainnet = AddressBook.parse(parser, "mainnet")
            config.testnet = AddressBook.parse(parser, "testnet")
            config.stagenet = AddressBook.parse(parser, "stagenet")
            config.keys = KeysBook.parse(parser)
            config.serialization_msg = parser.get("serialization", "msg")
            return config

    @pytest.fixture(scope="class")
    def config(self) -> TestMoneroUtils.Config:
        parser = ConfigParser()
        parser.read('tests/config/test_monero_utils.ini')
        return TestMoneroUtils.Config.parse(parser)

    # Can get integrated addresses
    def test_get_integrated_address(self, config: TestMoneroUtils.Config):
        primary_address: str = config.stagenet.primary_address_4
        subaddress: str = config.stagenet.subaddress_4
        payment_id: str = "03284e41c342f036"
        network_type: MoneroNetworkType = MoneroNetworkType.STAGENET

        # get integrated address with randomly generated payment id
        integrated_address: MoneroIntegratedAddress = MoneroUtils.get_integrated_address(network_type, primary_address, "")
        assert primary_address == integrated_address.standard_address
        assert 16 == len(integrated_address.payment_id)
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with specific payment id
        integrated_address = MoneroUtils.get_integrated_address(network_type, primary_address, payment_id)
        assert primary_address == integrated_address.standard_address
        assert payment_id == integrated_address.payment_id
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with subaddress
        integrated_address = MoneroUtils.get_integrated_address(network_type, subaddress, payment_id)
        assert subaddress == integrated_address.standard_address
        assert payment_id == integrated_address.payment_id
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with invalid payment id
        try:
          MoneroUtils.get_integrated_address(network_type, primary_address, "123")
          raise Exception("Getting integrated address with invalid payment id should have failed")
        except Exception as err:
          assert "Invalid payment id" == str(err)

    # Can serialize heights with small numbers
    def test_serialize_heights_small(self):
        json_map: dict[Any, Any] = {
          "heights": [111, 222, 333]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)

        MoneroTestUtils.assert_true(len(binary) > 0)

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can serialize heights with big numbers
    def test_serialize_heights_big(self):
        json_map: dict[Any, Any] = {
          "heights": [123456, 1234567, 870987]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        MoneroTestUtils.assert_true(len(binary) > 0)
        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can serialize jsonMap with text
    def test_serialize_text_short(self, config: TestMoneroUtils.Config):
        assert config.serialization_msg is not None and config.serialization_msg != ""
        json_map: dict[Any, Any] = {
            "msg": config.serialization_msg
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        MoneroTestUtils.assert_true(len(binary) > 0)
        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        
        assert json_map == json_map2

    # Can serialize json with long text
    def test_serialize_text_long(self, config: TestMoneroUtils.Config):
        msg = config.serialization_msg
        json_map: dict[str, str] = {
            "msg": f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n" +
                f"{msg}\n"
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        MoneroTestUtils.assert_true(len(binary) > 0)
        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can validate addresses
    def test_address_validation(self, config: TestMoneroUtils.Config):

        # test mainnet primary address validation
        assert (MoneroUtils.is_valid_address(config.mainnet.primary_address_1, MoneroNetworkType.MAINNET)) is True
        assert (MoneroUtils.is_valid_address(config.mainnet.primary_address_2, MoneroNetworkType.MAINNET)) is True
        assert (MoneroUtils.is_valid_address(config.mainnet.primary_address_3, MoneroNetworkType.MAINNET)) is True

        # test mainnet integrated address validation
        MoneroUtils.validate_address(config.mainnet.integrated_1, MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address(config.mainnet.integrated_2, MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address(config.mainnet.integrated_3, MoneroNetworkType.MAINNET)

        # test mainnet subaddress validation
        MoneroUtils.validate_address(config.mainnet.subaddress_1, MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address(config.mainnet.subaddress_2, MoneroNetworkType.MAINNET)
        MoneroUtils.validate_address(config.mainnet.subaddress_3, MoneroNetworkType.MAINNET)

        # test testnet primary address validation
        assert (MoneroUtils.is_valid_address(config.testnet.primary_address_1, MoneroNetworkType.TESTNET)) is True
        assert (MoneroUtils.is_valid_address(config.testnet.primary_address_2, MoneroNetworkType.TESTNET)) is True
        assert (MoneroUtils.is_valid_address(config.testnet.primary_address_3, MoneroNetworkType.TESTNET)) is True

        # test testnet integrated address validation
        assert (MoneroUtils.is_valid_address(config.testnet.integrated_1, MoneroNetworkType.TESTNET)) is True
        assert (MoneroUtils.is_valid_address(config.testnet.integrated_2, MoneroNetworkType.TESTNET)) is True
        assert (MoneroUtils.is_valid_address(config.testnet.integrated_3, MoneroNetworkType.TESTNET)) is True

        # test testnet subaddress validation
        assert (MoneroUtils.is_valid_address(config.testnet.subaddress_1, MoneroNetworkType.TESTNET)) is True
        assert (MoneroUtils.is_valid_address(config.testnet.subaddress_2, MoneroNetworkType.TESTNET)) is True
        assert (MoneroUtils.is_valid_address(config.testnet.subaddress_3, MoneroNetworkType.TESTNET)) is True

        # test stagenet primary address validation
        assert (MoneroUtils.is_valid_address(config.stagenet.primary_address_1, MoneroNetworkType.STAGENET)) is True
        assert (MoneroUtils.is_valid_address(config.stagenet.primary_address_2, MoneroNetworkType.STAGENET)) is True
        assert (MoneroUtils.is_valid_address(config.stagenet.primary_address_3, MoneroNetworkType.STAGENET)) is True

        # test stagenet integrated address validation
        assert (MoneroUtils.is_valid_address(config.stagenet.integrated_1, MoneroNetworkType.STAGENET)) is True
        assert (MoneroUtils.is_valid_address(config.stagenet.integrated_2, MoneroNetworkType.STAGENET)) is True
        assert (MoneroUtils.is_valid_address(config.stagenet.integrated_3, MoneroNetworkType.STAGENET)) is True

        # test stagenet subaddress validation
        assert (MoneroUtils.is_valid_address(config.stagenet.subaddress_1, MoneroNetworkType.STAGENET)) is True
        assert (MoneroUtils.is_valid_address(config.stagenet.subaddress_2, MoneroNetworkType.STAGENET)) is True
        assert (MoneroUtils.is_valid_address(config.stagenet.subaddress_3, MoneroNetworkType.STAGENET)) is True

        # test invalid addresses on mainnet
        MoneroTestUtils.test_invalid_address(None, MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address("", MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address(config.mainnet.invalid_1, MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address(config.mainnet.invalid_2, MoneroNetworkType.MAINNET)
        MoneroTestUtils.test_invalid_address(config.mainnet.invalid_3, MoneroNetworkType.MAINNET)

        # test invalid addresses on testnet
        MoneroTestUtils.test_invalid_address(None, MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address("", MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address(config.testnet.invalid_1, MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address(config.testnet.invalid_2, MoneroNetworkType.TESTNET)
        MoneroTestUtils.test_invalid_address(config.testnet.invalid_3, MoneroNetworkType.TESTNET)

        # test invalid addresses on stagenet
        MoneroTestUtils.test_invalid_address(None, MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address("", MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address(config.stagenet.invalid_1, MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address(config.stagenet.invalid_2, MoneroNetworkType.STAGENET)
        MoneroTestUtils.test_invalid_address(config.stagenet.invalid_3, MoneroNetworkType.STAGENET)

    # Can validate keys
    def test_key_validation(self, config: TestMoneroUtils.Config):

        # test private view key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_private_view_key(config.keys.private_view_key))
        MoneroTestUtils.test_invalid_private_view_key("")
        MoneroTestUtils.test_invalid_private_view_key(None)
        MoneroTestUtils.test_invalid_private_view_key(config.keys.invalid_private_view_key)

        # test public view key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_public_view_key(config.keys.public_view_key))
        MoneroTestUtils.test_invalid_public_view_key("")
        MoneroTestUtils.test_invalid_public_view_key(None)
        MoneroTestUtils.test_invalid_public_view_key(config.keys.invalid_public_view_key)

        # test private spend key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_private_spend_key(config.keys.private_spend_key))
        MoneroTestUtils.test_invalid_private_spend_key("")
        MoneroTestUtils.test_invalid_private_spend_key(None)
        MoneroTestUtils.test_invalid_private_spend_key(config.keys.invalid_private_spend_key)

        # test public spend key validation
        MoneroTestUtils.assert_true(MoneroUtils.is_valid_public_spend_key(config.keys.public_spend_key))
        MoneroTestUtils.test_invalid_public_spend_key("")
        MoneroTestUtils.test_invalid_public_spend_key(None)
        MoneroTestUtils.test_invalid_public_spend_key(config.keys.invalid_public_spend_key)

    # Can convert between XMR and atomic units
    def test_atomic_unit_conversion(self):
        assert 1000000000000 == MoneroUtils.xmr_to_atomic_units(1)
        assert 1 == MoneroUtils.atomic_units_to_xmr(1000000000000)
        assert 1000000000 == MoneroUtils.xmr_to_atomic_units(0.001)
        assert 0.001 == MoneroUtils.atomic_units_to_xmr(1000000000)
        assert 250000000000 == MoneroUtils.xmr_to_atomic_units(0.25)
        assert 0.25 == MoneroUtils.atomic_units_to_xmr(250000000000)
        assert 1250000000000 == MoneroUtils.xmr_to_atomic_units(1.25)
        assert 1.25 == MoneroUtils.atomic_units_to_xmr(1250000000000)
        assert 2796726190000 == MoneroUtils.xmr_to_atomic_units(2.79672619)
        assert 2.79672619 == MoneroUtils.atomic_units_to_xmr(2796726190000)
        assert 2796726190001 == MoneroUtils.xmr_to_atomic_units(2.796726190001)
        assert 2.796726190001 == MoneroUtils.atomic_units_to_xmr(2796726190001)
        assert 2796726189999 == MoneroUtils.xmr_to_atomic_units(2.796726189999)
        assert 2.796726189999 == MoneroUtils.atomic_units_to_xmr(2796726189999)
        assert 2796726180000 == MoneroUtils.xmr_to_atomic_units(2.79672618)
        assert 2.79672618 == MoneroUtils.atomic_units_to_xmr(2796726180000)

    # Can get payment uri
    def test_get_payment_uri(self, config: TestMoneroUtils.Config):
        address = config.mainnet.primary_address_1
        tx_config = MoneroTxConfig()
        tx_config.address = address
        tx_config.amount = 250000000000
        tx_config.recipient_name = "John Doe"
        tx_config.note = "My transfer to wallet"
        payment_uri = MoneroUtils.get_payment_uri(tx_config)
        query = "tx_amount=0.250000000000&recipient_name=John%20Doe&tx_description=My%20transfer%20to%20wallet"
        assert payment_uri == f"monero:{address}?{query}"
