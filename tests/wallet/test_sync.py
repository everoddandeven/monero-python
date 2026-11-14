from __future__ import annotations

import logging
from datetime import datetime
from time import sleep
from typing import Optional

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroError,
    MoneroRpcConnection,
    MoneroSyncResult,
    MoneroTxWallet,
    MoneroWallet,
    MoneroWalletConfig,
    MoneroWalletFull,
    MoneroWalletRpc,
)
from typing_extensions import override

from utils import (
    AssertUtils,
    GenUtils,
    MiningUtils,
    SyncProgressTester,
    SyncSeedTester,
    TestUtils,
    TestUtils as Utils,
    TxWalletUtils,
    WalletEqualityUtils,
    WalletNotificationCollector,
    WalletTxsUtils,
)
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletSync")


class BaseTestMoneroWalletSync(BaseTestMoneroWallet):
    """Common wallet sync tests."""

    # Can sync (without progress)
    # TODO test syncing from start height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sync_without_progress(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        num_blocks: int = 100
        chain_height: int = daemon.get_height()
        assert chain_height >= num_blocks
        result: MoneroSyncResult = wallet.sync(chain_height - num_blocks) # sync end of chain
        assert result.num_blocks_fetched >= 0
        assert result.received_money is not None

    # Can get the current height that the wallet is synchronized to
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height(self, wallet: MoneroWallet) -> None:
        height: int = wallet.get_height()
        assert height >= 0

    # Can get a blockchain height by date
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        # collect dates to test starting 100 days ago
        day_ms: int = 24 * 60 * 60 * 1000
        # TODO monero-project: today's date can throw exception as "in future" so we test up to yesterday
        yesterday: int = GenUtils.current_timestamp() - day_ms
        dates: list[datetime] = []
        date_range: list[int] = list(range(99))
        date_range.reverse()

        for i in date_range:
            # subtract i days
            dates.append(datetime.fromtimestamp((yesterday - day_ms * i) / 1000))

        # test heights by date
        last_height: Optional[int] = None
        for date in dates:
            height: int = wallet.get_height_by_date(date.year + 1900, date.month + 1, date.day)
            assert (height >= 0)
            if last_height is not None:
                assert (height >= last_height)
            last_height = height

        assert last_height is not None
        assert (last_height >= 0)
        height = wallet.get_height()
        assert (height >= 0)

        # test future date
        tomorrow: datetime = datetime.fromtimestamp((yesterday + day_ms * 2) / 1000)
        with pytest.raises(MoneroError, match="specified date is in the future"):
            wallet.get_height_by_date(tomorrow.year + 1900, tomorrow.month + 1, tomorrow.day)

    # Can scan transactions by id
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    def test_scan_txs(self, wallet: MoneroWallet) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = wallet.get_seed()
        config.restore_height = 0
        scan_wallet: MoneroWallet = self._create_wallet(config)
        logger.debug("Created scan wallet")
        WalletTxsUtils.test_scan_txs(wallet, scan_wallet)

    # Can rescan spent
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    def test_rescan_spent(self, wallet: MoneroWallet) -> None:
        wallet.rescan_spent()

    # Can rescan the blockchain
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skip(reason="Disabled so tests don't delete local cache")
    def test_rescan_blockchain(self, wallet: MoneroWallet) -> None:
        wallet.rescan_blockchain()
        for tx in wallet.get_txs():
            TxWalletUtils.test_tx_wallet(tx)


