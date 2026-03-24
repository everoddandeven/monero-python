import pytest
import logging

from typing import Optional
from typing_extensions import override

from time import sleep
from monero import (
    MoneroWalletFull, MoneroWalletConfig, MoneroAccount,
    MoneroSubaddress, MoneroWallet, MoneroNetworkType,
    MoneroRpcConnection, MoneroUtils, MoneroDaemonRpc,
    MoneroSyncResult, MoneroTxWallet
)

from utils import (
    TestUtils as Utils, StringUtils,
    AssertUtils, WalletUtils, WalletType,
    MultisigSampleCodeTester, SyncSeedTester,
    SyncProgressTester, WalletEqualityUtils
)
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletFull")


@pytest.mark.integration
class TestMoneroWalletFull(BaseTestMoneroWallet):
    """Full wallet integration tests"""

    #region Overrides

    @classmethod
    @override
    def get_wallet_type(cls) -> WalletType:
        return WalletType.FULL

    @pytest.fixture(scope="class")
    @override
    def wallet(self) -> MoneroWalletFull:
        """Test rpc wallet instance"""
        return Utils.get_wallet_full()

    @override
    def after_all(self) -> None:
        super().after_all()
        Utils.WALLET_FULL_TESTS_RUN = True

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True):
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        random: bool = self.is_random_wallet_config(config)
        if config.path is None:
            config.path = Utils.TEST_WALLETS_DIR + "/" + StringUtils.get_random_string()
        if config.password is None:
            config.password = Utils.WALLET_PASSWORD
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE
        #if config.server is None and config.connection_manager is None:
        if config.server is None:
            config.server = Utils.get_daemon_rpc_connection()
        if config.restore_height is None and not random:
            config.restore_height = 0

        # create wallet
        wallet = MoneroWalletFull.create_wallet(config)
        if not random:
            restore_height: int = 0 if config.restore_height is None else config.restore_height
            assert restore_height == wallet.get_restore_height()
        if start_syncing is not False and wallet.is_connected_to_daemon():
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)
        return wallet

    @override
    def _open_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True) -> MoneroWalletFull:
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        if config.password is None:
            config.password = Utils.WALLET_PASSWORD
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE
        if config.server is None and config.connection_manager is None:
            config.server = Utils.get_daemon_rpc_connection()

        # open wallet
        assert config.network_type is not None
        assert config.path is not None

        wallet = MoneroWalletFull.open_wallet(config.path, config.password, config.network_type)
        if start_syncing is not False and wallet.is_connected_to_daemon():
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)
        return wallet

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)

    @override
    def _get_seed_languages(self) -> list[str]:
        return self.get_test_wallet().get_seed_languages()

    @override
    @classmethod
    def get_test_wallet(cls) -> MoneroWalletFull:
        return super().get_test_wallet() # type: ignore

    #endregion

    #region Test Relays

    @pytest.mark.skipif(Utils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(Utils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.xfail(raises=RuntimeError, reason="TODO Cannot reconcile integrals:  0 vs  1. tx wallet m_is_incoming")
    @override
    def test_update_locked_different_accounts_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_different_accounts_split(daemon, wallet)

    #endregion

    #region Test Non Relays

    # TODO implement
    @pytest.mark.not_implemented
    @override
    def test_account_tags(self, wallet: MoneroWallet) -> None:
        return super().test_account_tags(wallet)

    # Can create a random full wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_random_full(self, daemon: MoneroDaemonRpc) -> None:
        # create random wallet with defaults
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.network_type = MoneroNetworkType.MAINNET
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        wallet: MoneroWalletFull = self._create_wallet(config)
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        MoneroUtils.validate_address(wallet.get_primary_address(), MoneroNetworkType.MAINNET)
        assert wallet.get_network_type() == MoneroNetworkType.MAINNET
        AssertUtils.assert_equals(wallet.get_daemon_connection(), MoneroRpcConnection(Utils.OFFLINE_SERVER_URI))
        assert wallet.is_connected_to_daemon() is False
        assert wallet.get_seed_language() == "English"
        assert wallet.get_path() == path
        assert wallet.is_synced() is False
        # TODO monero-project: why does height of new unsynced wallet start at 1?
        assert wallet.get_height() == 1
        assert wallet.get_restore_height() >= 0

        # cannot get daemon chain height
        try:
            wallet.get_daemon_height()
            raise Exception("Should have failed")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "Wallet is not connected to daemon", e_msg

        # set daemon and check chain height
        wallet.set_daemon_connection(daemon.get_rpc_connection())
        assert daemon.get_height() == wallet.get_daemon_height()

        # close wallet which releases resources
        wallet.close()

        # create random wallet with non defaults
        path = Utils.get_random_wallet_path()
        config = MoneroWalletConfig()
        config.path = path
        config.network_type = MoneroNetworkType.TESTNET
        config.language = "Spanish"
        wallet = self._create_wallet(config, False)
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        MoneroUtils.validate_address(wallet.get_primary_address(), MoneroNetworkType.TESTNET)
        assert wallet.get_network_type() == MoneroNetworkType.TESTNET
        assert wallet.get_daemon_connection() is not None
        assert wallet.get_daemon_connection() != daemon.get_rpc_connection()
        AssertUtils.assert_equals(wallet.get_daemon_connection(), daemon.get_rpc_connection())
        assert wallet.is_connected_to_daemon()
        assert wallet.get_seed_language() == "Spanish"
        assert path == wallet.get_path()
        assert wallet.is_synced() is False
        # TODO monero-project: why is height of unsynced wallet 1?
        assert wallet.get_height() == 1
        if daemon.is_connected():
            assert daemon.get_height() == wallet.get_restore_height()
        else:
            assert wallet.get_restore_height() >= 0

        wallet.close()

    # Can create a full wallet from seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed_full(self, daemon: MoneroDaemonRpc) -> None:
        # create unconnected wallet with seed
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        wallet: MoneroWalletFull = self._create_wallet(config)
        assert wallet.get_seed() == Utils.SEED
        assert wallet.get_primary_address() == Utils.ADDRESS
        assert wallet.get_network_type() == Utils.NETWORK_TYPE
        AssertUtils.assert_equals(MoneroRpcConnection(Utils.OFFLINE_SERVER_URI), wallet.get_daemon_connection())
        assert wallet.is_connected_to_daemon() is False
        assert wallet.get_seed_language() == "English"
        assert wallet.get_path() == path
        assert wallet.is_synced() is False
        assert wallet.get_height() == 1
        assert wallet.get_restore_height() == 0
        try:
            wallet.start_syncing()
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "Wallet is not connected to daemon", e_msg

        wallet.close()

        # create wallet without restore height
        path = Utils.get_random_wallet_path()
        config = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        wallet = self._create_wallet(config, False)
        assert wallet.get_seed() == Utils.SEED
        assert wallet.get_primary_address() == Utils.ADDRESS
        assert wallet.get_network_type() == Utils.NETWORK_TYPE
        assert wallet.get_daemon_connection() is not None
        assert wallet.get_daemon_connection() != daemon.get_rpc_connection()
        AssertUtils.assert_equals(wallet.get_daemon_connection(), daemon.get_rpc_connection())
        assert wallet.is_connected_to_daemon()
        assert wallet.get_seed_language() == "English"
        assert wallet.get_path() == path
        assert wallet.is_synced() is False
        assert wallet.get_height() == 1
        # TODO (java annotation) restore height is lost after closing only in JNI
        assert wallet.get_restore_height() == 0
        wallet.close()

        # create wallet with seed, no connection, and restore height
        restore_height: int = 10000
        path = Utils.get_random_wallet_path()
        config = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = restore_height
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        wallet = self._create_wallet(config)
        assert wallet.get_seed() == Utils.SEED
        assert wallet.get_primary_address() == Utils.ADDRESS
        assert wallet.get_network_type() == Utils.NETWORK_TYPE
        AssertUtils.assert_equals(MoneroRpcConnection(Utils.OFFLINE_SERVER_URI), wallet.get_daemon_connection())
        assert wallet.is_connected_to_daemon() is False
        assert wallet.get_seed_language() == "English"
        # TODO monero-project: why does height of new unsynced wallet start at 1?
        assert wallet.get_height() == 1
        assert wallet.get_restore_height() == restore_height
        assert wallet.get_path() == path
        wallet.close(True)
        config = MoneroWalletConfig()
        config.path = path
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        wallet = self._open_wallet(config)
        assert wallet.is_connected_to_daemon() is False
        assert wallet.is_synced() is False
        assert wallet.get_height() == 1
        # restore height is lost after closing
        assert wallet.get_restore_height() == 0
        wallet.close()

        # create wallet with seed, connection, and restore height
        path = Utils.get_random_wallet_path()
        config = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = restore_height
        wallet = self._create_wallet(config, False)
        assert wallet.get_seed() == Utils.SEED
        assert wallet.get_primary_address() == Utils.ADDRESS
        assert wallet.get_network_type() == Utils.NETWORK_TYPE
        assert wallet.get_daemon_connection() is not None
        assert wallet.get_daemon_connection() != daemon.get_rpc_connection()
        AssertUtils.assert_equals(wallet.get_daemon_connection(), daemon.get_rpc_connection())
        assert wallet.is_connected_to_daemon()
        assert wallet.get_seed_language() == "English"
        assert wallet.get_path() == path
        assert wallet.is_synced() is False
        # TODO monero-project: why does height of new unsynced wallet start at 1?
        assert wallet.get_height() == 1
        assert wallet.get_restore_height() == restore_height
        wallet.close()

    # Can create a full wallet from keys
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys_pybind(self, wallet: MoneroWalletFull) -> None:
        # recreate test wallet from keys
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.primary_address = wallet.get_primary_address()
        config.private_view_key = wallet.get_private_view_key()
        config.private_spend_key = wallet.get_private_spend_key()
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        wallet_keys: MoneroWalletFull = self._create_wallet(config)

        try:
            # test wallet keys equality
            assert wallet.get_seed() == wallet_keys.get_seed()
            assert wallet.get_primary_address() == wallet_keys.get_primary_address()
            assert wallet.get_private_view_key() == wallet_keys.get_private_view_key()
            assert wallet.get_public_view_key() == wallet_keys.get_public_view_key()
            assert wallet.get_private_spend_key() == wallet_keys.get_private_spend_key()
            assert wallet.get_public_spend_key() == wallet_keys.get_public_spend_key()
            assert Utils.FIRST_RECEIVE_HEIGHT == wallet_keys.get_restore_height()
            assert wallet_keys.is_connected_to_daemon()
            assert wallet_keys.is_synced() is False
        finally:
            wallet_keys.close()

    # Can sync a wallet with a randomly generated seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sync_random(self, daemon: MoneroDaemonRpc) -> None:
        assert daemon.is_connected(), "Not connected to daemon"

        # create test wallet
        wallet: MoneroWalletFull = self._create_wallet(MoneroWalletConfig(), False)
        restore_height: int = daemon.get_height()

        # test wallet's height before syncing
        AssertUtils.assert_equals(Utils.get_daemon_rpc_connection(), wallet.get_daemon_connection())
        assert restore_height == wallet.get_daemon_height()
        assert wallet.is_connected_to_daemon()
        assert wallet.is_synced() is False
        assert wallet.get_height() == 1
        assert wallet.get_restore_height() == restore_height
        assert wallet.get_daemon_height() == daemon.get_height()

        # sync the wallet
        progress_tester: SyncProgressTester = SyncProgressTester(wallet, wallet.get_restore_height(), wallet.get_daemon_height())
        result: MoneroSyncResult = wallet.sync(progress_tester)
        progress_tester.on_done(wallet.get_daemon_height())

        # test result after syncing
        wallet_gt: MoneroWalletFull = Utils.create_wallet_ground_truth(Utils.NETWORK_TYPE, wallet.get_seed(), None, restore_height)
        wallet_gt.sync()

        try:
            assert wallet.is_connected_to_daemon()
            assert wallet.is_synced()
            assert result.num_blocks_fetched == 0
            assert result.received_money is False
            assert wallet.get_height() == daemon.get_height()

            # sync the wallet with default params
            wallet.sync()
            assert wallet.is_synced()
            assert wallet.get_height() == daemon.get_height()

            # compare wallet to ground truth
            WalletEqualityUtils.test_wallet_full_equality_on_chain(wallet_gt, wallet)
        finally:
            wallet_gt.close(True)
            wallet.close()

        # attempt to sync unconnected wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        wallet = self._create_wallet(config)
        try:
            wallet.sync()
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "Wallet is not connected to daemon", e_msg
        finally:
            wallet.close()

    # Can sync a wallet created from seed from the genesis
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_seed_from_genesis(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull) -> None:
        self._test_sync_seed(daemon, wallet, None, None, True, False)

    # Can sync a wallet created from seed from a restore height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_seed_from_restore_height(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull) -> None:
        self._test_sync_seed(daemon, wallet, None, Utils.FIRST_RECEIVE_HEIGHT)

    # Can sync a wallet created from seed from a start height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_seed_from_start_height(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull) -> None:
        self._test_sync_seed(daemon, wallet, Utils.FIRST_RECEIVE_HEIGHT, None, False, True)

    # Can sync a wallet created from seed from a start height less than the restore height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_seed_start_height_lt_restore_height(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull) -> None:
        self._test_sync_seed(daemon, wallet, Utils.FIRST_RECEIVE_HEIGHT, Utils.FIRST_RECEIVE_HEIGHT + 3)

    # Can sync a wallet created from seed from a start height greater than the restore height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_seed_start_height_gt_restore_height(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull) -> None:
        self._test_sync_seed(daemon, wallet, Utils.FIRST_RECEIVE_HEIGHT + 3, Utils.FIRST_RECEIVE_HEIGHT)

    # Can sync a wallet created from keys
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_wallet_from_keys(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull) -> None:
        # recreate test wallet from keys
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.primary_address = wallet.get_primary_address()
        config.private_view_key = wallet.get_private_view_key()
        config.private_spend_key = wallet.get_private_spend_key()
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        wallet_keys: MoneroWalletFull = self._create_wallet(config, False)

        # create ground truth wallet for comparison
        wallet_gt: MoneroWalletFull = Utils.create_wallet_ground_truth(Utils.NETWORK_TYPE, Utils.SEED, None, Utils.FIRST_RECEIVE_HEIGHT)

        # test wallet and close as final step
        try:
            assert wallet_keys.get_seed() == wallet_gt.get_seed()
            assert wallet_keys.get_primary_address() == wallet_gt.get_primary_address()
            assert wallet_keys.get_private_view_key() == wallet_gt.get_private_view_key()
            assert wallet_keys.get_public_view_key() == wallet_gt.get_public_view_key()
            assert wallet_keys.get_private_spend_key() == wallet_gt.get_private_spend_key()
            assert wallet_keys.get_public_spend_key() == wallet_gt.get_public_spend_key()
            assert Utils.FIRST_RECEIVE_HEIGHT == wallet_gt.get_restore_height()
            assert wallet_keys.is_connected_to_daemon()
            assert wallet_keys.is_synced() is False

            # sync the wallet
            progress_tester: SyncProgressTester = SyncProgressTester(wallet_keys, Utils.FIRST_RECEIVE_HEIGHT, wallet_keys.get_daemon_max_peer_height())
            result: MoneroSyncResult = wallet_keys.sync(progress_tester)
            progress_tester.on_done(wallet_keys.get_daemon_height())

            # test result after syncing
            assert wallet_keys.is_synced()
            assert wallet_keys.get_daemon_height() - Utils.FIRST_RECEIVE_HEIGHT == result.num_blocks_fetched
            assert result.received_money is True
            assert wallet_keys.get_height() == daemon.get_height()
            assert wallet_keys.get_daemon_height() == daemon.get_height()

            # wallet should be fully synced so first tx happens on true restore height
            txs: list[MoneroTxWallet] = wallet.get_txs()
            assert len(txs) > 0
            tx: MoneroTxWallet = txs[0]
            tx_height: int | None = tx.get_height()
            assert tx_height is not None
            assert Utils.FIRST_RECEIVE_HEIGHT == tx_height

            # compare with ground truth
            WalletEqualityUtils.test_wallet_full_equality_on_chain(wallet_gt, wallet_keys)
        finally:
            wallet_gt.close(True)
            wallet_keys.close()

    # Can start and stop syncing
    # TODO test start syncing, notification of syncs happening, stop syncing, no notifications, etc
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_start_stop_syncing(self, daemon: MoneroDaemonRpc) -> None:
        # test unconnected wallet
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        config.path = path
        wallet: MoneroWalletFull = self._create_wallet(config)
        try:
            assert len(wallet.get_seed()) > 0
            assert wallet.get_height() == 1
            assert wallet.get_balance() == 0
            wallet.start_syncing()
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "Wallet is not connected to daemon", e_msg
        finally:
            wallet.close()

        # test connecting wallet
        path = Utils.get_random_wallet_path()
        config = MoneroWalletConfig()
        config.path = path
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        wallet = self._create_wallet(config)
        try:
            assert len(wallet.get_seed()) > 0
            wallet.set_daemon_connection(daemon.get_rpc_connection())
            assert wallet.get_height() == 1
            assert wallet.is_synced() is False
            assert wallet.get_balance() == 0
            chain_height: int = wallet.get_daemon_height()
            wallet.set_restore_height(chain_height - 3)
            wallet.start_syncing()
            assert chain_height - 3 == wallet.get_restore_height()
            AssertUtils.assert_equals(daemon.get_rpc_connection(), wallet.get_daemon_connection())
            wallet.stop_syncing()
            wallet.sync()
            wallet.stop_syncing()
            wallet.stop_syncing()
        finally:
            wallet.close()

        # test that sync starts automatically
        restore_height: int = daemon.get_height() - 100
        path = Utils.get_random_wallet_path()
        config = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = restore_height
        wallet = self._create_wallet(config, False)
        try:
            # start syncing
            assert wallet.get_height() == 1
            assert wallet.get_restore_height() == restore_height
            assert wallet.is_synced() is False
            assert wallet.get_balance() == 0
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)

            # pause for sync to start
            sleep(1 + (Utils.SYNC_PERIOD_IN_MS / 1000))

            # test that wallet has started syncing
            assert wallet.get_height() > 1

            # stop syncing
            wallet.stop_syncing()

            # TODO monero-project: wallet.cpp m_synchronized only ever set to true, never false
        finally:
            wallet.close()

    # Does not interfere with other wallet notifications
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_wallets_do_not_interfere(self, daemon: MoneroDaemonRpc) -> None:
        # create 2 wallets with a recent restore height
        height: int = daemon.get_height()
        restore_height: int = height - 5
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = Utils.SEED
        config.restore_height = restore_height
        wallet1: MoneroWalletFull = self._create_wallet(config, False)

        config = MoneroWalletConfig()
        config.seed = Utils.SEED
        config.restore_height = restore_height
        wallet2: MoneroWalletFull = self._create_wallet(config, False)

        # track notifications of each wallet
        tester1: SyncProgressTester = SyncProgressTester(wallet1, restore_height, height)
        tester2: SyncProgressTester = SyncProgressTester(wallet2, restore_height, height)
        wallet1.add_listener(tester1)
        wallet2.add_listener(tester2)

        # sync first wallet and test that 2nd is not notified
        wallet1.sync()
        assert tester1.is_notified
        assert not tester2.is_notified

        # sync 2nd wallet and test that 1st is not notified
        tester3: SyncProgressTester = SyncProgressTester(wallet1, restore_height, height)
        wallet1.add_listener(tester3)
        wallet2.sync()
        assert tester2.is_notified
        assert not tester3.is_notified

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_subaddress(self, wallet: MoneroWalletFull) -> None: # type: ignore
        # create subaddresses across accounts
        accounts: list[MoneroAccount] = wallet.get_accounts()
        if len(accounts) < 2:
            wallet.create_account()

        accounts = wallet.get_accounts()
        assert len(accounts) > 1
        account_idx: int = 0
        while account_idx < 2:
            # create subaddress with no label
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            subaddress: MoneroSubaddress = wallet.create_subaddress(account_idx)
            assert subaddress.label is None
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            assert len(subaddresses_new) - 1 == len(subaddresses)
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = wallet.get_subaddresses(account_idx)
            uuid: str = StringUtils.get_random_string()
            subaddress = wallet.create_subaddress(account_idx, uuid)
            assert uuid == subaddress.label
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses) == len(subaddresses_new) - 1
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])
            account_idx += 1

    # Can be closed
    # TODO demonstration of monero-cpp segmentation fault bug
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="TODO monero-cpp closed and re-opened wallet full causes segmentation fault")
    def test_close(self) -> None:
        # create test wallet
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        wallet: MoneroWalletFull = self._create_wallet(config)
        wallet.sync()
        assert wallet.get_height() > 1, "Wallet height is still 1"
        assert wallet.is_synced(), "Wallet is not synced"
        # TODO monero-cpp add monero_wallet::is_closed()
        #assert wallet.is_closed() is False

        # close wallet
        wallet.close()
        # TODO monero-cpp add monero_wallet::is_closed()
        #assert wallet.is_closed()

        # attempt to interact with the wallet
        try:
            wallet.get_height()
        except Exception as e:
            WalletUtils.test_wallet_is_closed_error(e)

        try:
            wallet.get_seed()
        except Exception as e:
            WalletUtils.test_wallet_is_closed_error(e)

        # TODO calling monero_wallet_full::sync() on a closed wallet causes segmentation fault
        try:
            wallet.sync()
        except Exception as e:
            WalletUtils.test_wallet_is_closed_error(e)

        try:
            wallet.start_syncing()
        except Exception as e:
            WalletUtils.test_wallet_is_closed_error(e)

        try:
            wallet.stop_syncing()
        except Exception as e:
            WalletUtils.test_wallet_is_closed_error(e)

        # re-open the wallet
        config = MoneroWalletConfig()
        config.path = path
        # TODO calling monero_wallet_full::sync() on a re-opened wallet causes segmentation fault
        wallet = self._open_wallet(config)
        wallet.sync()
        assert wallet.get_daemon_height() == wallet.get_height()
        # TODO monero-cpp add monero_wallet::is_closed()
        #assert wallet.is_closed() is False

        # close the wallet
        wallet.close()
        # TODO monero-cpp add monero_wallet::is_closed()
        #assert wallet.is_closed()

    # Supports multisig sample code
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_multisig_sample(self) -> None:
        self._test_multisig_sample(1, 2)
        self._test_multisig_sample(1, 4)
        self._test_multisig_sample(2, 2)
        self._test_multisig_sample(2, 3)
        self._test_multisig_sample(2, 4)

    @pytest.mark.skipif(Utils.REGTEST, reason="Cannot retrieve accurate height by date from regtest fakechain")
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet):
        return super().test_get_height_by_date(wallet)

    @pytest.mark.skipif(Utils.REGTEST is False, reason="REGTEST disabled")
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.xfail(raises=RuntimeError, reason="Month or day out of range")
    def test_get_height_by_date_regtest(self, wallet: MoneroWallet):
        return super().test_get_height_by_date(wallet)

    #endregion

    #region Disabled Tests

    @pytest.mark.skip(reason="TODO disabled because importing key images deletes corresponding incoming transfers: https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self, wallet: MoneroWallet):
        return super().test_import_key_images(wallet)

    #endregion

    #region Utils

    def _test_multisig_sample(self, m: int, n: int) -> None:
        """
        Test multisig sample code.

        :param int m: multisig threshold.
        :param int n: number of participants.
        """
        # create participant wallets
        wallets: list[MoneroWalletFull] = []
        for i in range(n):
            wallets.append(self._create_wallet(MoneroWalletConfig()))
            logger.debug(f"Created multisig wallet participant {i + 1}")

        tester: MultisigSampleCodeTester = MultisigSampleCodeTester(m, wallets)
        tester.test()

    def _test_sync_seed(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletFull, start_height: Optional[int], restore_height: Optional[int], skip_gt_comparison: bool = False, test_post_sync_notifications: bool = False) -> None:
        tester: SyncSeedTester = SyncSeedTester(daemon, wallet, self._create_wallet, start_height, restore_height, skip_gt_comparison, test_post_sync_notifications)
        tester.test()

    #endregion
