import pytest
import logging

from monero import (
    MoneroTxQuery, MoneroTransferQuery, MoneroOutputQuery,
    MoneroWalletConfig, MoneroDestination, MoneroUtils,
    MoneroTxConfig
)
from utils import BaseTestClass, TestUtils, AssertUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModel")


@pytest.mark.unit
class TestMoneroWalletModel(BaseTestClass):
    """Test monero wallet data model."""

    #region Tests

    # Test output query expected behaviour
    def test_output_query(self) -> None:
        output_query = MoneroOutputQuery()
        tx_query: MoneroTxQuery = MoneroTxQuery()

        # test tx query property assign
        try:
            output_query.tx_query = tx_query # type: ignore
        except AttributeError as e:
            err_msg: str = str(e)
            assert "object has no setter" in err_msg, err_msg

        # assign tx query to output query
        output_query.set_tx_query(tx_query, True)

        assert output_query.tx_query is not None
        assert output_query.tx_query == tx_query
        assert tx_query.input_query is None
        assert tx_query.output_query is not None
        assert tx_query.output_query == output_query

        # reassign output query to tx query
        output_query.tx_query.output_query = output_query
        assert output_query.tx_query is not None
        assert output_query == output_query.tx_query.output_query

        # remove tx query from output query
        output_query.set_tx_query(None, True)

        assert output_query.tx_query is None
        assert tx_query.output_query is None

    # Test input query expected behaviour
    def test_input_query(self) -> None:
        input_query = MoneroOutputQuery()
        tx_query: MoneroTxQuery = MoneroTxQuery()

        # assign tx query to input query
        input_query.set_tx_query(tx_query, False)

        assert input_query.tx_query is not None
        assert input_query.tx_query == tx_query
        assert tx_query.output_query is None
        assert tx_query.input_query is not None
        assert tx_query.input_query == input_query

        # reassign input query to tx query
        input_query.tx_query.input_query = input_query
        assert input_query.tx_query is not None
        assert input_query == input_query.tx_query.input_query

        # remove tx query from input query
        input_query.set_tx_query(None, False)

        assert input_query.tx_query is None
        assert tx_query.input_query is None

    # Test transfer query expected behaviour
    def test_transfer_query(self) -> None:
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        tx_query: MoneroTxQuery = MoneroTxQuery()

        # assign tx query to transfer query
        transfer_query.tx_query = tx_query

        assert tx_query.transfer_query is not None
        assert tx_query.transfer_query == transfer_query

        # reassign transfer query to tx query
        transfer_query.tx_query.transfer_query = transfer_query
        assert transfer_query.tx_query is not None
        assert transfer_query == transfer_query.tx_query.transfer_query

        # remove tx query from transfer query
        transfer_query.tx_query = None

        assert tx_query.transfer_query is None

        transfer_query = MoneroTransferQuery()
        transfer_query.tx_query = MoneroTxQuery()

        # check incoming/outgoing
        assert transfer_query.incoming is None
        assert transfer_query.outgoing is None
        assert transfer_query.is_incoming() is None
        assert transfer_query.is_outgoing() is None

        # set incoming
        transfer_query.incoming = True
        assert transfer_query.is_incoming() is True
        assert transfer_query.outgoing is False
        assert transfer_query.is_outgoing() is False
        transfer_query.incoming = None

        # set outgoing
        transfer_query.outgoing = True
        assert transfer_query.is_outgoing() is True
        assert transfer_query.incoming is False
        assert transfer_query.is_incoming() is False

    # Test tx query expected behaviour
    def test_tx_query(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        input_query: MoneroOutputQuery = MoneroOutputQuery()

        # assign transfer query to tx query
        tx_query.transfer_query = transfer_query

        assert tx_query.transfer_query == transfer_query
        assert transfer_query.tx_query is not None
        assert transfer_query.tx_query == tx_query

        # remove transfer query from tx query
        tx_query.transfer_query = None

        assert tx_query.transfer_query != transfer_query
        assert transfer_query.tx_query is None

        # assign output query to tx query
        tx_query.output_query = output_query

        assert tx_query.output_query == output_query
        assert output_query.tx_query is not None
        assert output_query.tx_query == tx_query

        # remove output query from tx query
        tx_query.output_query = None

        assert tx_query.output_query != output_query
        assert output_query.tx_query is None

        # assign input query to tx query
        tx_query.input_query = input_query

        assert tx_query.input_query == input_query
        assert input_query.tx_query is not None
        assert input_query.tx_query == tx_query

        # remove output query from tx query
        tx_query.input_query = None

        assert tx_query.input_query != input_query
        assert input_query.tx_query is None

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

        copy: MoneroTxConfig = config.copy()
        AssertUtils.assert_equals(config, copy)

        config_str: str = config.serialize()
        logger.debug(f"Serialized tx config: {config_str}")

        deserialized_config: MoneroTxConfig = MoneroTxConfig.deserialize(config_str)
        AssertUtils.assert_equals(config, deserialized_config)

    #endregion
