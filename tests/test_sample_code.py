import pytest

from typing_extensions import override

from monero import (
  MoneroDaemon, MoneroDaemonRpc, MoneroOutputWallet, MoneroTx, MoneroWalletRpc, MoneroTxConfig,
  MoneroWalletFull, MoneroWalletConfig, MoneroConnectionManager, MoneroRpcConnection,
  MoneroNetworkType, MoneroWalletListener, MoneroTxWallet
)

from utils import MoneroTestUtils as Utils, SampleConnectionListener, WalletSyncPrinter

class WalletFundsListener(MoneroWalletListener):
  FUNDS_RECEIVED: bool = False

  @override
  def on_output_received(self, output: MoneroOutputWallet) -> None:
    amount = output.amount
    txHash = output.tx.hash
    isConfirmed = output.tx.is_confirmed
    # isLocked = output.tx.is_locked
    self.FUNDS_RECEIVED = True

class TestSampleCode:

  # Sample code demonstration
  def test_sample_code(self):
    # connect to daemon
    daemon: MoneroDaemon = MoneroDaemonRpc("http:#localhost:28081", "", "")
    height: int = daemon.get_height()                       # 1523651
    txsInPool: list[MoneroTx] = daemon.get_tx_pool()          # get transactions in the pool
    
    # create wallet from seed using python bindings to monero-project
    config = MoneroWalletConfig()
    config.path = "./test_wallets/" + Utils.get_random_string()
    config.password = "supersecretpassword123"
    config.network_type = MoneroNetworkType.TESTNET
    config.server = MoneroRpcConnection("http:#localhost:28081", "superuser", "abctesting123")
    config.seed = Utils.SEED
    config.restore_height = Utils.FIRST_RECEIVE_HEIGHT

    walletFull = MoneroWalletFull.create_wallet(config)
    listener: MoneroWalletListener = WalletSyncPrinter()
    # synchronize the wallet and receive progress notifications
    walletFull.sync(listener)
    
    # synchronize in the background every 5 seconds
    walletFull.start_syncing(5000)
    
    # receive notifications when funds are received, confirmed, and unlocked
    fundsListener = WalletFundsListener()
    walletFull.add_listener(fundsListener)

    # connect to wallet RPC and open wallet
    walletRpc = MoneroWalletRpc(Utils.WALLET_RPC_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_RPC_PASSWORD) # *** REPLACE WITH CONSTANTS IN README ***
    walletRpc.open_wallet("test_wallet_1", "supersecretpassword123")  # *** CHANGE README TO "sample_wallet_rpc" ***
    primaryAddress: str = walletRpc.get_primary_address()  # 555zgduFhmKd2o8rPUz...
    balance: int = walletRpc.get_balance()            # 533648366742
    txs: list[MoneroTxWallet] = walletRpc.get_txs()          # get transactions containing transfers to/from the wallet
    
    # send funds from RPC wallet to full wallet
    Utils.WALLET_TX_TRACKER.wait_for_wallet_txs_to_clear_pool(daemon, Utils.SYNC_PERIOD_IN_MS, [walletRpc])                                    # *** REMOVE FROM README SAMPLE ***
    Utils.WALLET_TX_TRACKER.wait_for_unlocked_balance(daemon, Utils.SYNC_PERIOD_IN_MS, walletRpc, 0, None, 250000000000) # *** REMOVE FROM README SAMPLE ***
    tx_config = MoneroTxConfig()
    tx_config.account_index = 0
    tx_config.address = walletFull.get_address(1, 0)
    tx_config.amount = 250000000000 # send 0.25 XMR (denominated in atomic units)
    tx_config.relay = False # create transaction and relay to the network if true
    createdTx: MoneroTxWallet = walletRpc.create_tx(tx_config)
    fee: int | None = createdTx.fee # "Are you sure you want to send... ?"
    walletRpc.relay_tx(createdTx) # relay the transaction
    
    # recipient receives unconfirmed funds within 5 seconds
    Utils.wait_for(5000)
    Utils.assert_true(fundsListener.FUNDS_RECEIVED)
    
    # save and close full wallet
    walletFull.close(True)

  # Connection manager demonstration
  def test_connection_manager_demo(self):
    
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
    print(f"Connection is online: {connectionManager.get_connection().is_online()}")
    print(f"Connection is authenticated: {connectionManager.get_connection().is_authenticated()}")
    
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
