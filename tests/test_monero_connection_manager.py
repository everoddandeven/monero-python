import pytest
import logging

from typing import Optional
from monero import (
    MoneroWallet, MoneroConnectionManager, MoneroRpcConnection, MoneroConnectionPollType
)
from utils import ConnectionChangeCollector, TestUtils as Utils, AssertUtils, GenUtils

logger: logging.Logger = logging.getLogger("TestMoneroConnectionManager")

# TODO enable connection manager tests
@pytest.mark.skip(reason="TODO")
@pytest.mark.integration
class TestMoneroConnectionManager:
    """Connection manager integration tests"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    def test_connection_manager(self):
        wallet_rpcs: list[MoneroWallet] = Utils.get_wallets("rpc")
        connection_manager: Optional[MoneroConnectionManager] = None
        try:
            i: int = 0

            # create connection manager
            connection_manager = MoneroConnectionManager()

            # listen for changes
            listener = ConnectionChangeCollector()
            connection_manager.add_listener(listener)

            # add prioritized connections
            connection: Optional[MoneroRpcConnection]  = wallet_rpcs[4].get_daemon_connection()
            assert connection is not None
            connection.priority = 1
            connection_manager.add_connection(connection)
            connection = wallet_rpcs[2].get_daemon_connection()
            assert connection is not None
            connection.priority = 2
            connection_manager.add_connection(connection)
            connection = wallet_rpcs[3].get_daemon_connection()
            assert connection is not None
            connection.priority = 2
            connection_manager.add_connection(connection)
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            connection_manager.add_connection(connection) # default priority is lowest
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert connection.uri is not None
            connection_manager.add_connection(MoneroRpcConnection(connection.uri)) # test unauthenticated

            # test connections and order
            ordered_connections: list[MoneroRpcConnection] = connection_manager.get_connections()
            assert ordered_connections[0] == wallet_rpcs[4].get_daemon_connection()
            assert ordered_connections[1] == wallet_rpcs[2].get_daemon_connection()
            assert ordered_connections[2] == wallet_rpcs[3].get_daemon_connection()
            assert ordered_connections[3] == wallet_rpcs[0].get_daemon_connection()
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert ordered_connections[4].uri == connection.uri

            for connection in ordered_connections:
                assert connection.is_online() is None

            # test getting connection by uri
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            assert connection.uri is not None
            assert connection_manager.has_connection(connection.uri)
            assert connection_manager.get_connection_by_uri(connection.uri) == wallet_rpcs[0].get_daemon_connection()

            # test unknown connection
            num_expected_changes: int = 0
            connection_manager.set_connection(ordered_connections[0])
            assert connection_manager.is_connected() is None
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()

            # auto connect to the best available connection
            connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS)
            GenUtils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            assert connection_manager.is_connected()
            connection = connection_manager.get_connection()
            assert connection is not None
            assert connection.is_online()
            assert connection == wallet_rpcs[4].get_daemon_connection()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert listener.changed_connections.get(listener.changed_connections.size() - 1) == connection
            connection_manager.set_auto_switch(False)
            connection_manager.stop_polling()
            connection_manager.disconnect()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert listener.changed_connections.get(listener.changed_connections.size() - 1) is None

            # start periodically checking connection without auto switch
            connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS, False)

            # connect to the best available connection in order of priority and response time
            connection = connection_manager.get_best_available_connection()
            connection_manager.set_connection(connection)
            assert connection == wallet_rpcs[4].get_daemon_connection()
            assert connection.is_online()
            assert connection.is_authenticated()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert listener.changed_connections.get(listener.changed_connections.size() - 1) == connection

            # test connections and order
            ordered_connections = connection_manager.get_connections()
            assert ordered_connections[0] == wallet_rpcs[4].get_daemon_connection()
            assert ordered_connections[1] == wallet_rpcs[2].get_daemon_connection()
            assert ordered_connections[2] == wallet_rpcs[3].get_daemon_connection()
            assert ordered_connections[3] == wallet_rpcs[0].get_daemon_connection()
            connection =  wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert ordered_connections[4].uri == connection.uri
            for orderedConnection in ordered_connections:
                assert orderedConnection.is_online() is None

            # check all connections
            connection_manager.check_connections()

            # test connection order
            ordered_connections = connection_manager.get_connections()
            assert ordered_connections[0] == wallet_rpcs[4].get_daemon_connection()
            assert ordered_connections[1] == wallet_rpcs[0].get_daemon_connection()
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert ordered_connections[2].uri == connection.uri
            assert ordered_connections[3] == wallet_rpcs[2].get_daemon_connection()
            assert ordered_connections[4] == wallet_rpcs[3].get_daemon_connection()

            # test online and authentication status
            for orderedConnection in ordered_connections:
                is_online = orderedConnection.is_online()
                is_authenticated = orderedConnection.is_authenticated()
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
                i += 1

            # test auto switch when disconnected
            connection_manager.set_auto_switch(True)
            GenUtils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
            assert connection_manager.is_connected()
            connection = connection_manager.get_connection()
            assert connection is not None
            assert connection.is_online()
            assert connection == wallet_rpcs[0].get_daemon_connection()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert listener.changed_connections.get(listener.changed_connections.size() - 1) == connection

            # test connection order
            ordered_connections = connection_manager.get_connections()
            assert ordered_connections[0] == connection
            assert ordered_connections[0] == wallet_rpcs[0].get_daemon_connection()
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert ordered_connections[1].uri == connection.uri
            assert ordered_connections[2] == wallet_rpcs[4].get_daemon_connection()
            assert ordered_connections[3] == wallet_rpcs[2].get_daemon_connection()
            assert ordered_connections[4] == wallet_rpcs[3].get_daemon_connection()

            # connect to specific endpoint without authentication
            connection = ordered_connections[1]
            assert connection.is_authenticated() is False
            connection_manager.set_connection(connection)
            assert connection_manager.is_connected() is False
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()

            # connect to specific endpoint with authentication
            ordered_connections[1].set_credentials("rpc_user", "abc123")
            connection_manager.check_connection()
            connection = connection_manager.get_connection()
            assert connection is not None
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert connection.uri == connection.uri
            assert connection.is_online()
            assert connection.is_authenticated()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert listener.changed_connections.get(listener.changed_connections.size() - 1) == connection

            # test connection order
            ordered_connections = connection_manager.get_connections()
            assert ordered_connections[0] == connection_manager.get_connection()
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            assert ordered_connections[0].uri == connection.uri
            assert ordered_connections[1] == wallet_rpcs[0].get_daemon_connection()
            assert ordered_connections[2] == wallet_rpcs[4].get_daemon_connection()
            assert ordered_connections[3] == wallet_rpcs[2].get_daemon_connection()
            assert ordered_connections[4] == wallet_rpcs[3].get_daemon_connection()

            first: bool = True
            for orderedConnection in ordered_connections:
                if i <= 1:
                    assert orderedConnection.is_online() if first else not orderedConnection.is_online()

            assert ordered_connections[4].is_online() is False

            # set connection to existing uri
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            connection_manager.set_connection(connection.uri)
            assert connection_manager.is_connected() is True
            assert wallet_rpcs[0].get_daemon_connection() == connection_manager.get_connection()
            connection = connection_manager.get_connection()
            assert connection is not None
            assert Utils.WALLET_RPC_USERNAME == connection.username
            assert Utils.WALLET_RPC_PASSWORD == connection.password
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            AssertUtils.assert_equals(
                listener.changed_connections.get(listener.changed_connections.size() - 1),
                wallet_rpcs[0].get_daemon_connection()
            )

            # set connection to new uri
            connection_manager.stop_polling()
            uri: str = "http:#localhost:49999"
            connection_manager.set_connection(uri)
            connection = connection_manager.get_connection()
            assert connection is not None
            assert uri == connection.uri
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            connection = listener.changed_connections.get(listener.changed_connections.size() -1)
            assert connection is not None
            assert uri == connection.uri

            # set connection to empty string
            connection_manager.set_connection("")
            assert connection_manager.get_connection() is None
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()

            # check all connections and test auto switch
            connection_manager.check_connections()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert connection_manager.is_connected()

            # remove current connection and test auto switch
            connection = connection_manager.get_connection()
            assert connection is not None
            assert connection.uri is not None
            connection_manager.remove_connection(connection.uri)
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert connection_manager.is_connected() is False
            connection_manager.check_connections()
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert connection_manager.is_connected()

            # test polling current connection
            connection_manager.set_connection(None)
            assert connection_manager.is_connected() is False
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            connection_manager.start_polling(
                period_ms=Utils.SYNC_PERIOD_IN_MS,
                poll_type=MoneroConnectionPollType.CURRENT
            )
            GenUtils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            assert connection_manager.is_connected() is True
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()

            # test polling all connections
            connection_manager.set_connection(None)
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            connection_manager.start_polling(period_ms=Utils.SYNC_PERIOD_IN_MS, poll_type=MoneroConnectionPollType.ALL)
            GenUtils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            assert connection_manager.is_connected() is True
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()

            # shut down all connections
            connection = connection_manager.get_connection()
            assert connection is not None

            GenUtils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
            assert connection.is_online() is False
            num_expected_changes += 1
            assert num_expected_changes == listener.changed_connections.size()
            assert listener.changed_connections.get(listener.changed_connections.size() - 1) == connection

            # reset
            connection_manager.reset()
            assert len(connection_manager.get_connections()) == 0
            assert connection_manager.get_connection() is None

        finally:
            # stop connection manager
            if connection_manager is not None:
                connection_manager.reset()
