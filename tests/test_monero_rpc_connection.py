import pytest
import logging

from monero import MoneroRpcConnection
from utils import TestUtils as Utils

logger: logging.Logger = logging.getLogger("TestMoneroRpcConnection")


class TestMoneroRpcConnection:

    @pytest.fixture(autouse=True)
    def before_each(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    # Test monerod rpc connection
    def test_node_rpc_connection(self):
        connection = MoneroRpcConnection(Utils.DAEMON_RPC_URI, Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)
        Utils.test_rpc_connection(connection, Utils.DAEMON_RPC_URI)

    # Test wallet rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_wallet_rpc_connection(self):
        connection = MoneroRpcConnection(Utils.WALLET_RPC_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_RPC_PASSWORD)
        Utils.test_rpc_connection(connection, Utils.WALLET_RPC_URI)

    # Test invalid connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_invalid_connection(self):
        connection = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        Utils.test_rpc_connection(connection, Utils.OFFLINE_SERVER_URI, False)
