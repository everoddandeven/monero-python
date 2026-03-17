import logging

from typing import Optional, Callable

from time import sleep
from monero import (
    MoneroDaemonRpc, MoneroWalletFull, MoneroWalletConfig,
    MoneroSyncResult, MoneroTxWallet
)
from .sync_progress_tester import SyncProgressTester
from .wallet_sync_tester import WalletSyncTester
from .test_utils import TestUtils
from .mining_utils import MiningUtils
from .wallet_equality_utils import WalletEqualityUtils

logger: logging.Logger = logging.getLogger("SyncSeedTester")


class SyncSeedTester:
    """Wallet sync from seed tester."""

    __test__ = False

    daemon: MoneroDaemonRpc
    """Test daemon instance."""
    wallet: MoneroWalletFull
    """Test wallet instance."""
    start_height: Optional[int]
    """Wallet start height."""
    restore_height: Optional[int]
    """Wallet restore height."""
    skip_gt_comparison: bool
    """Skip wallet ground truth comparision."""
    test_post_sync_notifications: bool
    """Test post-sync wallet notifications."""

    create_wallet: Callable[[MoneroWalletConfig, bool], MoneroWalletFull]
    """Create wallet function."""

    def __init__(self,
                 daemon: MoneroDaemonRpc,
                 wallet: MoneroWalletFull,
                 create_wallet: Callable[[MoneroWalletConfig, bool], MoneroWalletFull],
                 start_height: Optional[int],
                 restore_height: Optional[int],
                 skip_gt_comparison: bool = False,
                 test_post_sync_notifications: bool = False
                 ) -> None:
        """
        Initialize a new sync seed tester.

        :param MoneroDaemonRpc daemon: daemon test instance.
        :param MoneroWalletFull wallet: wallet test instance.
        :param Callable[[MoneroWalletConfig, bool], MoneroWalletFull] create_wallet: wallet creation function.
        :param int | None start_height: blockchain start height.
        :param int | None restore_height: wallet restore height.
        :param bool skip_gt_comparison: Skip wallet ground thruth verification (default `False`).
        :param bool test_post_sync_notifications: Test wallet post-sync notifications (default `False`).
        """
        self.daemon = daemon
        self.wallet = wallet
        self.create_wallet = create_wallet
        self.start_height = start_height
        self.restore_height = restore_height
        self.skip_gt_comparison = skip_gt_comparison
        self.test_post_sync_notifications = test_post_sync_notifications

    def test_notifications(self, wallet: MoneroWalletFull, start_height_expected: int, end_height_expected: int) -> None:
        """
        Test wallet notifications.

        :param MoneroWalletFull wallet: wallet to test.
        :param int start_height_expected: expected start height.
        :param int end_height_expected: expected end height.
        """
        # test wallet's height before syncing
        assert wallet.is_connected_to_daemon()
        assert wallet.is_synced() is False
        assert wallet.get_height() == 1
        assert wallet.get_restore_height() == self.restore_height

        # register a wallet listener which tests notifications throughout the sync
        wallet_sync_tester: WalletSyncTester = WalletSyncTester(wallet, start_height_expected, end_height_expected)
        wallet.add_listener(wallet_sync_tester)

        # sync the wallet with a listener which tests sync notifications
        progress_tester: SyncProgressTester = SyncProgressTester(wallet, start_height_expected, end_height_expected)
        result: MoneroSyncResult = wallet.sync(self.start_height, progress_tester) if self.start_height is not None else wallet.sync(progress_tester)

        # test completion of the wallet and sync listeners
        progress_tester.on_done(wallet.get_daemon_height())
        wallet_sync_tester.on_done(wallet.get_daemon_height())

        # test result after syncing
        assert wallet.is_synced()
        assert wallet.get_daemon_height() - start_height_expected == result.num_blocks_fetched
        assert result.received_money

        if wallet.get_height() != self.daemon.get_height():
            # TODO height may not be same after long sync
            logger.warning(f"wallet height {wallet.get_height()} is not synced with daemon height {self.daemon.get_height()}")

        assert wallet.get_daemon_height() == self.daemon.get_height()

        wallet_txs: list[MoneroTxWallet] = wallet.get_txs()
        assert len(wallet_txs) > 0
        wallet_tx: MoneroTxWallet = wallet_txs[0]
        tx_height: int | None = wallet_tx.get_height()
        assert tx_height is not None

        if start_height_expected > TestUtils.FIRST_RECEIVE_HEIGHT:
            assert tx_height > TestUtils.FIRST_RECEIVE_HEIGHT
        else:
            assert tx_height == TestUtils.FIRST_RECEIVE_HEIGHT

        # sync the wallet with default params
        result = wallet.sync()
        assert wallet.is_synced()
        assert self.daemon.get_height() == wallet.get_height()
        # block might be added to chain
        assert result.num_blocks_fetched == 0 or result.num_blocks_fetched == 1
        assert result.received_money is False

        # compare with ground truth
        if not self.skip_gt_comparison:
            wallet_gt = TestUtils.create_wallet_ground_truth(TestUtils.NETWORK_TYPE, wallet.get_seed(), self.start_height, self.restore_height)
            WalletEqualityUtils.test_wallet_full_equality_on_chain(wallet_gt, wallet)

        # if testing post-sync notifications, wait for a block to be added to the chain
        # then test that sync arg listener was not invoked and registered wallet listener was invoked
        if self.test_post_sync_notifications:
            # start automatic syncing
            wallet.start_syncing(TestUtils.SYNC_PERIOD_IN_MS)

            # attempt to start mining to push the network along
            MiningUtils.try_start_mining()

            try:
                logger.info("Waiting for next block to test post sync notifications")
                self.daemon.wait_for_next_block_header()

                # ensure wallet has time to detect new block
                sleep((TestUtils.SYNC_PERIOD_IN_MS / 1000) + 3)

                # test that wallet listener's onSyncProgress() and onNewBlock() were invoked after previous completion
                assert wallet_sync_tester.on_sync_progress_after_done
                assert wallet_sync_tester.on_new_block_after_done
            finally:
                MiningUtils.try_stop_mining()

    def test(self) -> None:
        """Do sync seed test."""
        # check test parameters
        assert self.daemon.is_connected(), "Not connected to daemon"
        if self.start_height is not None and self.restore_height is not None:
            assert self.start_height <= TestUtils.FIRST_RECEIVE_HEIGHT or self.restore_height <= TestUtils.FIRST_RECEIVE_HEIGHT

        # wait for txs to clear pool
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self.wallet)

        # create wallet from seed
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = TestUtils.SEED
        config.restore_height = self.restore_height
        wallet: MoneroWalletFull = self.create_wallet(config, False)

        # sanitize expected sync bounds
        if self.restore_height is None:
            self.restore_height = 0
        start_height_expected: int = self.start_height if self.start_height is not None else self.restore_height
        if start_height_expected == 0:
            start_height_expected = 1
        end_height_expected: int = wallet.get_daemon_max_peer_height()

        # test wallet and close as final step
        wallet_gt: Optional[MoneroWalletFull] = None
        try:
            self.test_notifications(wallet, start_height_expected, end_height_expected)
        finally:
            if wallet_gt is not None:
                wallet_gt.close(True)
            wallet.close()
