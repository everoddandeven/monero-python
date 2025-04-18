import pytest

from monero import (
  MoneroWalletFull, MoneroWalletConfig, MoneroConnectionManager, MoneroRpcConnection,
  MoneroNetworkType
)

from utils import MoneroTestUtils as Utils, SampleConnectionListener

# Connection manager demonstration
def test_connection_manager_demo():
  
  # create connection manager
  connectionManager = MoneroConnectionManager()
  
  # add managed connections with priorities
  con1 = MoneroRpcConnection("http:#localhost:28081")
  con1.priority = 1
  connectionManager.add_connection(con1) # use localhost as first priority
  con2 = MoneroRpcConnection("http:#example.com")
  connectionManager.add_connection(con2) # default priority is prioritized last
  
  # set current connection
  con3 = MoneroRpcConnection("http:#foo.bar", "admin", "password")
  connectionManager.set_connection(con3) # connection is added if new

  # create or open wallet governed by connection manager
  wallet_config = MoneroWalletConfig()
  # *** CHANGE README TO "sample_wallet_full" ***
  wallet_config.path = "./test_wallets/" + Utils.get_random_string()
  wallet_config.password = "supersecretpassword123"
  wallet_config.network_type = MoneroNetworkType.TESTNET
  # wallet_config.connection_manager = connectionManager
  wallet_config.seed = Utils.SEED
  wallet_config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
  walletFull = MoneroWalletFull.create_wallet(wallet_config) # *** REPLACE WITH FIRST RECEIVE HEIGHT IN README ***
  
  # check connection status
  connectionManager.check_connection()
  print(f"Connection manager is connected: {connectionManager.is_connected()}")
  print(f"Connection is online: {connectionManager.get_connection().is_online}")
  print(f"Connection is authenticated: {connectionManager.get_connection().is_authenticated}")
  
  # receive notifications of any changes to current connection
  listener = SampleConnectionListener()
  connectionManager.add_listener(listener)
  
  # check connections every 10 seconds (in order of priority) and switch to the best
  connectionManager.start_polling(10000)
  
  # get best available connection in order of priority then response time
  bestConnection: MoneroRpcConnection = connectionManager.get_best_available_connection()
  
  # check status of all connections
  connectionManager.check_connections()
  
  # get connections in order of current connection, online status from last check, priority, and name
  connections: list[MoneroRpcConnection] = connectionManager.get_connections()
  
  # clear connection manager
  connectionManager.clear()