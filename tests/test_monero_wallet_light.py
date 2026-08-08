import pytest
import logging

from typing import override
from monero import (
    MoneroWalletLight, MoneroWalletConfig, MoneroWallet,
    MoneroDaemonRpc, MoneroRpcConnection, MoneroUtils,
    MoneroWalletKeys
)

from utils import (
    TestUtils as Utils, WalletType, ViewOnlyAndOfflineWalletTester,
    WalletErrorUtils
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

        if create and not MoneroWalletLight.wallet_exists(config, rpc):
            # create wallet
            wallet = MoneroWalletLight.create_wallet(config, rpc)
        else:
            # open wallet
            wallet = MoneroWalletLight.open_wallet(config, rpc)

        if start_syncing and wallet.is_connected_to_daemon():
            wallet.sync()
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)

        # TODO ensure wallet is synced with the daemon

        return wallet

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

    @pytest.mark.xfail(reason="TODO txs are not mergeable")
    @override
    def test_wallet_equality_ground_truth(self, wallet: MoneroWallet) -> None:
        return super().test_wallet_equality_ground_truth(wallet)

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

    # Can create a wallet from a seed
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

    # Can create a wallet from keys
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

    @pytest.mark.not_supported
    @override
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_max_peer_height(wallet)

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

    @pytest.mark.not_supported
    @override
    def test_create_subaddress(self, wallet: MoneroWallet) -> None:
        return super().test_create_subaddress(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_reserve_proof_wallet(self, wallet: MoneroWallet) -> None:
        return super().test_get_reserve_proof_wallet(wallet)

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
    def test_update_locked_same_account_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_same_account_split(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_update_locked_different_accounts_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_different_accounts_split(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_send_dust_to_multiple_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_send_dust_to_multiple_split(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_send_from_subaddresses_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_from_subaddresses_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_then_relay_split(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_dust_no_relay(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_dust_no_relay(wallet)

    @pytest.mark.not_supported
    @override
    def test_subtract_fee_from(self, wallet: MoneroWallet) -> None:
        return super().test_subtract_fee_from(wallet)

    @pytest.mark.not_supported
    @override
    def test_subtract_fee_from_split(self, wallet: MoneroWallet) -> None:
        return super().test_subtract_fee_from_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_to_multiple_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_to_multiple_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_input_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_input_key_images(wallet)

    @pytest.mark.not_supported
    @override
    def test_prove_unrelayed_txs(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_prove_unrelayed_txs(daemon, wallet)

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
    def test_check_tx_key(self, wallet: MoneroWallet) -> None:
        return super().test_check_tx_key(wallet)

    @pytest.mark.not_supported
    @override
    def test_import_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_import_outputs(wallet)

    #endregion

    #region Sweep Tests
    # kept last in the file: these sweep everything back to the primary address, which would
    # starve earlier tests that need balance on non-primary subaddresses/accounts

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
