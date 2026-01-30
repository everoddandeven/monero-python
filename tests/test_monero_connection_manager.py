import pytest
import logging

from typing import Optional
from monero import (
    MoneroWallet, MoneroConnectionManager, MoneroRpcConnection, MoneroConnectionPollType
)
from utils import ConnectionChangeCollector, TestUtils as Utils, AssertUtils, GenUtils

logger: logging.Logger = logging.getLogger("TestMoneroConnectionManager")

# TODO enable connection manager tests
@pytest.mark.skipif(True, reason="TODO")
class TestMoneroConnectionManager:

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
            AssertUtils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[1] == wallet_rpcs[2].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[2] == wallet_rpcs[3].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[3] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            AssertUtils.assert_equals(ordered_connections[4].uri, connection.uri)

            for connection in ordered_connections:
                assert connection.is_online() is None

            # test getting connection by uri
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            assert connection.uri is not None
            AssertUtils.assert_true(connection_manager.has_connection(connection.uri))
            AssertUtils.assert_true(
                connection_manager.get_connection_by_uri(connection.uri) == wallet_rpcs[0].get_daemon_connection()
            )

            # test unknown connection
            num_expected_changes: int = 0
            connection_manager.set_connection(ordered_connections[0])
            AssertUtils.assert_equals(None, connection_manager.is_connected())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # auto connect to the best available connection
            connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS)
            GenUtils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            AssertUtils.assert_true(connection_manager.is_connected())
            connection = connection_manager.get_connection()
            assert connection is not None
            AssertUtils.assert_true(connection.is_online())
            AssertUtils.assert_true(connection == wallet_rpcs[4].get_daemon_connection())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)
            connection_manager.set_auto_switch(False)
            connection_manager.stop_polling()
            connection_manager.disconnect()
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) is None)

            # start periodically checking connection without auto switch
            connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS, False)

            # connect to the best available connection in order of priority and response time
            connection = connection_manager.get_best_available_connection()
            connection_manager.set_connection(connection)
            AssertUtils.assert_true(connection == wallet_rpcs[4].get_daemon_connection())
            AssertUtils.assert_true(connection.is_online())
            AssertUtils.assert_true(connection.is_authenticated())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # test connections and order
            ordered_connections = connection_manager.get_connections()
            AssertUtils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[1] == wallet_rpcs[2].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[2] == wallet_rpcs[3].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[3] == wallet_rpcs[0].get_daemon_connection())
            connection =  wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            AssertUtils.assert_equals(ordered_connections[4].uri, connection.uri)
            for orderedConnection in ordered_connections:
                AssertUtils.assert_is_none(orderedConnection.is_online())

            # check all connections
            connection_manager.check_connections()

            # test connection order
            ordered_connections = connection_manager.get_connections()
            AssertUtils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[1] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            AssertUtils.assert_equals(ordered_connections[2].uri, connection.uri)
            AssertUtils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            # test online and authentication status
            for orderedConnection in ordered_connections:
                is_online = orderedConnection.is_online()
                is_authenticated = orderedConnection.is_authenticated()
                if i == 1 or i == 2:
                    AssertUtils.assert_true(is_online)
                else:
                    AssertUtils.assert_false(is_online)
                if i == 1:
                    AssertUtils.assert_true(is_authenticated)
                elif i == 2:
                    AssertUtils.assert_false(is_authenticated)
                else:
                    AssertUtils.assert_is_none(is_authenticated)
                i += 1

            # test auto switch when disconnected
            connection_manager.set_auto_switch(True)
            GenUtils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
            AssertUtils.assert_true(connection_manager.is_connected())
            connection = connection_manager.get_connection()
            assert connection is not None
            AssertUtils.assert_true(connection.is_online())
            AssertUtils.assert_true(connection == wallet_rpcs[0].get_daemon_connection())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # test connection order
            ordered_connections = connection_manager.get_connections()
            AssertUtils.assert_true(ordered_connections[0] == connection)
            AssertUtils.assert_true(ordered_connections[0] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            AssertUtils.assert_equals(ordered_connections[1].uri, connection.uri)
            AssertUtils.assert_true(ordered_connections[2] == wallet_rpcs[4].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            # connect to specific endpoint without authentication
            connection = ordered_connections[1]
            AssertUtils.assert_false(connection.is_authenticated())
            connection_manager.set_connection(connection)
            AssertUtils.assert_false(connection_manager.is_connected())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # connect to specific endpoint with authentication
            ordered_connections[1].set_credentials("rpc_user", "abc123")
            connection_manager.check_connection()
            connection = connection_manager.get_connection()
            assert connection is not None
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            AssertUtils.assert_equals(connection.uri, connection.uri)
            AssertUtils.assert_true(connection.is_online())
            AssertUtils.assert_true(connection.is_authenticated())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # test connection order
            ordered_connections = connection_manager.get_connections()
            AssertUtils.assert_true(ordered_connections[0] == connection_manager.get_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            AssertUtils.assert_equals(ordered_connections[0].uri, connection.uri)
            AssertUtils.assert_true(ordered_connections[1] == wallet_rpcs[0].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[2] == wallet_rpcs[4].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            AssertUtils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            first: bool = True
            for orderedConnection in ordered_connections:
                if i <= 1:
                    AssertUtils.assert_true(orderedConnection.is_online() if first else not orderedConnection.is_online() )

            AssertUtils.assert_false(ordered_connections[4].is_online())

            # set connection to existing uri
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            connection_manager.set_connection(connection.uri)
            AssertUtils.assert_true(connection_manager.is_connected())
            AssertUtils.assert_true(wallet_rpcs[0].get_daemon_connection() == connection_manager.get_connection())
            connection = connection_manager.get_connection()
            assert connection is not None
            AssertUtils.assert_equals(Utils.WALLET_RPC_USERNAME, connection.username)
            AssertUtils.assert_equals(Utils.WALLET_RPC_PASSWORD, connection.password)
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
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
            AssertUtils.assert_equals(uri, connection.uri)
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            connection = listener.changed_connections.get(listener.changed_connections.size() -1)
            assert connection is not None
            AssertUtils.assert_equals(uri, connection.uri)

            # set connection to empty string
            connection_manager.set_connection("")
            AssertUtils.assert_equals(None, connection_manager.get_connection())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # check all connections and test auto switch
            connection_manager.check_connections()
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(connection_manager.is_connected())

            # remove current connection and test auto switch
            connection = connection_manager.get_connection()
            assert connection is not None
            assert connection.uri is not None
            connection_manager.remove_connection(connection.uri)
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_false(connection_manager.is_connected())
            connection_manager.check_connections()
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(connection_manager.is_connected())

            # test polling current connection
            connection_manager.set_connection(None)
            AssertUtils.assert_false(connection_manager.is_connected())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            connection_manager.start_polling(
                period_ms=Utils.SYNC_PERIOD_IN_MS,
                poll_type=MoneroConnectionPollType.CURRENT
            )
            GenUtils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            AssertUtils.assert_true(connection_manager.is_connected())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # test polling all connections
            connection_manager.set_connection(None)
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            connection_manager.start_polling(period_ms=Utils.SYNC_PERIOD_IN_MS, poll_type=MoneroConnectionPollType.ALL)
            GenUtils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            AssertUtils.assert_true(connection_manager.is_connected())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # shut down all connections
            connection = connection_manager.get_connection()
            assert connection is not None

            GenUtils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
            AssertUtils.assert_false(connection.is_online())
            num_expected_changes += 1
            AssertUtils.assert_equals(num_expected_changes, listener.changed_connections.size())
            AssertUtils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # reset
            connection_manager.reset()
            AssertUtils.assert_equals(0, len(connection_manager.get_connections()))
            AssertUtils.assert_equals(None, connection_manager.get_connection())

        finally:
            # stop connection manager
            if connection_manager is not None:
                connection_manager.reset()

