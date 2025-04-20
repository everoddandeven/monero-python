import pytest
from typing import Optional
from monero import MoneroWalletRpc, MoneroConnectionManager, MoneroRpcConnection, MoneroConnectionPollType
from utils import ConnectionChangeCollector, MoneroTestUtils as Utils

# @pytest.mark.skip(reason="Wallet RPC process not implemented")
def test_connection_manager():
  walletRpcs: list[MoneroWalletRpc] = []
  connectionManager: Optional[MoneroConnectionManager] = None
  try:
    i: int = 0
    
    while i < 5:
      walletRpcs.append(Utils.start_wallet_rpc_process())
      i += 1
    # start monero-wallet-rpc instances as test server connections (can also use monerod servers)
    
    # create connection manager
    connectionManager = MoneroConnectionManager()
    
    # listen for changes
    listener = ConnectionChangeCollector()
    connectionManager.add_listener(listener)
    
    # add prioritized connections
    connection: Optional[MoneroRpcConnection]  = walletRpcs[4].get_daemon_connection()
    assert connection is not None
    connection.priority = 1
    connectionManager.add_connection(connection)
    connection = walletRpcs[2].get_daemon_connection()
    assert connection is not None
    connection.priority = 2
    connectionManager.add_connection(connection)
    connection = walletRpcs[3].get_daemon_connection()
    assert connection is not None
    connection.priority = 2
    connectionManager.add_connection(connection)
    connection = walletRpcs[0].get_daemon_connection()
    assert connection is not None
    connectionManager.add_connection(connection) # default priority is lowest
    connection = walletRpcs[1].get_daemon_connection()
    assert connection is not None
    connectionManager.add_connection(MoneroRpcConnection(connection.uri)) # test unauthenticated
    
    # test connections and order
    orderedConnections: list[MoneroRpcConnection] = connectionManager.get_connections()
    Utils.assert_true(orderedConnections[0] == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(orderedConnections[1] == walletRpcs[2].get_daemon_connection())
    Utils.assert_true(orderedConnections[2] == walletRpcs[3].get_daemon_connection())
    Utils.assert_true(orderedConnections[3] == walletRpcs[0].get_daemon_connection())
    Utils.assert_equals(orderedConnections[4].uri, walletRpcs[1].get_daemon_connection().uri)
    
    for connection in orderedConnections:
      assert connection.is_online() is None

    # test getting connection by uri
    Utils.assert_true(connectionManager.has_connection(walletRpcs[0].get_daemon_connection().uri))
    Utils.assert_true(connectionManager.get_connection_by_uri(walletRpcs[0].get_daemon_connection().uri) == walletRpcs[0].get_daemon_connection())
    
    # test unknown connection
    numExpectedChanges: int = 0
    connectionManager.set_connection(orderedConnections[0])
    Utils.assert_equals(None, connectionManager.is_connected())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())

    # auto connect to best available connection
    connectionManager.start_polling(Utils.SYNC_PERIOD_IN_MS)
    Utils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
    Utils.assert_true(connectionManager.is_connected())
    connection = connectionManager.get_connection()
    assert connection is not None
    Utils.assert_true(connection.is_online())
    Utils.assert_true(connection == walletRpcs[4].get_daemon_connection())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == connection)
    connectionManager.set_auto_switch(False)
    connectionManager.stop_polling()
    connectionManager.disconnect()
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == None)
    
    # start periodically checking connection without auto switch
    connectionManager.start_polling(Utils.SYNC_PERIOD_IN_MS, False)
    
    # connect to best available connection in order of priority and response time
    connection = connectionManager.get_best_available_connection()
    connectionManager.set_connection(connection)
    Utils.assert_true(connection == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(connection.is_online())
    Utils.assert_true(connection.is_authenticated())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == connection)
    
    # test connections and order
    orderedConnections = connectionManager.get_connections()
    Utils.assert_true(orderedConnections[0] == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(orderedConnections[1] == walletRpcs[2].get_daemon_connection())
    Utils.assert_true(orderedConnections[2] == walletRpcs[3].get_daemon_connection())
    Utils.assert_true(orderedConnections[3] == walletRpcs[0].get_daemon_connection())
    Utils.assert_equals(orderedConnections[4].uri, walletRpcs[1].get_daemon_connection().uri)
    for orderedConnection in orderedConnections: 
      Utils.assert_is_none(orderedConnection.is_online())
    
    # shut down prioritized servers
    Utils.stop_wallet_rpc_process(walletRpcs[2])
    Utils.stop_wallet_rpc_process(walletRpcs[3])
    Utils.stop_wallet_rpc_process(walletRpcs[4])
    Utils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100) # allow time to poll
    Utils.assert_false(connectionManager.is_connected())
    connection = connectionManager.get_connection()
    assert connection is not None
    Utils.assert_false(connection.is_online())
    Utils.assert_is_none(connection.is_authenticated())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == connectionManager.get_connection())
    
    # test connection order
    orderedConnections = connectionManager.get_connections()
    Utils.assert_true(orderedConnections[0] == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(orderedConnections[1] == walletRpcs[0].get_daemon_connection())
    Utils.assert_equals(orderedConnections[2].uri, walletRpcs[1].get_daemon_connection().uri)
    Utils.assert_true(orderedConnections[3] == walletRpcs[2].get_daemon_connection())
    Utils.assert_true(orderedConnections[4] == walletRpcs[3].get_daemon_connection())
    
    # check all connections
    connectionManager.check_connections()
    
    # test connection order
    orderedConnections = connectionManager.get_connections()
    Utils.assert_true(orderedConnections[0] == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(orderedConnections[1] == walletRpcs[0].get_daemon_connection())
    Utils.assert_equals(orderedConnections[2].uri, walletRpcs[1].get_daemon_connection().uri)
    Utils.assert_true(orderedConnections[3] == walletRpcs[2].get_daemon_connection())
    Utils.assert_true(orderedConnections[4] == walletRpcs[3].get_daemon_connection())
    
    # test online and authentication status
    for orderedConnection in orderedConnections:
      is_online = orderedConnection.is_online()
      is_authenticated = orderedConnection.is_authenticated()
      if (i == 1 or i == 2):
        Utils.assert_true(is_online)
      else:
        Utils.assert_false(is_online)
      if (i == 1):
        Utils.assert_true(is_authenticated)
      elif (i == 2): 
        Utils.assert_false(is_authenticated)
      else:
        Utils.assert_is_none(is_authenticated)
    
    # test auto switch when disconnected
    connectionManager.set_auto_switch(True)
    Utils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
    Utils.assert_true(connectionManager.is_connected())
    connection = connectionManager.get_connection()
    assert connection is not None
    Utils.assert_true(connection.is_online())
    Utils.assert_true(connection == walletRpcs[0].get_daemon_connection())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == connection)
    
    # test connection order
    orderedConnections = connectionManager.get_connections()
    Utils.assert_true(orderedConnections[0] == connection)
    Utils.assert_true(orderedConnections[0] == walletRpcs[0].get_daemon_connection())
    Utils.assert_equals(orderedConnections[1].uri, walletRpcs[1].get_daemon_connection().uri)
    Utils.assert_true(orderedConnections[2] == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(orderedConnections[3] == walletRpcs[2].get_daemon_connection())
    Utils.assert_true(orderedConnections[4] == walletRpcs[3].get_daemon_connection())
    
    # connect to specific endpoint without authentication
    connection = orderedConnections[1]
    Utils.assert_false(connection.is_authenticated())
    connectionManager.set_connection(connection)
    Utils.assert_false(connectionManager.is_connected())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    
    # connect to specific endpoint with authentication
    orderedConnections[1].set_credentials("rpc_user", "abc123")
    connectionManager.check_connection()
    connection = connectionManager.get_connection()
    assert connection is not None
    Utils.assert_equals(connection.uri, walletRpcs[1].get_daemon_connection().uri)
    Utils.assert_true(connection.is_online())
    Utils.assert_true(connection.is_authenticated())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == connection)
    
    # test connection order
    orderedConnections = connectionManager.get_connections()
    Utils.assert_true(orderedConnections[0] == connectionManager.get_connection())
    Utils.assert_equals(orderedConnections[0].uri, walletRpcs[1].get_daemon_connection().uri)
    Utils.assert_true(orderedConnections[1] == walletRpcs[0].get_daemon_connection())
    Utils.assert_true(orderedConnections[2] == walletRpcs[4].get_daemon_connection())
    Utils.assert_true(orderedConnections[3] == walletRpcs[2].get_daemon_connection())
    Utils.assert_true(orderedConnections[4] == walletRpcs[3].get_daemon_connection())
        
    first: bool = True
    for orderedConnection in orderedConnections:
      if (i <= 1):
        Utils.assert_true(orderedConnection.is_online() if first else not orderedConnection.is_online() )

    Utils.assert_false(orderedConnections[4].is_online())
    
    # set connection to existing uri
    connectionManager.set_connection(walletRpcs[0].get_daemon_connection().uri)
    Utils.assert_true(connectionManager.is_connected())
    Utils.assert_true(walletRpcs[0].get_daemon_connection() == connectionManager.get_connection())
    connection = connectionManager.get_connection()
    assert connection is not None
    Utils.assert_equals(Utils.WALLET_RPC_USERNAME, connection.username)
    Utils.assert_equals(Utils.WALLET_RPC_PASSWORD, connection.password)
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == walletRpcs[0].get_daemon_connection())
    
    # set connection to new uri
    connectionManager.stop_polling()
    uri: str = "http:#localhost:49999"
    connectionManager.set_connection(uri)
    connection = connectionManager.get_connection()
    assert connection is not None
    Utils.assert_equals(uri, connection.uri)
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    connection = listener.changedConnections.get(listener.changedConnections.size() -1)
    assert connection is not None
    Utils.assert_equals(uri, connection.uri)
    
    # set connection to empty string
    connectionManager.set_connection("")
    Utils.assert_equals(None, connectionManager.get_connection())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    
    # check all connections and test auto switch
    connectionManager.check_connections()
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(connectionManager.is_connected())

    # remove current connection and test auto switch
    connection = connectionManager.get_connection()
    assert connection is not None
    connectionManager.remove_connection(connection.uri)
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_false(connectionManager.is_connected())
    connectionManager.check_connections()
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(connectionManager.is_connected())

    # test polling current connection
    connectionManager.set_connection(None)
    Utils.assert_false(connectionManager.is_connected())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    connectionManager.start_polling(period_ms=Utils.SYNC_PERIOD_IN_MS, poll_type=MoneroConnectionPollType.CURRENT)
    Utils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
    Utils.assert_true(connectionManager.is_connected())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())

    # test polling all connections
    connectionManager.set_connection(None)
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    connectionManager.start_polling(period_ms=Utils.SYNC_PERIOD_IN_MS, poll_type=MoneroConnectionPollType.ALL)
    Utils.wait_for(Utils.AUTO_CONNECT_TIMEOUT_MS)
    Utils.assert_true(connectionManager.is_connected())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())

    # shut down all connections
    connection = connectionManager.get_connection()
    assert connection is not None
    for walletRpc in walletRpcs: 
      Utils.stop_wallet_rpc_process(walletRpc)

    Utils.wait_for(Utils.SYNC_PERIOD_IN_MS + 100)
    Utils.assert_false(connection.is_online())
    numExpectedChanges += 1
    Utils.assert_equals(numExpectedChanges, listener.changedConnections.size())
    Utils.assert_true(listener.changedConnections.get(listener.changedConnections.size() - 1) == connection)
    
    # reset
    connectionManager.reset()
    Utils.assert_equals(0, len(connectionManager.get_connections()))
    Utils.assert_equals(None, connectionManager.get_connection())
  
  finally:    
    # stop connection manager
    if connectionManager is not None:
      connectionManager.reset()
    
    # stop monero-wallet-rpc instances
    for walletRpc in walletRpcs:
      #try { Utils.stop_wallet_rpc_process(walletRpc) }
      #catch (Exception e2) { }
      pass
  
