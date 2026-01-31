from __future__ import annotations

import pytest
import logging

from typing import Any
from configparser import ConfigParser
from monero import (
    MoneroNetworkType, MoneroIntegratedAddress, MoneroUtils, MoneroTxConfig
)
from utils import AddressBook, KeysBook, AssertUtils, WalletUtils

logger: logging.Logger = logging.getLogger("TestMoneroUtils")


@pytest.mark.unit
class TestMoneroUtils:
    """Monero utilities unit tests"""

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

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    #region Tests

    # Can get integrated addresses
    def test_get_integrated_address(self, config: TestMoneroUtils.Config) -> None:
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
    def test_serialize_heights_small(self) -> None:
        json_map: dict[Any, Any] = {
          "heights": [111, 222, 333]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)

        AssertUtils.assert_true(len(binary) > 0)

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can serialize heights with big numbers
    def test_serialize_heights_big(self) -> None:
        json_map: dict[Any, Any] = {
          "heights": [123456, 1234567, 870987]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        AssertUtils.assert_true(len(binary) > 0)
        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can serialize jsonMap with text
    def test_serialize_text_short(self, config: TestMoneroUtils.Config) -> None:
        assert config.serialization_msg is not None and config.serialization_msg != ""
        json_map: dict[Any, Any] = {
            "msg": config.serialization_msg
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        AssertUtils.assert_true(len(binary) > 0)
        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can serialize json with long text
    def test_serialize_text_long(self, config: TestMoneroUtils.Config) -> None:
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
        AssertUtils.assert_true(len(binary) > 0)
        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)

        assert json_map == json_map2

    # Can validate addresses
    def test_address_validation(self, config: TestMoneroUtils.Config) -> None:

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
        WalletUtils.test_invalid_address(None, MoneroNetworkType.MAINNET)
        WalletUtils.test_invalid_address("", MoneroNetworkType.MAINNET)
        WalletUtils.test_invalid_address(config.mainnet.invalid_1, MoneroNetworkType.MAINNET)
        WalletUtils.test_invalid_address(config.mainnet.invalid_2, MoneroNetworkType.MAINNET)
        WalletUtils.test_invalid_address(config.mainnet.invalid_3, MoneroNetworkType.MAINNET)

        # test invalid addresses on testnet
        WalletUtils.test_invalid_address(None, MoneroNetworkType.TESTNET)
        WalletUtils.test_invalid_address("", MoneroNetworkType.TESTNET)
        WalletUtils.test_invalid_address(config.testnet.invalid_1, MoneroNetworkType.TESTNET)
        WalletUtils.test_invalid_address(config.testnet.invalid_2, MoneroNetworkType.TESTNET)
        WalletUtils.test_invalid_address(config.testnet.invalid_3, MoneroNetworkType.TESTNET)

        # test invalid addresses on stagenet
        WalletUtils.test_invalid_address(None, MoneroNetworkType.STAGENET)
        WalletUtils.test_invalid_address("", MoneroNetworkType.STAGENET)
        WalletUtils.test_invalid_address(config.stagenet.invalid_1, MoneroNetworkType.STAGENET)
        WalletUtils.test_invalid_address(config.stagenet.invalid_2, MoneroNetworkType.STAGENET)
        WalletUtils.test_invalid_address(config.stagenet.invalid_3, MoneroNetworkType.STAGENET)

    # Can validate keys
    def test_key_validation(self, config: TestMoneroUtils.Config) -> None:

        # test private view key validation
        AssertUtils.assert_true(MoneroUtils.is_valid_private_view_key(config.keys.private_view_key))
        WalletUtils.test_invalid_private_view_key("")
        WalletUtils.test_invalid_private_view_key(None)
        WalletUtils.test_invalid_private_view_key(config.keys.invalid_private_view_key)

        # test public view key validation
        AssertUtils.assert_true(MoneroUtils.is_valid_public_view_key(config.keys.public_view_key))
        WalletUtils.test_invalid_public_view_key("")
        WalletUtils.test_invalid_public_view_key(None)
        WalletUtils.test_invalid_public_view_key(config.keys.invalid_public_view_key)

        # test private spend key validation
        AssertUtils.assert_true(MoneroUtils.is_valid_private_spend_key(config.keys.private_spend_key))
        WalletUtils.test_invalid_private_spend_key("")
        WalletUtils.test_invalid_private_spend_key(None)
        WalletUtils.test_invalid_private_spend_key(config.keys.invalid_private_spend_key)

        # test public spend key validation
        AssertUtils.assert_true(MoneroUtils.is_valid_public_spend_key(config.keys.public_spend_key))
        WalletUtils.test_invalid_public_spend_key("")
        WalletUtils.test_invalid_public_spend_key(None)
        WalletUtils.test_invalid_public_spend_key(config.keys.invalid_public_spend_key)

    # Can validate seed
    def test_mnemonic_validation(self, config: TestMoneroUtils.Config) -> None:

        # test valid seed
        AssertUtils.assert_true(MoneroUtils.is_valid_mnemonic(config.keys.seed), f"Invalid seed: {config.keys.seed}")

        # test invalid seed
        AssertUtils.assert_false(MoneroUtils.is_valid_mnemonic("invalid monero wallet seed"))

        # test empty seed
        AssertUtils.assert_false(MoneroUtils.is_valid_mnemonic(""))

    # Can validate language
    def test_seed_language_validation(self) -> None:
        languages: list[str] = ["Italian", "English", "German"]

        for language in languages:
            assert MoneroUtils.is_valid_language(language), f"Expected valid language: {language}"

        invalid_languages: list[str] = ["", "english", "italian"]

        for language in invalid_languages:
            assert not MoneroUtils.is_valid_language(language), f"Expected invalid language: {language}"

    # Can validate payment id
    def test_payment_id_validation(self) -> None:
        payment_ids: list[str] = [
            "43e04076e176b768", "ef35647e9842991c",
            "8434d5452ad1b0ab", "3b5ac230d2666177",
            "87fdf837b5e6a390", "304e0fa65b9c9e14"
        ]

        for payment_id in payment_ids:
            assert MoneroUtils.is_valid_payment_id(payment_id), f"Expected valid payment id: {payment_id}"
            MoneroUtils.validate_payment_id(payment_id)

        invalid_payment_ids: list[str] = [
            "", "wijqwnn38y",
            "87fdf837b5e6a39", "3b5ac230d26661778",
            "304e0fa65b9c9e14304e0fa65b9c9e14"
        ]

        for payment_id in invalid_payment_ids:
            assert not MoneroUtils.is_valid_payment_id(payment_id), f"Expected invalid payment id: {payment_id}"
            try:
                MoneroUtils.validate_payment_id(payment_id)
            except Exception as e:
                expected = "Invalid payment id"
                e_str = str(e)
                assert expected == e_str, f"Expected error '{expected}', got {e_str}"

    # Can convert between XMR and atomic units
    def test_atomic_unit_conversion(self) -> None:
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
    def test_get_payment_uri(self, config: TestMoneroUtils.Config) -> None:
        address = config.mainnet.primary_address_1
        tx_config = MoneroTxConfig()
        tx_config.address = address
        tx_config.amount = 250000000000
        tx_config.recipient_name = "John Doe"
        tx_config.note = "My transfer to wallet"
        payment_uri = MoneroUtils.get_payment_uri(tx_config)
        query = "tx_amount=0.250000000000&recipient_name=John%20Doe&tx_description=My%20transfer%20to%20wallet"
        assert payment_uri == f"monero:{address}?{query}"

    # Can get version
    def test_get_version(self) -> None:
        version = MoneroUtils.get_version()
        assert version is not None, "Version is None"
        assert version != "", "Version is empty"

    # Can get ring size
    def test_get_ring_size(self) -> None:
        size = MoneroUtils.get_ring_size()
        # TODO why 12?
        assert size == 12

    # Can set log level
    def test_set_log_level(self) -> None:
        MoneroUtils.set_log_level(1)
        MoneroUtils.set_log_level(0)

    # Can configure logging
    def test_configure_logging(self) -> None:
        MoneroUtils.configure_logging("", False)

    #endregion