@pytest.mark.integration
class TestMoneroWalletFullSync(FullWalletSupport, BaseTestMoneroWalletSync):
    """Full wallet sync integration tests."""

    def _test_sync_seed(
        self,
        daemon: MoneroDaemonRpc,
        wallet: MoneroWalletFull,
        start_height: Optional[int],
        restore_height: Optional[int],
        skip_gt_comparison: bool = False,
        test_post_sync_notifications: bool = False
    ) -> None:
        tester: SyncSeedTester = SyncSeedTester(
            daemon, wallet, self._create_wallet,
            start_height, restore_height,
            skip_gt_comparison, test_post_sync_notifications
        )
        tester.test()

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
            with pytest.raises(Exception) as exc_info:
                wallet.sync()
            assert str(exc_info.value) == "Wallet is not connected to daemon"
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
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        config.path = Utils.get_random_wallet_path()
        wallet: MoneroWalletFull = self._create_wallet(config)
        try:
            assert len(wallet.get_seed()) > 0
            assert wallet.get_height() == 1
            assert wallet.get_balance() == 0
            wallet.start_syncing()  # succeeds while offline, syncing when a daemon becomes reachable
        finally:
            wallet.close()

        # test connecting wallet
        config = MoneroWalletConfig()
        config.path = Utils.get_random_wallet_path()
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
        config = MoneroWalletConfig()
        config.path = Utils.get_random_wallet_path()
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

    @pytest.mark.skipif(Utils.REGTEST, reason="Cannot retrieve accurate height by date from regtest fakechain")
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        return super().test_get_height_by_date(wallet)

    @pytest.mark.skipif(Utils.REGTEST is False, reason="REGTEST disabled")
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height_by_date_regtest(self, wallet: MoneroWallet) -> None:
        # the base test's fixed dates fall outside a short regtest chain
        with pytest.raises(RuntimeError):
            super().test_get_height_by_date(wallet)

    # Can wait for the next block to be added and be notified of its height
    @pytest.mark.skipif(Utils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=[])
    def test_wait_for_next_block(self, wallet: MoneroWalletFull) -> None:
        height_before: int = wallet.get_height()
        MiningUtils.try_start_mining()
        try:
            height: int = wallet.wait_for_next_block()
            # the notification carries the height of the new block, which is the chain
            # length the wallet knew before it was added, so it is only greater when the wallet lagged behind
            assert height >= height_before
        finally:
            MiningUtils.try_stop_mining()


@pytest.mark.integration
class TestMoneroWalletRpcSync(RpcWalletSupport, BaseTestMoneroWalletSync):
    """Rpc wallet sync integration tests."""

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sync_progress(self, wallet: MoneroWalletRpc) -> None:
        listener: WalletNotificationCollector = WalletNotificationCollector()
        # expected error message
        ERR_MSG: str = "Monero Wallet RPC does not support reporting sync progress"

        # sync with listener
        with pytest.raises(Exception) as exc_info:
            wallet.sync(listener)
        assert str(exc_info.value) == ERR_MSG

        # sync with listener from start height
        with pytest.raises(Exception) as exc_info:
            wallet.sync(0, listener)
        assert str(exc_info.value) == ERR_MSG

    # Can set the poll period for wallet notifications
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_poll_period_in_ms(self, wallet: MoneroWalletRpc) -> None:
        try:
            wallet.set_poll_period_in_ms(1000)
        finally:
            # restore the configured period so later tests poll at the expected rate
            wallet.set_poll_period_in_ms(Utils.SYNC_PERIOD_IN_MS)

    @pytest.mark.not_supported
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        return super().test_get_height_by_date(wallet)


@pytest.mark.unit
class TestMoneroWalletKeysSync(KeysWalletSupport, BaseTestMoneroWalletSync):
    """Keys-only wallet sync unit tests."""

    @pytest.mark.not_supported
    @override
    def test_sync_without_progress(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_without_progress(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_get_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        return super().test_get_height_by_date(wallet)

    @pytest.mark.not_supported
    @override
    def test_scan_txs(self, wallet: MoneroWallet) -> None:
        return super().test_scan_txs(wallet)

    @pytest.mark.not_supported
    @override
    def test_rescan_blockchain(self, wallet: MoneroWallet) -> None:
        return super().test_rescan_blockchain(wallet)

    @pytest.mark.not_supported
    @override
    def test_rescan_spent(self, wallet: MoneroWallet) -> None:
        return super().test_rescan_spent(wallet)
