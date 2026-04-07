import pytest
import logging

from typing import Optional
from monero import (
    MoneroConnectionManager, MoneroRpcConnection, MoneroConnectionPollType
)
from utils import (
    ConnectionChangeCollector, TestUtils as Utils,
    AssertUtils, RpcConnectionUtils
)

logger: logging.Logger = logging.getLogger("TestMoneroConnectionManager")


@pytest.mark.integration
class TestMoneroConnectionManager:
    """Connection manager integration tests"""

    OFFLINE_PROXY_URI: str = "127.0.0.1:9050"
    """Proxy used to simulate offline servers"""

    _cm: MoneroConnectionManager | None = None

    #region Fixtures

    # Setup and teardown of test class
    @pytest.fixture(scope="class", autouse=True)
    def global_setup_and_teardown(self):
        """Executed once before all tests"""
        self.before_all()
        yield
        self.after_all()

    # Before all tests
    def before_all(self) -> None:
        """Executed once before all tests"""
        logger.info(f"Setup test class {type(self).__name__}")
        self._cm = MoneroConnectionManager()

    # After all tests
    def after_all(self) -> None:
        """Executed once after all tests"""
        logger.info(f"Teardown test class {type(self).__name__}")
        if self._cm:
            self._cm.reset()
            logger.debug("Resetted connection manager")
        else:
            logger.warning("Test connection manager is not set!")

        Utils.RPC_WALLET_MANAGER.clear()

    # setup and teardown of each test
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    # test connnections fixture
    @pytest.fixture(scope="class")
    def connections(self) -> list[MoneroRpcConnection]:
        """Rpc connections used in connection manager tests."""
        return Utils.get_all_rpc_connections()

    # connection manager
    @pytest.fixture(scope="class")
    def connection_manager(self) -> MoneroConnectionManager:
        """Connection manager test instance."""
        if self._cm is None:
            self._cm = MoneroConnectionManager()
        return self._cm

    #endregion

    @pytest.mark.timeout(60 * 5)
    def test_connection_manager(self, connection_manager: MoneroConnectionManager, connections: list[MoneroRpcConnection]) -> None:
        # listen for changes
        listener = ConnectionChangeCollector()
        connection_manager.add_listener(listener)

        # add prioritized connections
        connection: Optional[MoneroRpcConnection]  = connections[4]
        assert connection is not None
        connection.priority = 1
        connection_manager.add_connection(connection)
        connection = connections[2]
        assert connection is not None
        connection.priority = 2
        connection_manager.add_connection(connection)
        connection = connections[3]
        assert connection is not None
        connection.priority = 2
        connection_manager.add_connection(connection)
        connection = connections[0]
        assert connection is not None
        # default priority is lowest
        connection_manager.add_connection(connection)
        connection = connections[1]
        assert connection is not None
        assert connection.uri is not None
        # test unauthenticated
        connection_manager.add_connection(MoneroRpcConnection(connection.uri, timeout=connection.timeout))

        # test connections and order
        ordered_connections: list[MoneroRpcConnection] = connection_manager.get_connections()
        RpcConnectionUtils.test_connections_and_order(ordered_connections, connections, True)

        # test getting connection by uri
        connection = connections[0]
        assert connection is not None
        assert connection.uri is not None
        assert connection_manager.has_connection(connection.uri)
        assert connection_manager.get_connection_by_uri(connection.uri) == connections[0]

        # test unknown connection
        num_expected_changes: int = 0
        connection_manager.set_connection(ordered_connections[0])
        assert connection_manager.is_connected() is None
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections

        # auto connect to the best available connection
        connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS)
        listener.wait_for_change(Utils.SYNC_PERIOD_IN_MS, "Waiting for auto connect to best available connection")
        assert connection_manager.is_connected()
        connection = connection_manager.get_connection()
        assert connection is not None
        assert connection.is_online()
        assert connection == connections[4]
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] == connection
        connection_manager.set_auto_switch(False)
        connection_manager.stop_polling()
        connection_manager.disconnect()
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] is None

        # start periodically checking connection without auto switch
        connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS, False)

        # connect to the best available connection in order of priority and response time
        connection = connection_manager.get_best_available_connection()
        connection_manager.set_connection(connection)
        assert connection == connections[4]
        assert connection.is_online()
        assert connection.is_authenticated()
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] == connection

        # test connections and order
        ordered_connections = connection_manager.get_connections()
        RpcConnectionUtils.test_connections_and_order(ordered_connections, connections, False)
        # TODO others should not ever connected
        #for i, connection in enumerate(ordered_connections):
        #    if i < 1:
        #        continue
        #    assert connection.is_online() is None

        # set proxies to simulate prioritized servers shutdown
        for i, conn in enumerate(connections):
            if i < 2:
                continue
            conn.proxy_uri = self.OFFLINE_PROXY_URI

        listener.wait_for_change(Utils.SYNC_PERIOD_IN_MS, "Simulating priotizized servers shut down")
        assert connection_manager.is_connected() is False, f"{connection_manager.get_connection().serialize()}"
        connection = connection_manager.get_connection()

        assert connection.is_online() is False
        assert connection.is_connected() is False
        assert connection.is_authenticated() is None
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] == connection_manager.get_connection()

        # test connection order
        ordered_connections = connection_manager.get_connections()
        RpcConnectionUtils.test_connections_order(ordered_connections, connections)

        # check all connections
        connection_manager.check_connections()

        # test connection order
        ordered_connections = connection_manager.get_connections()
        RpcConnectionUtils.test_connections_order(ordered_connections, connections)

        # test online and authentication status
        for i, ordered_connection in enumerate(ordered_connections):
            is_online = ordered_connection.is_online()
            is_authenticated = ordered_connection.is_authenticated()
            if i == 1 or i == 2:
                assert is_online
            else:
                assert is_online is False
            if i == 1:
                assert is_authenticated
            elif i == 2:
                assert is_authenticated is False
            else:
                assert is_authenticated is None

        # test auto switch when disconnected
        connection_manager.set_auto_switch(True)
        listener.wait_for_autoswitch(connection_manager, Utils.SYNC_PERIOD_IN_MS)
        connection = connection_manager.get_connection()
        conn_str = connection.serialize() if connection is not None else 'None' # type: ignore
        assert connection_manager.is_connected(), f"conn= {conn_str}"
        assert connection is not None
        assert connection.is_online()
        assert connection == connections[0]
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] == connection

        # test connection order
        ordered_connections = connection_manager.get_connections()
        assert ordered_connections[0] == connection
        assert ordered_connections[0] == connections[0]
        connection = connections[1]
        assert connection is not None
        assert ordered_connections[1].uri == connection.uri
        assert ordered_connections[2] == connections[4]
        assert ordered_connections[3] == connections[2]
        assert ordered_connections[4] == connections[3]

        # connect to specific endpoint without authentication
        connection = ordered_connections[1]
        assert connection.is_authenticated() is False
        connection_manager.set_connection(connection)
        assert connection_manager.is_connected() is False
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections

        # connect to specific endpoint with authentication
        ordered_connections[1].set_credentials("rpc_user", "abc123")
        connection_manager.check_connection()
        cm_connection: MoneroRpcConnection = connection_manager.get_connection()
        assert cm_connection is not None
        assert cm_connection.uri == connections[1].uri
        assert connection.is_online()
        assert connection.is_authenticated()
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] == connection

        # test connection order
        ordered_connections = connection_manager.get_connections()
        assert ordered_connections[0] == connection_manager.get_connection()
        connection = connections[1]
        assert connection is not None
        assert ordered_connections[0].uri == connection.uri
        assert ordered_connections[1] == connections[0]
        assert ordered_connections[2] == connections[4]
        assert ordered_connections[3] == connections[2]
        assert ordered_connections[4] == connections[3]

        first: bool = True
        for i, ordered_connection in enumerate(ordered_connections):
            if i == len(ordered_connections) - 1:
                break
            if i <= 1:
                assert ordered_connection.is_online() if first else not ordered_connection.is_online()

        assert ordered_connections[4].is_online() is False

        # set connection to existing uri
        connection = connections[0]
        assert connection is not None
        connection_manager.set_connection(connection.uri)
        assert connection_manager.is_connected() is True
        assert connections[0] == connection_manager.get_connection()
        connection = connection_manager.get_connection()
        assert connection is not None
        assert Utils.DAEMON_RPC_USERNAME == connection.username
        assert Utils.DAEMON_RPC_PASSWORD == connection.password
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        AssertUtils.assert_equals(listener.changed_connections[-1], connections[0])

        # set connection to new uri
        connection_manager.stop_polling()
        uri: str = "http:#localhost:49999"
        connection_manager.set_connection(uri)
        connection = connection_manager.get_connection()
        assert connection is not None
        assert uri == connection.uri
        connection.timeout = Utils.AUTO_CONNECT_TIMEOUT_MS
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        connection = listener.changed_connections[-1]
        assert connection is not None
        assert uri == connection.uri

        # set connection to empty string
        connection_manager.set_connection("")
        assert connection_manager.get_connection() is None
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections

        # check all connections and test auto switch
        connection_manager.check_connections()
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert connection_manager.is_connected()

        # remove current connection and test auto switch
        connection = connection_manager.get_connection()
        assert connection is not None
        assert connection.uri is not None
        connection_manager.remove_connection(connection.uri)
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert connection_manager.is_connected() is False
        connection_manager.check_connections()
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert connection_manager.is_connected()

        # test polling current connection
        connection_manager.set_connection(None)
        assert connection_manager.is_connected() is False
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        connection_manager.start_polling(
            period_ms=Utils.SYNC_PERIOD_IN_MS,
            poll_type=MoneroConnectionPollType.CURRENT
        )

        listener.wait_for_change(Utils.SYNC_PERIOD_IN_MS, "Polling current connection")
        assert connection_manager.is_connected() is True
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections

        # test polling all connections
        connection_manager.set_connection(None)
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        connection_manager.start_polling(period_ms=Utils.SYNC_PERIOD_IN_MS, poll_type=MoneroConnectionPollType.ALL)
        listener.wait_for_change(Utils.SYNC_PERIOD_IN_MS, "Polling all connections")
        assert connection_manager.is_connected() is True
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections

        connection = connection_manager.get_connection()
        assert connection is not None
        # set proxies simulating shut down all connections
        for con in ordered_connections:
            con.proxy_uri = self.OFFLINE_PROXY_URI

        listener.wait_for_change(Utils.SYNC_PERIOD_IN_MS, "Simulating total shut down")
        assert connection.is_online() is False, f"Expected offline connection: {connection.serialize()}"
        num_expected_changes += 1
        assert num_expected_changes == listener.num_changed_connections
        assert listener.changed_connections[-1] == connection

        # reset
        connection_manager.reset()
        assert len(connection_manager.get_connections()) == 0
        assert connection_manager.get_connection() is None
