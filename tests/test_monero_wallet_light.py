import pytest
import logging

from typing import override
from monero import (
    MoneroWalletLight, MoneroWalletConfig, MoneroWallet, MoneroWalletKeys,
    MoneroDaemonRpc, MoneroRpcConnection, MoneroUtils, MoneroAccount, MoneroSyncResult,
    MoneroWalletFull
)

from utils import (
    TestUtils as Utils, WalletType, ViewOnlyAndOfflineWalletTester,
    WalletErrorUtils, AssertUtils, WalletUtils, SyncProgressTester,
    WalletEqualityUtils, MoneroDaemonLws
)
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletLight")


@pytest.mark.integration
class TestMoneroWalletLight(BaseTestMoneroWallet):
    """Light wallet integration tests."""

    @classmethod
    @override
    def get_wallet_type(cls) -> WalletType:
        return WalletType.LIGHT

    def _create_open_wallet(self, config: MoneroWalletConfig | None, create: bool = True, start_syncing: bool = True) -> MoneroWalletLight:
        """Create or open a light wallet."""
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE

        wallet: MoneroWalletLight
        rpc: MoneroRpcConnection = Utils.get_daemon_lws_connection()
        logger.info(f"create: {create}, config: {config.serialize()}")
        if create and not MoneroWalletLight.wallet_exists(config, rpc):
            # create wallet
            logger.info("creating wallet")
            wallet = MoneroWalletLight.create_wallet(config, rpc)
            logger.info(f"Created wallet {wallet.get_primary_address()}")
        else:
            # open wallet
            logger.info("opening wallet")
            wallet = MoneroWalletLight.open_wallet(config, rpc)

        if start_syncing and wallet.is_connected_to_daemon():
            wallet.sync()
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)

        # TODO ensure wallet is synced with the daemon

        return wallet

    @pytest.fixture(scope="class")
    def daemon_lws(self) -> MoneroDaemonLws:
        return Utils.get_daemon_lws()

    #region Overrides

    @pytest.fixture(scope="class")
    @override
    def wallet(self) -> MoneroWalletLight:
        """Test light wallet instance."""
        return self.get_test_wallet()

    @classmethod
    @override
    def get_test_wallet(cls) -> MoneroWalletLight:
        return super().get_test_wallet() # type: ignore

    @override
    def _open_wallet(self, config: MoneroWalletConfig | None, start_syncing: bool = True) -> MoneroWalletLight:
        return self._create_open_wallet(config, False, start_syncing)

    @override
    def _create_wallet(self, config: MoneroWalletConfig | None, start_syncing: bool = True) -> MoneroWalletLight:
        return self._create_open_wallet(config, True, start_syncing)

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)

    @override
    def _get_seed_languages(self) -> list[str]:
        return MoneroWalletLight.get_seed_languages()

    #endregion

    #region Tests

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        config = MoneroWalletConfig()
        wallet: MoneroWalletLight = self._create_wallet(config)
        seed: str = wallet.get_seed()

        try:
            MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
            MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
            MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
            MoneroUtils.validate_mnemonic(wallet.get_seed())
            assert MoneroWallet.DEFAULT_LANGUAGE == wallet.get_seed_language()
        finally:
            self._close_wallet(wallet)

        # attempt to create wallet at same path
        try:
            config = MoneroWalletConfig()
            config.seed = seed
            config.network_type = Utils.NETWORK_TYPE
            MoneroWalletLight.create_wallet(config, Utils.get_daemon_lws_connection())
            raise Exception("Should have thrown error")
        except Exception as e:
            e_msg: str = str(e)
            assert "Wallet already exists" == e_msg, e_msg

        # attempt to create wallet with unknown language
        try:
            config = MoneroWalletConfig()
            config.language = "english"
            config.network_type = Utils.NETWORK_TYPE
            self._create_wallet(config)
            raise Exception("Should have thrown error")
        except Exception as e:
            e_msg: str = str(e)
            assert "Unknown language: english" == e_msg, e_msg

    # Can create a light wallet from a seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed(self, wallet: MoneroWallet, test_config: BaseTestMoneroWallet.Config) -> None:
        # create random wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        random_wallet: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        seed: str = random_wallet.get_seed()

        # save for comparison
        primary_address = random_wallet.get_primary_address()
        private_view_key = random_wallet.get_private_view_key()
        private_spend_key = random_wallet.get_private_spend_key()

        config = MoneroWalletConfig()
        config.seed = seed

        w: MoneroWalletLight = self._create_wallet(config)

        try:
            assert primary_address == w.get_primary_address()
            assert private_view_key == w.get_private_view_key()
            assert private_spend_key == w.get_private_spend_key()
            assert Utils.SEED, w.get_seed()
            assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()
        finally:
            self._close_wallet(w)

        # attempt to create wallet at same path
        try:
            config = MoneroWalletConfig()
            config.seed = seed
            config.network_type = Utils.NETWORK_TYPE
            MoneroWalletLight.create_wallet(config, Utils.get_daemon_lws_connection())
            raise Exception("Should have thrown error")
        except Exception as e:
            e_msg: str = str(e)
            assert "Wallet already exists" == e_msg, e_msg

    # Can create a light wallet from keys
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # create random wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        random_wallet: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)

        # save for comparison
        primary_address = random_wallet.get_primary_address()
        private_view_key = random_wallet.get_private_view_key()
        private_spend_key = random_wallet.get_private_spend_key()

        config = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_view_key = private_view_key
        config.private_spend_key = private_spend_key

        w: MoneroWalletLight = self._create_wallet(config)

        try:
            assert primary_address == w.get_primary_address()
            assert private_view_key == w.get_private_view_key()
            assert private_spend_key == w.get_private_spend_key()
            assert Utils.SEED, w.get_seed()
            assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()
        finally:
            self._close_wallet(w)

        # attempt to create wallet at same path
        try:
            config = MoneroWalletConfig()
            config.primary_address = primary_address
            config.private_view_key = private_view_key
            config.private_spend_key = private_spend_key
            config.network_type = Utils.NETWORK_TYPE
            MoneroWalletLight.create_wallet(config, Utils.get_daemon_lws_connection())
            raise Exception("Should have thrown error")
        except Exception as e:
            e_msg: str = str(e)
            assert "Wallet already exists" in e_msg, e_msg

    # Can sync a wallet with a randomly generated seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.xfail(reason="monero-lws on regtest get stuck after a block reorg https://github.com/vtnerd/monero-lws/pull/286")
    def test_sync_random(self, daemon: MoneroDaemonRpc, daemon_lws: MoneroDaemonLws) -> None:
        assert daemon.is_connected(), "Not connected to daemon"

        # wait for lws's own scan progress to catch up to the daemon before creating the wallet,
        # otherwise the new account's start_height is assigned from lws's lagging scan height
        # instead of the daemon's live height. lws's scanned/start height is the 0-indexed height
        # of the last processed block, one less than daemon.get_height()'s block-count convention
        daemon_lws.wait_for_scan_height(Utils.ADDRESS, Utils.PRIVATE_VIEW_KEY, daemon.get_height() - 1)

        # create test wallet
        wallet: MoneroWalletLight = self._create_wallet(MoneroWalletConfig(), False)
        restore_height: int = daemon.get_height()

        # test wallet's height before syncing
        assert restore_height == wallet.get_daemon_height()
        assert wallet.is_connected_to_daemon()
        assert wallet.is_synced() is False
        assert wallet.get_height() == 1
        addr_info = daemon_lws.get_address_info(wallet.get_primary_address(), wallet.get_private_view_key())
        logger.info(f"wallet address info: {addr_info}")
        assert wallet.get_restore_height() == restore_height
        assert wallet.get_daemon_height() == daemon.get_height()

        # sync the wallet
        progress_tester: SyncProgressTester = SyncProgressTester(wallet, wallet.get_restore_height(), wallet.get_daemon_height())
        result: MoneroSyncResult = wallet.sync(progress_tester)
        logger.debug(f"Sync result: {result.serialize}")
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
            WalletEqualityUtils.test_wallet_equality_on_chain(wallet_gt, wallet)
        finally:
            wallet_gt.close(True)
            wallet.close()

        # attempt to sync unconnected wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        wallet = MoneroWalletLight.create_wallet(config, MoneroRpcConnection(Utils.OFFLINE_SERVER_URI))
        try:
            wallet.sync()
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg == "Wallet is not connected to daemon", e_msg
        finally:
            wallet.close()

    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False and Utils.TEST_RELAYS is False, reason="TEST_NON_RELAYS and TEST_RELAYS disabled")
    def test_view_only_and_offline_wallet_compatibility(self, wallet: MoneroWallet) -> None:
        # create view only wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.primary_address = wallet.get_primary_address()
        config.private_view_key = wallet.get_private_view_key()
        view_only_wallet: MoneroWalletLight = self._create_open_wallet(config)

        config = MoneroWalletConfig()
        config.primary_address = wallet.get_primary_address()
        config.private_view_key = wallet.get_private_view_key()
        config.private_spend_key = wallet.get_private_spend_key()
        config.server = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        config.restore_height = 0
        offline_wallet: MoneroWallet = Utils.create_wallet_full(config, False)
        assert offline_wallet.is_connected_to_daemon() is False
        view_only_wallet.sync()
        # test tx signing with wallets
        try:
            tester = ViewOnlyAndOfflineWalletTester(wallet, view_only_wallet, offline_wallet)
            tester.test()
        finally:
            self._close_wallet(view_only_wallet)
            self._close_wallet(offline_wallet)

    # Can be closed
    # TODO refactor test_monero_wallet_full::test_close
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_close(self) -> None:
        # create test wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = Utils.SEED
        wallet: MoneroWalletLight = self._create_wallet(config)
        try:
            wallet.sync()
            assert wallet.get_height() > 1, "Wallet height is still 1"
            # TODO lws stucks on blockchain height after a reorg
            #assert wallet.is_synced(), "Wallet is not synced"
            assert wallet.is_closed() is False

            # close wallet
            wallet.close()

            assert wallet.is_closed()

            # attempt to interact with the wallet
            try:
                wallet.get_height()
            except Exception as e:
                WalletErrorUtils.test_wallet_is_closed_error(e)

            try:
                wallet.get_seed()
            except Exception as e:
                WalletErrorUtils.test_wallet_is_closed_error(e)

            try:
                wallet.sync()
            except Exception as e:
                WalletErrorUtils.test_wallet_is_closed_error(e)

            try:
                wallet.start_syncing()
            except Exception as e:
                WalletErrorUtils.test_wallet_is_closed_error(e)

            try:
                wallet.stop_syncing()
            except Exception as e:
                WalletErrorUtils.test_wallet_is_closed_error(e)
        finally:
            # close() is idempotent, so this is safe even if already closed above
            self._close_wallet(wallet)

        # re-open the wallet
        config = MoneroWalletConfig()
        config.seed = Utils.SEED

        wallet = self._open_wallet(config)
        try:
            assert wallet.is_closed() is False
            wallet.sync()
            # TODO monero-lws get stuck when block reorgs occurs
            #assert wallet.get_daemon_height() == wallet.get_height()
            assert wallet.is_closed() is False
        finally:
            # close the wallet
            self._close_wallet(wallet)
        assert wallet.is_closed()

    # Can create a subaddress without label
    @override
    def test_create_subaddress(self, wallet: MoneroWallet) -> None:
        # create subaddresses across accounts
        accounts: list[MoneroAccount] = wallet.get_accounts()
        if len(accounts) < 2:
            wallet.create_account()

        accounts = wallet.get_accounts()
        assert len(accounts) > 1
        account_idx: int = 0
        while account_idx < 2:
            # create subaddress with no label
            subaddresses = wallet.get_subaddresses(account_idx)
            subaddress = wallet.create_subaddress(account_idx)
            assert subaddress.label is None
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses_new) - 1 == len(subaddresses)
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])
            account_idx += 1

    #endregion

    #region Not Supported Tests

    @pytest.mark.skip(reason="monero-lws does not support syncing with the pool")
    @override
    def test_sync_with_pool_same_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_same_accounts(daemon, wallet)

    @pytest.mark.skip(reason="monero-lws does not support syncing with the pool")
    @override
    def test_sync_with_pool_submit_and_relay(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_submit_and_relay(daemon, wallet)

    @pytest.mark.skip(reason="monero-lws does not support syncing with the pool")
    @override
    def test_sync_with_pool_relay(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_relay(daemon, wallet)

    @pytest.mark.skip(reason="monero-lws does not support syncing with the pool")
    @override
    def test_sync_with_pool_submit_and_flush(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_submit_and_flush(daemon, wallet)

    @pytest.mark.skip(reason="can't create two wallet on the same monero-lws instance")
    @override
    def test_view_only_and_offline_wallets(self, wallet: MoneroWallet) -> None:
        return super().test_view_only_and_offline_wallets(wallet)

    @pytest.mark.xfail(reason="monero-lws does not allow to fetch non-wallet transactions")
    @override
    def test_prove_unrelayed_txs(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_prove_unrelayed_txs(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
        return super().test_get_new_key_images_from_last_import(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_daemon_connection(self) -> None:
        return super().test_set_daemon_connection()

    @pytest.mark.not_supported
    @override
    def test_get_path(self) -> None:
        return super().test_get_path()

    @pytest.mark.not_supported
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        return super().test_get_height_by_date(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_account_with_label(self, wallet: MoneroWallet) -> None:
        return super().test_create_account_with_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_account_label(self, wallet: MoneroWallet) -> None:
        return super().test_set_account_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_subaddress_label(self, wallet: MoneroWallet) -> None:
        return super().test_set_subaddress_label(wallet)

    # monero-lws doesn't provide full on-chain data
    @pytest.mark.not_supported
    @override
    def test_get_reserve_proof_wallet(self, wallet: MoneroWallet) -> None:
        return super().test_get_reserve_proof_wallet(wallet)

    # monero-lws doesn't provide full on-chain data
    @pytest.mark.not_supported
    @override
    def test_get_reserve_proof_account(self, wallet: MoneroWallet) -> None:
        return super().test_get_reserve_proof_account(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_note(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_tx_notes(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_notes(wallet)

    @pytest.mark.not_supported
    @override
    def test_address_book(self, wallet: MoneroWallet) -> None:
        return super().test_address_book(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_attributes(self, wallet: MoneroWallet) -> None:
        return super().test_set_attributes(wallet)

    @pytest.mark.not_supported
    @override
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_mining(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_change_password(self) -> None:
        return super().test_change_password()

    @pytest.mark.not_supported
    @override
    def test_save_and_close(self) -> None:
        return super().test_save_and_close()

    @pytest.mark.not_supported
    @override
    def test_account_tags(self, wallet: MoneroWallet) -> None:
        return super().test_account_tags(wallet)

    @pytest.mark.not_supported
    @override
    def test_rescan_spent(self, wallet: MoneroWallet) -> None:
        return super().test_rescan_spent(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_dust(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_dust(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_dust_no_relay(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_dust_no_relay(wallet)

    @pytest.mark.not_supported
    @override
    def test_input_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_input_key_images(wallet)

    @pytest.mark.not_supported
    @override
    def test_check_spend_proof(self, wallet: MoneroWallet) -> None:
        return super().test_check_spend_proof(wallet)

    @pytest.mark.not_supported
    @override
    def test_check_tx_proof(self, wallet: MoneroWallet) -> None:
        return super().test_check_tx_proof(wallet)

    @pytest.mark.not_supported
    @override
    def test_import_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_import_outputs(wallet)

    #endregion

    #region Sweep Tests
    # kept last

    @pytest.mark.skipif(Utils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @override
    def test_sweep_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_outputs(wallet)

    @pytest.mark.skipif(Utils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    @override
    def test_sweep_wallet_by_accounts(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_wallet_by_accounts(wallet)

    @pytest.mark.skipif(Utils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    @override
    def test_sweep_wallet_by_subaddresses(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_wallet_by_subaddresses(wallet)

    #endregion
