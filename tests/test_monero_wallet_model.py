import pytest
import logging

from monero import MoneroTxQuery, MoneroTransferQuery, MoneroOutputQuery

logger: logging.Logger = logging.getLogger("TestMoneroWalletModel")


@pytest.mark.unit
class TestMoneroWalletModel:
    """Test monero wallet data model"""

    #region Fixtures

    # Setup and teardown of test class
    @pytest.fixture(scope="class", autouse=True)
    def global_setup_and_teardown(self):
        """Executed once before all tests"""
        logger.info(f"Setup test class {type(self).__name__}")
        yield
        logger.info(f"Teardown test class {type(self).__name__}")

    # setup and teardown of each tests
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    #endregion

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

    #endregion
