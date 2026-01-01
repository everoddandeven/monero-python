import pytest

from typing import Optional
from monero import (
    MoneroWalletRpc, MoneroConnectionManager, MoneroRpcConnection, MoneroConnectionPollType
)
from utils import ConnectionChangeCollector, MoneroTestUtils as Utils


# TODO enable connection manager tests
@pytest.mark.skipif(True, reason="TODO")
class TestMoneroConnectionManager:

    def test_connection_manager(self):
        wallet_rpcs: list[MoneroWalletRpc] = []
        connection_manager: Optional[MoneroConnectionManager] = None
        try:
            i: int = 0

            while i < 5:
                wallet_rpcs.append(Utils.start_wallet_rpc_process())
                i += 1
            # start monero-wallet-rpc instances as test server connections (can also use monerod servers)

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
            Utils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(ordered_connections[1] == wallet_rpcs[2].get_daemon_connection())
            Utils.assert_true(ordered_connections[2] == wallet_rpcs[3].get_daemon_connection())
            Utils.assert_true(ordered_connections[3] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(ordered_connections[4].uri, connection.uri)

            for connection in ordered_connections:
                assert connection.is_online() is None

            # test getting connection by uri
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            assert connection.uri is not None
            Utils.assert_true(connection_manager.has_connection(connection.uri))
            Utils.assert_true(
                connection_manager.get_connection_by_uri(connection.uri) == wallet_rpcs[0].get_daemon_connection()
            )

            # test unknown connection
            num_expected_changes: int = 0
            connection_manager.set_connection(ordered_connections[0])
            Utils.assert_equals(None, connection_manager.is_connected())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # auto connect to the best available connection
            connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS)
            Utils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            Utils.assert_true(connection_manager.is_connected())
            connection = connection_manager.get_connection()
            assert connection is not None
            Utils.assert_true(connection.is_online())
            Utils.assert_true(connection == wallet_rpcs[4].get_daemon_connection())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)
            connection_manager.set_auto_switch(False)
            connection_manager.stop_polling()
            connection_manager.disconnect()
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) is None)

            # start periodically checking connection without auto switch
            connection_manager.start_polling(Utils.SYNC_PERIOD_IN_MS, False)

            # connect to the best available connection in order of priority and response time
            connection = connection_manager.get_best_available_connection()
            connection_manager.set_connection(connection)
            Utils.assert_true(connection == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(connection.is_online())
            Utils.assert_true(connection.is_authenticated())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # test connections and order
            ordered_connections = connection_manager.get_connections()
            Utils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(ordered_connections[1] == wallet_rpcs[2].get_daemon_connection())
            Utils.assert_true(ordered_connections[2] == wallet_rpcs[3].get_daemon_connection())
            Utils.assert_true(ordered_connections[3] == wallet_rpcs[0].get_daemon_connection())
            connection =  wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(ordered_connections[4].uri, connection.uri)
            for orderedConnection in ordered_connections:
                Utils.assert_is_none(orderedConnection.is_online())

            # shut down prioritized servers
            Utils.stop_wallet_rpc_process(wallet_rpcs[2])
            Utils.stop_wallet_rpc_process(wallet_rpcs[3])
            Utils.stop_wallet_rpc_process(wallet_rpcs[4])
            Utils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100) # allow time to poll
            Utils.assert_false(connection_manager.is_connected())
            connection = connection_manager.get_connection()
            assert connection is not None
            Utils.assert_false(connection.is_online())
            Utils.assert_is_none(connection.is_authenticated())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_equals(
                listener.changed_connections.get(listener.changed_connections.size() - 1),
                connection_manager.get_connection()
            )

            # test connection order
            ordered_connections = connection_manager.get_connections()
            Utils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(ordered_connections[1] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(ordered_connections[2].uri, connection.uri)
            Utils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            Utils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            # check all connections
            connection_manager.check_connections()

            # test connection order
            ordered_connections = connection_manager.get_connections()
            Utils.assert_true(ordered_connections[0] == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(ordered_connections[1] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(ordered_connections[2].uri, connection.uri)
            Utils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            Utils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            # test online and authentication status
            for orderedConnection in ordered_connections:
                is_online = orderedConnection.is_online()
                is_authenticated = orderedConnection.is_authenticated()
                if i == 1 or i == 2:
                    Utils.assert_true(is_online)
                else:
                    Utils.assert_false(is_online)
                if i == 1:
                    Utils.assert_true(is_authenticated)
                elif i == 2:
                    Utils.assert_false(is_authenticated)
                else:
                    Utils.assert_is_none(is_authenticated)

            # test auto switch when disconnected
            connection_manager.set_auto_switch(True)
            Utils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
            Utils.assert_true(connection_manager.is_connected())
            connection = connection_manager.get_connection()
            assert connection is not None
            Utils.assert_true(connection.is_online())
            Utils.assert_true(connection == wallet_rpcs[0].get_daemon_connection())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # test connection order
            ordered_connections = connection_manager.get_connections()
            Utils.assert_true(ordered_connections[0] == connection)
            Utils.assert_true(ordered_connections[0] == wallet_rpcs[0].get_daemon_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(ordered_connections[1].uri, connection.uri)
            Utils.assert_true(ordered_connections[2] == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            Utils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            # connect to specific endpoint without authentication
            connection = ordered_connections[1]
            Utils.assert_false(connection.is_authenticated())
            connection_manager.set_connection(connection)
            Utils.assert_false(connection_manager.is_connected())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # connect to specific endpoint with authentication
            ordered_connections[1].set_credentials("rpc_user", "abc123")
            connection_manager.check_connection()
            connection = connection_manager.get_connection()
            assert connection is not None
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(connection.uri, connection.uri)
            Utils.assert_true(connection.is_online())
            Utils.assert_true(connection.is_authenticated())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # test connection order
            ordered_connections = connection_manager.get_connections()
            Utils.assert_true(ordered_connections[0] == connection_manager.get_connection())
            connection = wallet_rpcs[1].get_daemon_connection()
            assert connection is not None
            Utils.assert_equals(ordered_connections[0].uri, connection.uri)
            Utils.assert_true(ordered_connections[1] == wallet_rpcs[0].get_daemon_connection())
            Utils.assert_true(ordered_connections[2] == wallet_rpcs[4].get_daemon_connection())
            Utils.assert_true(ordered_connections[3] == wallet_rpcs[2].get_daemon_connection())
            Utils.assert_true(ordered_connections[4] == wallet_rpcs[3].get_daemon_connection())

            first: bool = True
            for orderedConnection in ordered_connections:
                if i <= 1:
                    Utils.assert_true(orderedConnection.is_online() if first else not orderedConnection.is_online() )

            Utils.assert_false(ordered_connections[4].is_online())

            # set connection to existing uri
            connection = wallet_rpcs[0].get_daemon_connection()
            assert connection is not None
            connection_manager.set_connection(connection.uri)
            Utils.assert_true(connection_manager.is_connected())
            Utils.assert_true(wallet_rpcs[0].get_daemon_connection() == connection_manager.get_connection())
            connection = connection_manager.get_connection()
            assert connection is not None
            Utils.assert_equals(Utils.WALLET_RPC_USERNAME, connection.username)
            Utils.assert_equals(Utils.WALLET_RPC_PASSWORD, connection.password)
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_equals(
                listener.changed_connections.get(listener.changed_connections.size() - 1),
                wallet_rpcs[0].get_daemon_connection()
            )

            # set connection to new uri
            connection_manager.stop_polling()
            uri: str = "http:#localhost:49999"
            connection_manager.set_connection(uri)
            connection = connection_manager.get_connection()
            assert connection is not None
            Utils.assert_equals(uri, connection.uri)
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            connection = listener.changed_connections.get(listener.changed_connections.size() -1)
            assert connection is not None
            Utils.assert_equals(uri, connection.uri)

            # set connection to empty string
            connection_manager.set_connection("")
            Utils.assert_equals(None, connection_manager.get_connection())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # check all connections and test auto switch
            connection_manager.check_connections()
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(connection_manager.is_connected())

            # remove current connection and test auto switch
            connection = connection_manager.get_connection()
            assert connection is not None
            assert connection.uri is not None
            connection_manager.remove_connection(connection.uri)
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_false(connection_manager.is_connected())
            connection_manager.check_connections()
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(connection_manager.is_connected())

            # test polling current connection
            connection_manager.set_connection(None)
            Utils.assert_false(connection_manager.is_connected())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            connection_manager.start_polling(
                period_ms=Utils.SYNC_PERIOD_IN_MS,
                poll_type=MoneroConnectionPollType.CURRENT
            )
            Utils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            Utils.assert_true(connection_manager.is_connected())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # test polling all connections
            connection_manager.set_connection(None)
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            connection_manager.start_polling(period_ms=Utils.SYNC_PERIOD_IN_MS, poll_type=MoneroConnectionPollType.ALL)
            Utils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
            Utils.assert_true(connection_manager.is_connected())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())

            # shut down all connections
            connection = connection_manager.get_connection()
            assert connection is not None
            for wallet_rpc in wallet_rpcs:
                Utils.stop_wallet_rpc_process(wallet_rpc)

            Utils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
            Utils.assert_false(connection.is_online())
            num_expected_changes += 1
            Utils.assert_equals(num_expected_changes, listener.changed_connections.size())
            Utils.assert_true(listener.changed_connections.get(listener.changed_connections.size() - 1) == connection)

            # reset
            connection_manager.reset()
            Utils.assert_equals(0, len(connection_manager.get_connections()))
            Utils.assert_equals(None, connection_manager.get_connection())

        finally:
            # stop connection manager
            if connection_manager is not None:
                connection_manager.reset()

            # stop monero-wallet-rpc instances
            for wallet_rpc in wallet_rpcs:
                try:
                    Utils.stop_wallet_rpc_process(wallet_rpc)
                except Exception as e2:
                    print(f"[!] {str(e2)}")
