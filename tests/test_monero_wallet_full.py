import pytest
import logging

from typing import Optional
from typing_extensions import override
from monero import (
    MoneroWalletFull, MoneroWalletConfig, MoneroAccount,
    MoneroSubaddress, MoneroDaemonRpc, MoneroWallet
)

from utils import (
    TestUtils as Utils, StringUtils,
    AssertUtils, WalletUtils
)
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletFull")


@pytest.mark.integration
class TestMoneroWalletFull(BaseTestMoneroWallet):
    """Full wallet integration tests"""

    #region Overrides

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
            AssertUtils.assert_equals(
                0 if config.restore_height is None else config.restore_height, wallet.get_restore_height()
            )
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
    def get_test_wallet(self) -> MoneroWalletFull:
        return Utils.get_wallet_full()

    #endregion

    #region Tests

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_subaddress(self, wallet: MoneroWalletFull): # type: ignore
        # create subaddresses across accounts
        accounts: list[MoneroAccount] = wallet.get_accounts()
        if len(accounts) < 2:
            wallet.create_account()

        accounts = wallet.get_accounts()
        AssertUtils.assert_true(len(accounts) > 1)
        account_idx: int = 0
        while account_idx < 2:
            # create subaddress with no label
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            subaddress: MoneroSubaddress = wallet.create_subaddress(account_idx)
            # TODO fix monero-cpp/monero_wallet_full.cpp to return boost::none on empty label
            #assert subaddress.label is None
            assert subaddress.label is None or subaddress.label == ""
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            AssertUtils.assert_equals(len(subaddresses_new) - 1, len(subaddresses))
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = wallet.get_subaddresses(account_idx)
            uuid: str = StringUtils.get_random_string()
            subaddress = wallet.create_subaddress(account_idx, uuid)
            AssertUtils.assert_equals(uuid, subaddress.label)
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            AssertUtils.assert_equals(len(subaddresses), len(subaddresses_new) - 1)
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])
            account_idx += 1

    #endregion

    #region Disabled Tests

    @pytest.mark.skipif(Utils.REGTEST, reason="Cannot retrieve accurate height by date from regtest fakechain")
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet):
        return super().test_get_height_by_date(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_wallet_equality_ground_truth(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet):
        return super().test_wallet_equality_ground_truth(daemon, wallet)

    @pytest.mark.skip(reason="TODO fix MoneroTxConfig.serialize()")
    @override
    def test_get_payment_uri(self, wallet: MoneroWallet):
        return super().test_get_payment_uri(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_note(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_notes(self, wallet: MoneroWallet):
        return super().test_set_tx_notes(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_export_key_images(self, wallet: MoneroWallet):
        return super().test_export_key_images(wallet)

    @pytest.mark.skip(reason="TODO (monero-project): https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self, wallet: MoneroWallet):
        return super().test_import_key_images(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet):
        return super().test_get_new_key_images_from_last_import(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        return super().test_subaddress_lookahead(wallet)

    @pytest.mark.skip(reason="TODO fix segmentation fault")
    @override
    def test_set_account_label(self, wallet: MoneroWallet) -> None:
        super().test_set_account_label(wallet)

    #endregion
