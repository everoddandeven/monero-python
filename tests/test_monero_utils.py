from __future__ import annotations

import pytest
import logging
import subprocess
import sys
import gc

if sys.platform != "win32":
    import resource

from typing import Any
from configparser import ConfigParser
from monero import (
    MoneroNetworkType, MoneroIntegratedAddress, MoneroUtils, MoneroTxConfig,
    MoneroBlock, MoneroTxWallet, MoneroIncomingTransfer, MoneroOutputWallet,
    MoneroTx
)
from utils import AddressBook, KeysBook, WalletUtils, BaseTestClass, WalletErrorUtils

logger: logging.Logger = logging.getLogger("TestMoneroUtils")


@pytest.mark.unit
class TestMoneroUtils(BaseTestClass):
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
        def parse(cls, parser: ConfigParser) -> TestMoneroUtils.Config:
            """Parse utils tests configuration.

            :param ConfigParser parser: configuration parser.
            :returns TestMoneroUtils.Config: parsed test utils configuration.
            """
            config: TestMoneroUtils.Config = cls()
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

    #region Fixtures

    @pytest.fixture(scope="class")
    def config(self) -> TestMoneroUtils.Config:
        parser: ConfigParser = ConfigParser()
        parser.read('tests/config/test_monero_utils.ini')
        return TestMoneroUtils.Config.parse(parser)

    #endregion

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
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2

    # Can serialize heights with big numbers
    def test_serialize_heights_big(self) -> None:
        json_map: dict[Any, Any] = {
          "heights": [123456, 1234567, 870987]
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2

    # can serialize height with large unsigned values
    def test_serialize_large_unsigned_values(self) -> None:
        big_value: int = 18446744073709551615  # UINT64_MAX
        json_map: dict[Any, Any] = {
          "heights": [big_value]
        }
        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2
        assert json_map2["heights"][0] > 0, "uint64 > INT64_MAX must not serialize as negative"

    # Can serialize jsonMap with text
    def test_serialize_text_short(self, config: TestMoneroUtils.Config) -> None:
        assert config.serialization_msg is not None and config.serialization_msg != ""
        json_map: dict[Any, Any] = {
            "msg": config.serialization_msg
        }

        binary: bytes = MoneroUtils.dict_to_binary(json_map)
        assert len(binary) > 0

        json_map2: dict[Any, Any] = MoneroUtils.binary_to_dict(binary)
        assert json_map == json_map2

    # Can serialize json with long text
    def test_serialize_text_long(self, config: TestMoneroUtils.Config) -> None:
        msg: str = config.serialization_msg
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
        assert len(binary) > 0

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
        assert MoneroUtils.is_valid_private_view_key(config.keys.private_view_key)
        MoneroUtils.validate_private_view_key(config.keys.private_view_key)
        WalletUtils.test_invalid_private_view_key("")
        WalletUtils.test_invalid_private_view_key(None)
        WalletUtils.test_invalid_private_view_key(config.keys.invalid_private_view_key)

        # test public view key validation
        assert MoneroUtils.is_valid_public_view_key(config.keys.public_view_key)
        MoneroUtils.validate_public_view_key(config.keys.public_view_key)
        WalletUtils.test_invalid_public_view_key("")
        WalletUtils.test_invalid_public_view_key(None)
        WalletUtils.test_invalid_public_view_key(config.keys.invalid_public_view_key)

        # test private spend key validation
        assert MoneroUtils.is_valid_private_spend_key(config.keys.private_spend_key)
        WalletUtils.test_invalid_private_spend_key("")
        WalletUtils.test_invalid_private_spend_key(None)
        WalletUtils.test_invalid_private_spend_key(config.keys.invalid_private_spend_key)

        # test public spend key validation
        assert MoneroUtils.is_valid_public_spend_key(config.keys.public_spend_key)
        MoneroUtils.validate_public_spend_key(config.keys.public_spend_key)
        WalletUtils.test_invalid_public_spend_key("")
        WalletUtils.test_invalid_public_spend_key(None)
        WalletUtils.test_invalid_public_spend_key(config.keys.invalid_public_spend_key)

    # Can validate seed
    def test_mnemonic_validation(self, config: TestMoneroUtils.Config) -> None:

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
            "304e0fa65b9c9e14304e0fa65b9c9e14"
        ]

        for payment_id in invalid_payment_ids:
            assert not MoneroUtils.is_valid_payment_id(payment_id), f"Expected invalid payment id: {payment_id}"
            try:
                MoneroUtils.validate_payment_id(payment_id)
            except Exception as e:
                expected: str = "payment id expected to be 64 or 16 hex characters"
                e_str: str = str(e)
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

    # xmr_to_atomic_units(0.0) and negative zero are valid, not errors
    def test_xmr_to_atomic_units_zero(self) -> None:
        assert 0 == MoneroUtils.xmr_to_atomic_units(0.0)
        # -0.0 < 0 is False in IEEE 754, so it must not be rejected by the
        # "amount must be non-negative" check
        assert 0 == MoneroUtils.xmr_to_atomic_units(-0.0)

    # Amounts smaller than half an atomic unit (1e-12 XMR) round down to 0
    def test_xmr_to_atomic_units_rounds_down_to_zero(self) -> None:
        assert 0 == MoneroUtils.xmr_to_atomic_units(1e-13)
        assert 0 == MoneroUtils.xmr_to_atomic_units(4e-13)

    # xmr_to_atomic_units() rounds the underlying long double * 1e12 product to
    # the nearest atomic unit (away from zero on an exact .5). Decimal literals
    # ending in .5e-12 are not necessarily exact halves once represented as a
    # double, so which way they round depends on whether the closest double is
    # a hair above or below the nominal decimal value, and that itself can
    # depend on the platform's "long double" precision (80-bit extended on
    # x86_64 Linux/glibc, but identical to a plain 64-bit double on Apple
    # Silicon/macOS), so the same literal can round differently on different
    # platforms. This is inherent to IEEE 754, not an inconsistency in
    # xmr_to_atomic_units() itself, assert the result lands on one of the
    # two atomic units the value sits between, not a specific platform's tie-break.
    def test_xmr_to_atomic_units_half_atomic_unit_rounding(self) -> None:
        cases: list[tuple[float, int, int]] = [
            (0.5e-12, 0, 1),
            (1.5e-12, 1, 2),
            (2.5e-12, 2, 3),
            (3.5e-12, 3, 4),
        ]
        for amount_xmr, floor_atomic, ceil_atomic in cases:
            actual: int = MoneroUtils.xmr_to_atomic_units(amount_xmr)
            logger.debug(f"xmr_to_atomic_units({amount_xmr!r}) = {actual} (expected {floor_atomic} or {ceil_atomic})")
            assert actual in (floor_atomic, ceil_atomic), f"xmr_to_atomic_units({amount_xmr!r}) == {actual}, expected {floor_atomic} or {ceil_atomic}"

    # amount_xmr must be finite and non-negative
    @pytest.mark.parametrize("amount_xmr", [-1.0, -0.0000000001, float("nan"), float("inf"), float("-inf")])
    def test_xmr_to_atomic_units_invalid_amount(self, amount_xmr: float) -> None:
        with pytest.raises(RuntimeError, match="amount must be a finite, non-negative number"):
            MoneroUtils.xmr_to_atomic_units(amount_xmr)

    # amounts whose rounded atomic-unit value would overflow uint64_t are rejected
    # rather than silently wrapping or invoking undefined behavior on the cast
    def test_xmr_to_atomic_units_overflow(self) -> None:
        # UINT64_MAX atomic units is ~18446744.0737... XMR; comfortably over that
        # (with margin for float imprecision) must raise
        with pytest.raises(RuntimeError, match="amount exceeds maximum representable atomic units"):
            MoneroUtils.xmr_to_atomic_units(18446745.0)
        with pytest.raises(RuntimeError, match="amount exceeds maximum representable atomic units"):
            MoneroUtils.xmr_to_atomic_units(2e22)

    # values comfortably below the uint64_t boundary succeed
    def test_xmr_to_atomic_units_near_uint64_max_boundary(self) -> None:
        uint64_max: int = 2 ** 64 - 1
        boundary_xmr: float = uint64_max / 1e12  # ~18446744.073709551615 XMR
        margin_xmr: float = 1.0

        safely_below: float = boundary_xmr - margin_xmr
        below: int = MoneroUtils.xmr_to_atomic_units(safely_below)
        logger.debug(f"xmr_to_atomic_units({safely_below!r}) = {below} (uint64_max = {uint64_max})")
        assert below <= uint64_max

        safely_above: float = boundary_xmr + margin_xmr
        with pytest.raises(RuntimeError, match="amount exceeds maximum representable atomic units"):
            MoneroUtils.xmr_to_atomic_units(safely_above)

    # Can get payment uri
    def test_get_payment_uri(self, config: TestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        payment_uri: str = MoneroUtils.get_payment_uri(tx_config)
        query: str = "tx_amount=0.250000000000&recipient_name=John%20Doe&tx_description=My%20transfer%20to%20wallet"
        logger.debug(f"Testing payment uri: {payment_uri}")
        assert payment_uri == f"monero:{address}?{query}"

    # Test invalid payment uri address network type
    def test_payment_uri_invalid_network_type(self, config: TestMoneroUtils.Config) -> None:
        address: str = config.testnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        try:
            MoneroUtils.get_payment_uri(tx_config)
            raise Exception("Should have failed")
        except Exception as e:
            WalletErrorUtils.test_invalid_address_error(e, address)

    # Test deprecated standalone payment id
    def test_payment_uri_deprecated_payment_uri(self, config: TestMoneroUtils.Config) -> None:
        address: str = config.testnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        tx_config.payment_id = "03284e41c342f03603284e41c342f03603284e41c342f03603284e41c342f036"
        try:
            MoneroUtils.get_payment_uri(tx_config, MoneroNetworkType.TESTNET)
            raise Exception("Should have failed")
        except Exception as e:
            WalletErrorUtils.test_deprecated_payment_id_error(e)

    # Can get version
    def test_get_version(self) -> None:
        version: str = MoneroUtils.get_version()
        logger.debug(f"Testing monero-python version: {version}")
        assert version != "", "Version is empty"

    # Can get ring size
    def test_get_ring_size(self) -> None:
        size: int = MoneroUtils.get_ring_size()
        assert size == 16

    #endregion

    #region Gather blocks

    def test_get_blocks_from_txs_dedup_and_order(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 100
        block2: MoneroBlock = MoneroBlock()
        block2.height = 200

        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx1.block = block1

        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        tx2.block = block2

        tx3: MoneroTxWallet = MoneroTxWallet()  # shares block1 with tx1
        tx3.hash = "c" * 64
        tx3.block = block1

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_txs([tx1, tx2, tx3])
        assert len(blocks) == 2  # block1 deduplicated despite appearing twice
        assert blocks[0] is block1  # blocks are returned in first-seen order
        assert blocks[1] is block2

    def test_get_blocks_from_txs_unconfirmed_placeholder(self) -> None:
        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        assert tx1.block is None and tx2.block is None

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_txs([tx1, tx2])

        # unconfirmed (blockless) txs are grouped under one shared placeholder block
        assert len(blocks) == 1
        placeholder: MoneroBlock = blocks[0]
        assert placeholder.height is None
        assert len(placeholder.txs) == 2

        # side effect: get_blocks_from_txs() mutates its inputs, attaching each
        # unconfirmed tx to the placeholder block it creates
        assert tx1.block is placeholder
        assert tx2.block is placeholder

    def test_get_blocks_from_txs_mixed_confirmed_and_unconfirmed(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        confirmed: MoneroTxWallet = MoneroTxWallet()
        confirmed.hash = "a" * 64
        confirmed.block = block

        unconfirmed1: MoneroTxWallet = MoneroTxWallet()
        unconfirmed1.hash = "b" * 64
        unconfirmed2: MoneroTxWallet = MoneroTxWallet()
        unconfirmed2.hash = "c" * 64

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_txs([confirmed, unconfirmed1, unconfirmed2])
        assert len(blocks) == 2  # the real block, plus one shared unconfirmed placeholder
        assert blocks[0] is block
        assert blocks[1].height is None
        assert unconfirmed1.block is unconfirmed2.block is blocks[1]

    def test_get_blocks_from_transfers_dedup_and_order(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 100
        block2: MoneroBlock = MoneroBlock()
        block2.height = 200

        t1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t1.tx = MoneroTxWallet()
        t1.tx.hash = "a" * 64
        t1.tx.block = block1

        t2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t2.tx = MoneroTxWallet()
        t2.tx.hash = "b" * 64
        t2.tx.block = block2

        t3: MoneroIncomingTransfer = MoneroIncomingTransfer()  # tx shares block1 with t1
        t3.tx = MoneroTxWallet()
        t3.tx.hash = "c" * 64
        t3.tx.block = block1

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_transfers([t1, t2, t3])
        assert len(blocks) == 2
        assert blocks[0] is block1
        assert blocks[1] is block2

    def test_get_blocks_from_transfers_unconfirmed_placeholder(self) -> None:
        t1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t1.tx = MoneroTxWallet()
        t1.tx.hash = "a" * 64
        t2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t2.tx = MoneroTxWallet()
        t2.tx.hash = "b" * 64
        assert t1.tx.block is None and t2.tx.block is None

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_transfers([t1, t2])
        assert len(blocks) == 1
        placeholder: MoneroBlock = blocks[0]
        assert placeholder.height is None

        # side effect: mutates transfer.tx.block, same as get_blocks_from_txs()
        assert t1.tx.block is placeholder
        assert t2.tx.block is placeholder

    @pytest.mark.xfail(reason="get_blocks_from_transfers() dereferences transfer.tx without a null check and segfaults the interpreter when it's unset", strict=True)
    def test_get_blocks_from_transfers_missing_tx_does_not_crash(self) -> None:
        # a transfer with no tx set is a legitimate, reachable state (it's just
        # never assigned), but get_blocks_from_transfers() used to dereference
        # transfer.tx unconditionally, causing a native segfault (SIGSEGV)
        # instead of raising a catchable Python exception. Run in an isolated
        # subprocess so a regression here only kills a throwaway process
        # instead of the whole test run; fixed upstream in the local
        # everoddandeven/monero-cpp checkout, pending a submodule bump.
        script: str = (
            "import monero\n"
            "t = monero.MoneroIncomingTransfer()\n"
            "t.amount = 500000\n"
            "monero.MoneroUtils.get_blocks_from_transfers([t])\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"get_blocks_from_transfers() crashed the interpreter (exit code {result.returncode}) "
            "instead of raising a Python exception for a transfer with no tx set"
        )

    def test_get_blocks_from_outputs_dedup_and_order(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 100
        block2: MoneroBlock = MoneroBlock()
        block2.height = 200

        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx1.block = block1
        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        tx2.block = block2

        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = tx1
        o2: MoneroOutputWallet = MoneroOutputWallet()
        o2.tx = tx2
        o3: MoneroOutputWallet = MoneroOutputWallet()  # tx shares block1 with o1
        o3.tx = tx1

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_outputs([o1, o2, o3])
        assert len(blocks) == 2
        assert blocks[0] is block1
        assert blocks[1] is block2

    def test_get_blocks_from_outputs_unconfirmed_raises(self) -> None:
        # unlike get_blocks_from_txs()/get_blocks_from_transfers(), an
        # unconfirmed (blockless) output's tx does not get a placeholder
        # block -- it raises instead
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.tx = MoneroTxWallet()
        output.tx.hash = "a" * 64
        assert output.tx.block is None

        with pytest.raises(RuntimeError, match="Need to handle unconfirmed output"):
            MoneroUtils.get_blocks_from_outputs([output])

    @pytest.mark.xfail(reason="get_blocks_from_outputs() bug", strict=True)
    def test_get_blocks_from_outputs_missing_tx_does_not_crash(self) -> None:
        # same crash as get_blocks_from_transfers(), for the same reason:
        # output.tx is a legitimate but unchecked null before the cast/dereference.
        script: str = (
            "import monero\n"
            "o = monero.MoneroOutputWallet()\n"
            "o.amount = 1000000\n"
            "monero.MoneroUtils.get_blocks_from_outputs([o])\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"get_blocks_from_outputs() crashed the interpreter (exit code {result.returncode}) "
            "instead of raising a Python exception for an output with no tx set"
        )

    #endregion

    #region Free memory

    def test_free_block_breaks_tx_backlink(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        MoneroUtils.free(block)
        assert tx.block is None

    def test_free_blocks_list(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 1
        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx1.block = block1
        block1.txs = [tx1]

        block2: MoneroBlock = MoneroBlock()
        block2.height = 2
        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        tx2.block = block2
        block2.txs = [tx2]

        MoneroUtils.free([block1, block2])
        assert tx1.block is None
        assert tx2.block is None

    def test_free_tx_without_block_does_not_crash(self) -> None:
        # free(tx) creates a throwaway placeholder block for an unconfirmed
        # tx, then immediately frees it. Net no-op on tx.block, but exercises
        # that code path safely
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        assert tx.block is None
        MoneroUtils.free(tx)
        assert tx.block is None

    def test_free_tx_with_block(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        MoneroUtils.free(tx)
        assert tx.block is None

    def test_free_txs_list_confirmed_and_unconfirmed(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        confirmed: MoneroTxWallet = MoneroTxWallet()
        confirmed.hash = "a" * 64
        confirmed.block = block
        block.txs = [confirmed]

        unconfirmed: MoneroTxWallet = MoneroTxWallet()
        unconfirmed.hash = "b" * 64

        MoneroUtils.free([confirmed, unconfirmed])
        assert confirmed.block is None
        assert unconfirmed.block is None

    def test_free_transfers_list(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.tx = tx

        MoneroUtils.free([transfer])
        assert transfer.tx.block is None

    def test_free_outputs_list(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        output: MoneroOutputWallet = MoneroOutputWallet()
        output.tx = tx

        MoneroUtils.free([output])
        assert output.tx.block is None

    @pytest.mark.skipif(sys.platform == "win32", reason="resource module (RSS measurement) is not available on Windows")
    def test_free_breaks_reference_cycle_avoids_leak(self) -> None:
        # regression guard for the leak demonstrated manually: building
        # block<->tx cycles and dropping every Python reference without
        # calling free() leaves the C++ shared_ptr cycle permanently
        # unreachable-but-alive (confirmed: 2,000,000 such tx objects grew
        # RSS by ~2.4GB with gc.collect() unable to reclaim any of it). This
        # test builds a much smaller-but-still-telling batch, always calling
        # free() before dropping references, and asserts memory stays roughly flat.
        def rss_mb() -> float:
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

        def run_batch(rounds: int) -> None:
            for _ in range(rounds):
                for _ in range(50):
                    block: MoneroBlock = MoneroBlock()
                    block.height = 100
                    txs: list[MoneroTx] = []
                    for i in range(20):
                        tx: MoneroTxWallet = MoneroTxWallet()
                        tx.hash = "a" * 63 + str(i % 10)
                        tx.block = block
                        txs.append(tx)
                    block.txs = txs
                    MoneroUtils.free(block)

        gc.disable()
        try:
            run_batch(20)  # unmeasured warmup: absorb one-time allocator growth
            baseline: float = rss_mb()
            run_batch(200)  # measured: 200 * 50 * 20 = 200,000 tx objects
            after: float = rss_mb()
        finally:
            gc.enable()

        growth_mb: float = after - baseline
        logger.debug(f"RSS growth after freeing 200,000 tx objects (post-warmup): {growth_mb:.1f} MB")
        # generous bound: a real leak of this shape grows ~1.2KB/tx (~240MB for
        # 200,000 tx); this only needs to rule out that magnitude of leak, not
        # pin down normal allocator noise
        assert growth_mb < 100, f"RSS grew {growth_mb:.1f} MB after freeing 200,000 tx objects -- possible leak"

    def test_free_none_does_not_crash(self) -> None:
        script: str = "import monero\nmonero.MoneroUtils.free(None)\n"
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"free(None) crashed the interpreter (exit code {result.returncode}) "
            "instead of raising a Python exception (or being a documented no-op)"
        )

    @pytest.mark.xfail(reason="free(transfers) delegates to get_blocks_from_transfers(), which segfaults on a transfer with no tx set", strict=True)
    def test_free_transfers_missing_tx_does_not_crash(self) -> None:
        script: str = (
            "import monero\n"
            "t = monero.MoneroIncomingTransfer()\n"
            "t.amount = 500000\n"
            "monero.MoneroUtils.free([t])\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"free([transfer]) crashed the interpreter (exit code {result.returncode}) "
            "instead of raising a Python exception for a transfer with no tx set"
        )

    @pytest.mark.xfail(reason="free(outputs) delegates to get_blocks_from_outputs(), which segfaults on an output with no tx set", strict=True)
    def test_free_outputs_missing_tx_does_not_crash(self) -> None:
        script: str = (
            "import monero\n"
            "o = monero.MoneroOutputWallet()\n"
            "o.amount = 1000000\n"
            "monero.MoneroUtils.free([o])\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"free([output]) crashed the interpreter (exit code {result.returncode}) "
            "instead of raising a Python exception for an output with no tx set"
        )

    #endregion
