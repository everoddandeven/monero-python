import pytest
import logging

from typing import Optional
from typing_extensions import override
from monero import (
    MoneroWalletFull, MoneroWalletConfig, MoneroAccount,
    MoneroSubaddress, MoneroDaemonRpc, MoneroWallet
)

from utils import TestUtils as Utils
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletFull")


class TestMoneroWalletFull(BaseTestMoneroWallet):

    _daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
    _wallet: MoneroWalletFull = Utils.get_wallet_full() # type: ignore

    #region Overrides

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True):
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        random: bool = self.is_random_wallet_config(config)
        if config.path is None:
            config.path = Utils.TEST_WALLETS_DIR + "/" + Utils.get_random_string()
        if config.password is None:
            config.password = Utils.WALLET_PASSWORD
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE
        #if config.server is None and config.connection_manager is None:
        if config.server is None:
            config.server = self._daemon.get_rpc_connection()
        if config.restore_height is None and not random:
            config.restore_height = 0

        # create wallet
        wallet = MoneroWalletFull.create_wallet(config)
        if not random:
            Utils.assert_equals(
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
            config.server = self._daemon.get_rpc_connection()

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
        return self._wallet.get_seed_languages()

    @override
    def get_test_wallet(self) -> MoneroWallet:
        return Utils.get_wallet_full()

    @pytest.fixture(autouse=True)
    @override
    def before_each(self, request: pytest.FixtureRequest):
        logger.info(f"Before test {request.node.name}") # type: ignore
        yield
        logger.info(f"After test {request.node.name}") # type: ignore

    #endregion

    #region Tests

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_subaddress(self):
        # create subaddresses across accounts
        accounts: list[MoneroAccount] = self._wallet.get_accounts()
        if len(accounts) < 2:
            self._wallet.create_account()

        accounts = self._wallet.get_accounts()
        Utils.assert_true(len(accounts) > 1)
        account_idx: int = 0
        while account_idx < 2:
            # create subaddress with no label
            subaddresses: list[MoneroSubaddress] = self._wallet.get_subaddresses(account_idx)
            subaddress: MoneroSubaddress = self._wallet.create_subaddress(account_idx)
            # TODO fix monero-cpp/monero_wallet_full.cpp to return boost::none on empty label
            #assert subaddress.label is None
            assert subaddress.label is None or subaddress.label == ""
            Utils.test_subaddress(subaddress)
            subaddresses_new: list[MoneroSubaddress] = self._wallet.get_subaddresses(account_idx)
            Utils.assert_equals(len(subaddresses_new) - 1, len(subaddresses))
            Utils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = self._wallet.get_subaddresses(account_idx)
            uuid: str = Utils.get_random_string()
            subaddress = self._wallet.create_subaddress(account_idx, uuid)
            Utils.assert_equals(uuid, subaddress.label)
            Utils.test_subaddress(subaddress)
            subaddresses_new = self._wallet.get_subaddresses(account_idx)
            Utils.assert_equals(len(subaddresses), len(subaddresses_new) - 1)
            Utils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])
            account_idx += 1

    #endregion

    #region Disabled Tests

    @pytest.mark.skipif(Utils.REGTEST, reason="Cannot retrieve accurate height by date from regtest fakechain")
    @override
    def test_get_height_by_date(self):
        return super().test_get_height_by_date()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_wallet_equality_ground_truth(self):
        return super().test_wallet_equality_ground_truth()

    @pytest.mark.skip(reason="TODO fix MoneroTxConfig.serialize()")
    @override
    def test_get_payment_uri(self):
        return super().test_get_payment_uri()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_note(self) -> None:
        return super().test_set_tx_note()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_notes(self):
        return super().test_set_tx_notes()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_export_key_images(self):
        return super().test_export_key_images()

    @pytest.mark.skip(reason="TODO (monero-project): https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self):
        return super().test_import_key_images()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_new_key_images_from_last_import(self):
        return super().test_get_new_key_images_from_last_import()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_subaddress_lookahead(self) -> None:
        return super().test_subaddress_lookahead()

    @pytest.mark.skip(reason="TODO fix segmentation fault")
    @override
    def test_set_account_label(self) -> None:
        super().test_set_account_label()

    #endregion
