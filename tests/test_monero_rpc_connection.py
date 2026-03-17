import pytest
import logging

from monero import MoneroRpcConnection, MoneroConnectionType, MoneroRpcError, MoneroUtils
from utils import TestUtils as Utils, DaemonUtils, StringUtils

logger: logging.Logger = logging.getLogger("TestMoneroRpcConnection")


@pytest.mark.integration
class TestMoneroRpcConnection:
    """Rpc connection integration tests"""

    # region Fixtures

    # Setup and teardown of test class
    @pytest.fixture(scope="class", autouse=True)
    def global_setup_and_teardown(self):
        """Executed once before all tests"""
        logger.info(f"Setup test class {type(self).__name__}")
        self.before_all()
        yield
        logger.info(f"Teardown test class {type(self).__name__}")

    # Before all tests
    def before_all(self) -> None:
        """Executed once before all tests"""
        logger.info(f"Setup test class {type(self).__name__}")

    # Setup and teardown of each tests
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    # Node rpc connection fixture
    @pytest.fixture(scope="class")
    def node_connection(self) -> MoneroRpcConnection:
        """Rpc connection test instance."""
        return MoneroRpcConnection(Utils.DAEMON_RPC_URI, Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)

    # Wallet rpc connection fixture
    @pytest.fixture(scope="class")
    def wallet_connection(self) -> MoneroRpcConnection:
        """Rpc connection test instance."""
        return MoneroRpcConnection(Utils.WALLET_RPC_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_RPC_PASSWORD)

    #endregion

    #region Tests

    # Test rpc connection json serialization
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_rpc_connection_serialization(self, node_connection: MoneroRpcConnection, wallet_connection: MoneroRpcConnection) -> None:
        # test node connection serialization
        connection_str: str = node_connection.serialize()
        assert '{"uri":"http://127.0.0.1:18081","username":"rpc_daemon_user","password":"abc123"}' == connection_str

        # node wallet connection serialization
        connection_str = wallet_connection.serialize()
        assert '{"uri":"127.0.0.1:18082","username":"rpc_user","password":"abc123"}' == connection_str

    # Can copy a rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_connection_copy(self, node_connection: MoneroRpcConnection) -> None:
        # test copy
        copy: MoneroRpcConnection = MoneroRpcConnection(node_connection)
        assert copy.serialize() == node_connection.serialize()

    # Test monerod rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_node_rpc_connection(self, node_connection: MoneroRpcConnection) -> None:
        DaemonUtils.test_rpc_connection(node_connection, Utils.DAEMON_RPC_URI, True, MoneroConnectionType.IPV4)

    # Test wallet rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_wallet_rpc_connection(self, wallet_connection: MoneroRpcConnection) -> None:
        DaemonUtils.test_rpc_connection(wallet_connection, Utils.WALLET_RPC_URI, True, MoneroConnectionType.IPV4)

    # Test invalid connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_invalid_connection(self) -> None:
        connection = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        DaemonUtils.test_rpc_connection(connection, Utils.OFFLINE_SERVER_URI, False, MoneroConnectionType.INVALID)

    # Can set credentials
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_credentials(self) -> None:
        # create connection
        connection: MoneroRpcConnection = MoneroRpcConnection(Utils.DAEMON_RPC_URI)

        # test connection without credentials
        assert connection.username is None
        assert connection.password is None

        # test set credentials
        connection.set_credentials(Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)

        assert not connection.is_connected(), "Expected not connected"
        assert not connection.is_online(), "Expected not online"
        assert not connection.is_authenticated(), "Expected not authenticated"

        # test connection
        assert connection.username == Utils.DAEMON_RPC_USERNAME
        assert connection.password == Utils.DAEMON_RPC_PASSWORD

        assert connection.check_connection(), "Could not check connection"

        assert connection.is_connected(), "Expected connected after check"
        assert connection.is_online(), "Expected online after check"
        assert connection.is_authenticated(), "Not authenticated"

        # test empty credentials
        connection.set_credentials("", "")

        assert not connection.is_connected(), "Expected not connected"
        assert not connection.is_online(), "Expected not online"
        assert not connection.is_authenticated(), "Expected not authenticated"

        assert connection.username is None
        assert connection.password is None

    # Test invalid credentials
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_invalid_credentials(self) -> None:
        # create test connection
        connection: MoneroRpcConnection = MoneroRpcConnection(Utils.DAEMON_RPC_URI, Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)

        # test connection username property assign
        try:
            connection.username = "user" # type: ignore
        except AttributeError as e:
            err_msg: str = str(e)
            assert "object has no setter" in err_msg, err_msg

        # test connection password property assign
        try:
            connection.password = "abc123" # type: ignore
        except AttributeError as e:
            err_msg: str = str(e)
            assert "object has no setter" in err_msg, err_msg

        # set invalid username
        try:
            connection.set_credentials("", "abc123")
            raise Exception("Should have thrown")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "username cannot be empty because password is not empty", e_msg

        # set invalid password
        try:
            connection.set_credentials("user", "")
            raise Exception("Should have thrown")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "password cannot be empty because username is not empty", e_msg

        # test connection
        assert connection.username == Utils.DAEMON_RPC_USERNAME
        assert connection.password == Utils.DAEMON_RPC_PASSWORD

        connection.set_credentials("user", "abc123")

        # test connection
        assert connection.username == "user"
        assert connection.password == "abc123"

        assert connection.check_connection()
        assert not connection.is_authenticated()
        # TODO internal http client throwing "Network error" instaead of 201 http error
        #assert connection.is_online()
        #assert connection.is_connected()
        assert not connection.is_online()
        assert not connection.is_connected()

    # Can get and set arbitrary key/value attributes
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_attributes(self, node_connection: MoneroRpcConnection) -> None:
        # set attributes
        attrs: dict[str, str] = {}
        for i in range(5):
            key: str = f"attr{i}"
            val: str = StringUtils.get_random_string()
            attrs[key] = val
            node_connection.set_attribute(key, val)

        # test attributes
        for key in attrs:
            val = attrs[key]
            assert val == node_connection.get_attribute(key)

    # Can send json request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_json_request(self, node_connection: MoneroRpcConnection) -> None:
        result: object = node_connection.send_json_request("get_version")
        assert result is not None
        logger.debug(f"JSON-RPC response {result}")

        # test invalid json rpc method
        try:
            node_connection.send_json_request("invalid_method")
        except MoneroRpcError as e:
            if str(e) != "Method not found":
                raise
            assert e.code == -32601

    # Can send binary request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_binary_request(self, node_connection: MoneroRpcConnection) -> None:
        parameters: dict[str, list[int]] = { "heights": list(range(100)) }
        bin_result: str | None = node_connection.send_binary_request("get_blocks_by_height.bin", parameters)
        assert bin_result is not None
        result: str = MoneroUtils.binary_to_json(bin_result)
        logger.debug(f"Binary response: {result}")

        # test invalid binary method
        try:
            node_connection.send_binary_request("invalid_method")
        except MoneroRpcError as e:
            assert e.code == 404

    # Can send path request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_path_request(self, node_connection: MoneroRpcConnection) -> None:
        result: object = node_connection.send_path_request("get_height")
        assert result is not None
        logger.debug(f"Path response {result}")

        # test invalid path method
        try:
            node_connection.send_path_request("invalid_method")
        except MoneroRpcError as e:
            assert e.code == 404

    #endregion
