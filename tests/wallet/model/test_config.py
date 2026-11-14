from __future__ import annotations

import logging

import pytest
from monero import MoneroDestination, MoneroTxConfig, MoneroTxPriority, MoneroUtils, MoneroWalletConfig

from utils import AssertUtils, BaseTestClass, TestUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelConfig")


@pytest.mark.unit
class TestMoneroWalletModelConfig(BaseTestClass):
    """Wallet config model unit tests."""

    def test_destination(self) -> None:
        amount: int = MoneroUtils.xmr_to_atomic_units(1)
        dest: MoneroDestination = MoneroDestination(TestUtils.ADDRESS, amount)
        logger.debug(f"Testing destination: {dest.serialize()}")
        copy: MoneroDestination = dest.copy()
        AssertUtils.assert_equals(dest, copy)

    def test_wallet_config(self) -> None:
        config: MoneroWalletConfig = TestUtils.get_wallet_full_config(TestUtils.get_daemon_rpc_connection())
        logger.debug(f"Testing wallet config: {config.serialize()}")
        copy: MoneroWalletConfig = config.copy()
        AssertUtils.assert_equals(config, copy)
        config_str: str = config.serialize()
        deserialized_config: MoneroWalletConfig = MoneroWalletConfig.deserialize(config_str)
        logger.debug(f"Deserialized config: {deserialized_config.serialize()}")
        AssertUtils.assert_equals(config, deserialized_config)

    @pytest.mark.parametrize("json_fragment", ['{"networkType":-1}', '{"networkType":3}'])
    def test_wallet_config_invalid_network_type(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="Invalid network type"):
            MoneroWalletConfig.deserialize(json_fragment)

    def test_tx_config(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.set_address(TestUtils.ADDRESS)
        config.amount = MoneroUtils.xmr_to_atomic_units(0.5)
        config.account_index = 0
        config.subaddress_indices = [i for i in range(10)]
        config.below_amount = MoneroUtils.xmr_to_atomic_units(0.1)
        config.can_split = True
        config.fee = MoneroUtils.xmr_to_atomic_units(0.00075)
        config.sweep_each_subaddress = False
        config.priority = MoneroTxPriority.ELEVATED
        config.key_image = "a" * 64

        copy: MoneroTxConfig = config.copy()
        AssertUtils.assert_equals(config, copy)

        config_str: str = config.serialize()
        logger.debug(f"Serialized tx config: {config_str}")

        deserialized_config: MoneroTxConfig = MoneroTxConfig.deserialize(config_str)
        AssertUtils.assert_equals(config, deserialized_config)

    @pytest.mark.parametrize("priority,priority_num", [
        (MoneroTxPriority.DEFAULT, 0),
        (MoneroTxPriority.UNIMPORTANT, 1),
        (MoneroTxPriority.NORMAL, 2),
        (MoneroTxPriority.ELEVATED, 3),
    ])
    def test_tx_config_priority_deserialize(self, priority: MoneroTxPriority, priority_num: int) -> None:
        config: MoneroTxConfig = MoneroTxConfig.deserialize('{"priority": %d}' % priority_num)
        assert config.priority == priority

    def test_tx_config_invalid_priority_deserialize(self) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            MoneroTxConfig.deserialize('{"priority": 4}')
        assert str(exc_info.value) == "Invalid priority number: 4"

    def test_get_normalized_destinations_uses_destinations_when_address_and_amount_unset(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.destinations = [MoneroDestination(TestUtils.ADDRESS, 100), MoneroDestination(TestUtils.MINING_ADDRESS, 200)]
        assert config.get_normalized_destinations() == config.destinations

    def test_get_normalized_destinations_builds_single_destination(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = TestUtils.ADDRESS
        config.amount = 500000
        assert len(config.destinations) == 0  # address/amount alone don't populate destinations

        normalized: list[MoneroDestination] = config.get_normalized_destinations()
        assert len(normalized) == 1
        assert normalized[0].address == TestUtils.ADDRESS
        assert normalized[0].amount == 500000

    def test_get_normalized_destinations_conflicts_with_multiple_destinations(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = TestUtils.ADDRESS
        config.amount = 500000
        config.destinations = [MoneroDestination(TestUtils.ADDRESS, 500000), MoneroDestination(TestUtils.MINING_ADDRESS, 1)]
        with pytest.raises(RuntimeError) as exc_info:
            config.get_normalized_destinations()
        assert str(exc_info.value) == "Invalid tx configuration: single destination address/amount incompatible with multiple destinations"

    def test_get_normalized_destinations_address_mismatch(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = TestUtils.ADDRESS
        config.amount = 500000
        config.destinations = [MoneroDestination(TestUtils.MINING_ADDRESS, 500000)]
        with pytest.raises(RuntimeError) as exc_info:
            config.get_normalized_destinations()
        assert str(exc_info.value) == "Invalid tx configuration: single destination address does not match first destination address"

    def test_get_normalized_destinations_amount_mismatch(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = TestUtils.ADDRESS
        config.amount = 500000
        config.destinations = [MoneroDestination(TestUtils.ADDRESS, 1)]
        with pytest.raises(RuntimeError) as exc_info:
            config.get_normalized_destinations()
        assert str(exc_info.value) == "Invalid tx configuration: single destination amount does not match first destination amount"

    def test_get_normalized_destinations_matches_single_destination(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = TestUtils.ADDRESS
        config.amount = 500000
        config.destinations = [MoneroDestination(TestUtils.ADDRESS, 500000)]
        assert config.get_normalized_destinations() == config.destinations

    def test_destination_deserialize(self) -> None:
        destination: MoneroDestination = MoneroDestination(TestUtils.ADDRESS, 500000)
        AssertUtils.assert_serialization_integrity(destination)
