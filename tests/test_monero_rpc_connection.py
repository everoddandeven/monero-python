import pytest # type: ignore

from monero import MoneroRpcConnection
from utils import MoneroTestUtils as Utils


class TestMoneroRpcConnection:

    # Test monerod rpc connection
    def test_node_rpc_connection(self):
        connection = MoneroRpcConnection(Utils.DAEMON_RPC_URI, Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)
        Utils.test_rpc_connection(connection, Utils.DAEMON_RPC_URI)
        assert connection.check_connection()
        assert connection.is_connected()
        assert connection.is_online()

    # Test wallet rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS is disabled")
    def test_wallet_rpc_connection(self):
        connection = MoneroRpcConnection(Utils.WALLET_RPC_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_RPC_PASSWORD)
        Utils.test_rpc_connection(connection, Utils.WALLET_RPC_URI)
        assert connection.check_connection()
        assert connection.is_connected()
        assert connection.is_online()
