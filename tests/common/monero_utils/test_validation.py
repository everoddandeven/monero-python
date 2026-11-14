from __future__ import annotations

import logging

import pytest
from monero import MoneroNetworkType, MoneroUtils

from utils import WalletUtils
from .base_test_monero_utils import BaseTestMoneroUtils

logger: logging.Logger = logging.getLogger("TestMoneroUtilsValidation")


@pytest.mark.unit
class TestMoneroUtilsValidation(BaseTestMoneroUtils):
    """Monero utilities validation unit tests."""

    # Can validate addresses
    def test_address_validation(self, config: BaseTestMoneroUtils.Config) -> None:

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
    def test_key_validation(self, config: BaseTestMoneroUtils.Config) -> None:
        invalid_hex_64: str = "z" * 64 # right length but not hex

        # test private view key validation
        assert MoneroUtils.is_valid_private_view_key(config.keys.private_view_key)
        MoneroUtils.validate_private_view_key(config.keys.private_view_key)
        WalletUtils.test_invalid_private_view_key("")
        WalletUtils.test_invalid_private_view_key(None)
        WalletUtils.test_invalid_private_view_key(config.keys.invalid_private_view_key)
        WalletUtils.test_invalid_private_view_key(invalid_hex_64)

        # test public view key validation
        assert MoneroUtils.is_valid_public_view_key(config.keys.public_view_key)
        MoneroUtils.validate_public_view_key(config.keys.public_view_key)
        WalletUtils.test_invalid_public_view_key("")
        WalletUtils.test_invalid_public_view_key(None)
        WalletUtils.test_invalid_public_view_key(config.keys.invalid_public_view_key)
        WalletUtils.test_invalid_public_view_key(invalid_hex_64)

        # test private spend key validation
        assert MoneroUtils.is_valid_private_spend_key(config.keys.private_spend_key)
        WalletUtils.test_invalid_private_spend_key("")
        WalletUtils.test_invalid_private_spend_key(None)
        WalletUtils.test_invalid_private_spend_key(config.keys.invalid_private_spend_key)
        WalletUtils.test_invalid_private_spend_key(invalid_hex_64)

        # test public spend key validation
        assert MoneroUtils.is_valid_public_spend_key(config.keys.public_spend_key)
        MoneroUtils.validate_public_spend_key(config.keys.public_spend_key)
        WalletUtils.test_invalid_public_spend_key("")
        WalletUtils.test_invalid_public_spend_key(None)
        WalletUtils.test_invalid_public_spend_key(config.keys.invalid_public_spend_key)
        WalletUtils.test_invalid_public_spend_key(invalid_hex_64)

    # Can validate seed
    def test_mnemonic_validation(self, config: BaseTestMoneroUtils.Config) -> None:

        # test valid seed
        MoneroUtils.validate_mnemonic(config.keys.seed)
        assert MoneroUtils.is_valid_mnemonic(config.keys.seed), f"Invalid seed: {config.keys.seed}"
        assert MoneroUtils.is_valid_mnemonic(config.keys.seed, "English"), f"Expected valid English seed: {config.keys.seed}"

        # test invalid seed language
        assert not MoneroUtils.is_valid_mnemonic(config.keys.seed, "Spanish"), f"Expected invalid Spanish seed: {config.keys.seed}"

        # test invalid seed
        assert not MoneroUtils.is_valid_mnemonic("invalid monero wallet seed")

        # test empty seed
        assert not MoneroUtils.is_valid_mnemonic("")

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

        # validate long payment id
        assert MoneroUtils.is_valid_payment_id("87fdf837b5e6a390ef35647e9842991c8434d5452ad1b0ab304e0fa65b9c9e14")

        invalid_payment_ids: list[str] = [
            "", "wijqwnn38y",
            "87fdf837b5e6a39", "3b5ac230d26661778",
            "304e0fa65b9c9e14304e0fa65b9c9e14",
            "z" * 16, "z" * 64
        ]

        for payment_id in invalid_payment_ids:
            assert not MoneroUtils.is_valid_payment_id(payment_id), f"Expected invalid payment id: {payment_id}"
            try:
                MoneroUtils.validate_payment_id(payment_id)
            except Exception as e:
                expected: str = "payment id expected to be 64 or 16 hex characters"
                e_str: str = str(e)
                assert expected == e_str, f"Expected error '{expected}', got {e_str}"

    # Can validate a long payment id specifically
    def test_payment_id_long_validation(self) -> None:
        long_payment_id: str = "87fdf837b5e6a390ef35647e9842991c8434d5452ad1b0ab304e0fa65b9c9e14"
        assert MoneroUtils.is_valid_payment_id_long(long_payment_id)

        short_payment_id: str = "87fdf837b5e6a390"
        assert not MoneroUtils.is_valid_payment_id_long(short_payment_id)

        invalid_payment_ids: list[str] = ["", "wijqwnn38y", long_payment_id[:-1]]

        for payment_id in invalid_payment_ids:
            assert not MoneroUtils.is_valid_payment_id_long(payment_id), f"Expected invalid long payment id: {payment_id}"

    # Can validate a short payment id specifically
    def test_payment_id_short_validation(self) -> None:
        short_payment_id: str = "87fdf837b5e6a390"
        assert MoneroUtils.is_valid_payment_id_short(short_payment_id)

        long_payment_id: str = "87fdf837b5e6a390ef35647e9842991c8434d5452ad1b0ab304e0fa65b9c9e14"
        assert not MoneroUtils.is_valid_payment_id_short(long_payment_id)

        invalid_payment_ids: list[str] = ["", "wijqwnn38y", short_payment_id[:-1]]

        for payment_id in invalid_payment_ids:
            assert not MoneroUtils.is_valid_payment_id_short(payment_id), f"Expected invalid short payment id: {payment_id}"

    # Can validate a long payment id, raising on failure
    def test_validate_payment_id_long(self) -> None:
        long_payment_id: str = "87fdf837b5e6a390ef35647e9842991c8434d5452ad1b0ab304e0fa65b9c9e14"
        MoneroUtils.validate_payment_id_long(long_payment_id)

        with pytest.raises(RuntimeError, match="Invalid long payment id"):
            MoneroUtils.validate_payment_id_long("87fdf837b5e6a390")  # too short

        with pytest.raises(RuntimeError, match="Invalid long payment id"):
            MoneroUtils.validate_payment_id_long("wijqwnn38y")  # not hex

    # Can validate a short payment id, raising on failure
    def test_validate_payment_id_short(self) -> None:
        short_payment_id: str = "87fdf837b5e6a390"
        MoneroUtils.validate_payment_id_short(short_payment_id)

        with pytest.raises(RuntimeError, match="Invalid short payment id"):
            MoneroUtils.validate_payment_id_short("87fdf837b5e6a390ef35647e9842991c8434d5452ad1b0ab304e0fa65b9c9e14")  # too long

        with pytest.raises(RuntimeError, match="Invalid short payment id"):
            MoneroUtils.validate_payment_id_short("wijqwnn38y")  # not hex
