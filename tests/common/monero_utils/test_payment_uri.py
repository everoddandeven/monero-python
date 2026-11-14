from __future__ import annotations

import logging

import pytest
from monero import MoneroNetworkType, MoneroTxConfig, MoneroUtils

from utils import WalletUtils
from .base_test_monero_utils import BaseTestMoneroUtils

logger: logging.Logger = logging.getLogger("TestMoneroUtilsPaymentUri")


@pytest.mark.unit
class TestMoneroUtilsPaymentUri(BaseTestMoneroUtils):
    """Monero utilities payment uri unit tests."""

    # Can get payment uri
    def test_get_payment_uri(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        payment_uri: str = MoneroUtils.get_payment_uri(tx_config)
        query: str = "tx_amount=0.250000000000&recipient_name=John%20Doe&tx_description=My%20transfer%20to%20wallet"
        logger.debug(f"Testing payment uri: {payment_uri}")
        assert payment_uri == f"monero:{address}?{query}"

    # Test invalid payment uri address network type
    def test_payment_uri_invalid_network_type(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.testnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        with pytest.raises(Exception) as exc_info:
            MoneroUtils.get_payment_uri(tx_config)

        # get_payment_uri() wraps make_uri()'s error with context, unlike e.g. validate_address()
        assert str(exc_info.value) == f"Cannot make URI from supplied parameters: wrong address: {address}"

    # Test deprecated standalone payment id
    def test_payment_uri_deprecated_payment_uri(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.testnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        tx_config.payment_id = "03284e41c342f03603284e41c342f03603284e41c342f03603284e41c342f036"
        with pytest.raises(Exception) as exc_info:
            MoneroUtils.get_payment_uri(tx_config, MoneroNetworkType.TESTNET)

        # get_payment_uri() wraps make_uri()'s error with context, unlike e.g. validate_address()
        assert str(exc_info.value) == "Cannot make URI from supplied parameters: Standalone payment id deprecated, use integrated address instead"

    # Test single payment id given with an integrated address
    def test_payment_uri_single_payment_id_with_integrated_address(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.integrated_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        tx_config.payment_id = "03284e41c342f03603284e41c342f03603284e41c342f03603284e41c342f036"
        with pytest.raises(Exception) as exc_info:
            MoneroUtils.get_payment_uri(tx_config)

        # get_payment_uri() wraps make_uri()'s error with context, unlike e.g. validate_address()
        assert str(exc_info.value) == "Cannot make URI from supplied parameters: A single payment id is allowed"

    # Can parse a payment uri without any query string
    def test_parse_payment_uri_no_query(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        parsed: MoneroTxConfig = MoneroUtils.parse_payment_uri(f"monero:{address}")
        assert parsed.destinations[0].address == address
        assert parsed.destinations[0].amount == 0
        assert parsed.recipient_name is None
        assert parsed.note is None
        assert parsed.payment_id is None

    # Can parse a payment uri with an empty query string
    def test_parse_payment_uri_empty_query(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        parsed: MoneroTxConfig = MoneroUtils.parse_payment_uri(f"monero:{address}?")
        assert parsed.destinations[0].address == address

    # Can parse a payment uri round trip built by get_payment_uri()
    def test_parse_payment_uri_round_trip(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        tx_config: MoneroTxConfig = WalletUtils.build_payment_uri_config(address)
        uri: str = MoneroUtils.get_payment_uri(tx_config)
        parsed: MoneroTxConfig = MoneroUtils.parse_payment_uri(uri)
        assert parsed.destinations[0].address == address
        assert parsed.destinations[0].amount == tx_config.amount
        assert parsed.recipient_name == tx_config.recipient_name
        assert parsed.note == tx_config.note

    # Payment uri must use the "monero:" scheme
    def test_parse_payment_uri_wrong_scheme(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"bitcoin:{address}")
        assert str(exc_info.value) == f'Error parsing URI: URI has wrong scheme (expected "monero:"): bitcoin:{address}'

    # Payment uri address must be valid
    def test_parse_payment_uri_wrong_address(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.invalid_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"monero:{address}")
        assert str(exc_info.value) == f"Error parsing URI: URI has wrong address: {address}"

    # Payment uri parameters must be "key=value" pairs
    def test_parse_payment_uri_malformed_parameter(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"monero:{address}?tx_amount")
        assert str(exc_info.value) == "Error parsing URI: URI has wrong parameter: tx_amount"

    # Payment uri parameters must not repeat
    def test_parse_payment_uri_duplicate_parameter(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"monero:{address}?tx_amount=1&tx_amount=2")
        assert str(exc_info.value) == "Error parsing URI: URI has more than one instance of tx_amount"

    # Payment uri tx_amount must be a valid amount
    def test_parse_payment_uri_invalid_amount(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"monero:{address}?tx_amount=abc")
        assert str(exc_info.value) == "Error parsing URI: URI has invalid amount: abc"

    # Payment uri tx_payment_id must be a valid long payment id
    def test_parse_payment_uri_invalid_payment_id(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"monero:{address}?tx_payment_id=nothex")
        assert str(exc_info.value) == "Error parsing URI: Invalid payment id: nothex"

    # Payment uri can carry a separate, valid tx_payment_id for a non-integrated address
    def test_parse_payment_uri_valid_payment_id(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        payment_id: str = "a" * 64
        parsed: MoneroTxConfig = MoneroUtils.parse_payment_uri(f"monero:{address}?tx_payment_id={payment_id}")
        assert parsed.payment_id == payment_id

    # Payment uri must not combine a separate tx_payment_id with an integrated address
    def test_parse_payment_uri_separate_payment_id_with_integrated_address(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.integrated_1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.parse_payment_uri(f"monero:{address}?tx_payment_id={'a' * 64}")
        assert str(exc_info.value) == "Error parsing URI: Separate payment id given with an integrated address"

    # Unknown payment uri parameters are silently discarded
    def test_parse_payment_uri_unknown_parameter(self, config: BaseTestMoneroUtils.Config) -> None:
        address: str = config.mainnet.primary_address_1
        parsed: MoneroTxConfig = MoneroUtils.parse_payment_uri(f"monero:{address}?foo=bar")
        assert parsed.destinations[0].address == address
