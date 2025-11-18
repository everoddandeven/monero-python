import pytest

from typing_extensions import override

from monero import (
    MoneroDaemon, MoneroDaemonRpc, MoneroOutputWallet, MoneroTx, MoneroWalletRpc, MoneroTxConfig,
    MoneroWalletFull, MoneroWalletConfig, MoneroConnectionManager, MoneroRpcConnection,
    MoneroNetworkType, MoneroWalletListener, MoneroTxWallet
)

from utils import MoneroTestUtils as Utils, SampleConnectionListener, WalletSyncPrinter


class WalletFundsListener(MoneroWalletListener):
    funds_received: bool = False

    @override
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        amount = output.amount
        tx_hash = output.tx.hash
        is_confirmed = output.tx.is_confirmed
        print(f"Received {amount}, confirmed {is_confirmed}, tx hash: {tx_hash}")
        self.funds_received = True


@pytest.mark.sample_code
class TestSampleCode:

    # Sample code demonstration
    def test_sample_code(self):
        # connect to daemon
        daemon: MoneroDaemon = MoneroDaemonRpc("http:#localhost:28081", "", "")
        height: int = daemon.get_height() # 1523651
        txs_in_pool: list[MoneroTx] = daemon.get_tx_pool() # get transactions in the pool
        print(f"Found {len(txs_in_pool)} tx(s) in pool at height {height}")

        # create wallet from seed using python bindings to monero-project
        config = MoneroWalletConfig()
        config.path = "./test_wallets/" + Utils.get_random_string()
        config.password = "supersecretpassword123"
        config.network_type = MoneroNetworkType.TESTNET
        config.server = MoneroRpcConnection("http:#localhost:28081", "superuser", "abctesting123")
        config.seed = Utils.SEED
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT

        wallet_full = MoneroWalletFull.create_wallet(config)
        listener: MoneroWalletListener = WalletSyncPrinter()
        # synchronize the wallet and receive progress notifications
        wallet_full.sync(listener)

        # synchronize in the background every 5 seconds
        wallet_full.start_syncing(5000)

        # receive notifications when funds are received, confirmed, and unlocked
        funds_listener = WalletFundsListener()
        wallet_full.add_listener(funds_listener)

        # connect to wallet RPC and open wallet
        # *** REPLACE WITH CONSTANTS IN README ***
        wallet_rpc = MoneroWalletRpc(Utils.WALLET_RPC_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_RPC_PASSWORD)
        wallet_rpc.open_wallet("test_wallet_1", "supersecretpassword123") # *** CHANGE README TO "sample_wallet_rpc" ***
        primary_address: str = wallet_rpc.get_primary_address() # 555zgduFhmKd2o8rPUz...
        balance: int = wallet_rpc.get_balance() # 533648366742
        txs: list[MoneroTxWallet] = wallet_rpc.get_txs() # get transactions containing transfers to/from the wallet
        print(f"Open wallet {primary_address}, balance: {balance}, tx(s): {len(txs)}")
        # send funds from RPC wallet to full wallet
        # *** REMOVE FROM README SAMPLE ***
        Utils.WALLET_TX_TRACKER.wait_for_wallet_txs_to_clear_pool(daemon, Utils.SYNC_PERIOD_IN_MS, [wallet_rpc])
        # *** REMOVE FROM README SAMPLE ***
        Utils.WALLET_TX_TRACKER.wait_for_unlocked_balance(
            daemon, Utils.SYNC_PERIOD_IN_MS, wallet_rpc, 0, None, 250000000000
        )
        tx_config = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.address = wallet_full.get_address(1, 0)
        tx_config.amount = 250000000000 # send 0.25 XMR (denominated in atomic units)
        tx_config.relay = False # create transaction and relay to the network if true
        created_tx: MoneroTxWallet = wallet_rpc.create_tx(tx_config)
        fee: int | None = created_tx.fee # "Are you sure you want to send... ?"
        assert fee is not None
        wallet_rpc.relay_tx(created_tx) # relay the transaction

        # recipient receives unconfirmed funds within 5 seconds
        Utils.wait_for(5000)
        Utils.assert_true(funds_listener.funds_received)

        # save and close full wallet
        wallet_full.close(True)

    # Connection manager demonstration
    def test_connection_manager_demo(self):

        # create connection manager
        connection_manager = MoneroConnectionManager()

        # add managed connections with priorities
        con1 = MoneroRpcConnection("http:#localhost:28081")
        con1.priority = 1
        connection_manager.add_connection(con1) # use localhost as first priority
        con2 = MoneroRpcConnection("http:#example.com")
        connection_manager.add_connection(con2) # default priority is prioritized last

        # set current connection
        con3 = MoneroRpcConnection("http:#foo.bar", "admin", "password")
        connection_manager.set_connection(con3) # connection is added if new

        # create or open wallet governed by connection manager
        wallet_config = MoneroWalletConfig()
        # *** CHANGE README TO "sample_wallet_full" ***
        wallet_config.path = "./test_wallets/" + Utils.get_random_string()
        wallet_config.password = "supersecretpassword123"
        wallet_config.network_type = MoneroNetworkType.TESTNET
        # wallet_config.connection_manager = connection_manager
        wallet_config.seed = Utils.SEED
        wallet_config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        # *** REPLACE WITH FIRST RECEIVE HEIGHT IN README ***
        wallet_full = MoneroWalletFull.create_wallet(wallet_config)
        print(f"Created wallet {wallet_full.get_path()}")

        # check connection status
        connection_manager.check_connection()
        print(f"Connection manager is connected: {connection_manager.is_connected()}")
        print(f"Connection is online: {connection_manager.get_connection().is_online()}")
        print(f"Connection is authenticated: {connection_manager.get_connection().is_authenticated()}")

        # receive notifications of any changes to current connection
        listener = SampleConnectionListener()
        connection_manager.add_listener(listener)

        # check connections every 10 seconds (in order of priority) and switch to the best
        connection_manager.start_polling(10000)

        # get the best available connection in order of priority then response time
        best_connection: MoneroRpcConnection = connection_manager.get_best_available_connection()

        assert best_connection is not None

        # check status of all connections
        connection_manager.check_connections()

        # get connections in order of current connection, online status from last check, priority, and name
        connections: list[MoneroRpcConnection] = connection_manager.get_connections()

        assert len(connections) > 0

        # clear connection manager
        connection_manager.clear()
