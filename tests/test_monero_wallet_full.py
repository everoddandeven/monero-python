import pytest
import os

from typing import Optional
from typing_extensions import override
from monero import (
    MoneroWalletFull, MoneroWalletConfig, MoneroNetworkType, MoneroAccount,
    MoneroSubaddress, MoneroDaemonRpc, MoneroWallet
)

from utils import MoneroTestUtils as Utils
from .test_monero_wallet_common import BaseTestMoneroWallet


@pytest.mark.monero_wallet_full
class TestMoneroWalletFull(BaseTestMoneroWallet):

    _daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
    _wallet: MoneroWalletFull = Utils.get_wallet_full() # type: ignore

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig], startSyncing: bool = True):
        # assign defaults
        if config is None: 
            config = MoneroWalletConfig()
        random: bool = config.seed is None and config.primary_address is None
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
        if (not random):
            Utils.assert_equals(0 if config.restore_height is None else config.restore_height, wallet.get_restore_height())
        if (startSyncing is not False and wallet.is_connected_to_daemon()):
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)
        return wallet

    @override
    def _open_wallet(self, config: Optional[MoneroWalletConfig], startSyncing: bool = True) -> MoneroWalletFull:
        # assign defaults
        if config is None:
            config = MoneroWalletConfig();
        if config.password is None:
            config.password = Utils.WALLET_PASSWORD
        if config.network_type is not None:
            config.network_type = Utils.NETWORK_TYPE
        if config.server is None and config.connection_manager is None:
            config.server = self._daemon.get_rpc_connection()

        # open wallet
        assert config.network_type is not None
        assert config.path is not None

        wallet = MoneroWalletFull.open_wallet(config.path, config.password, config.network_type)
        if startSyncing is not False and wallet.is_connected_to_daemon():
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

    def test_wallet_creation_and_close(self):
        config_keys = MoneroWalletConfig()
        config_keys.language = "English"
        config_keys.network_type = MoneroNetworkType.TESTNET
        keys_wallet = MoneroWalletFull.create_wallet(config_keys)
        seed = keys_wallet.get_seed()

        config = MoneroWalletConfig()
        config.path = "test_wallet_sync"
        config.password = "password"
        config.network_type = MoneroNetworkType.TESTNET
        config.restore_height = 0
        config.seed = seed
        config.language = "English"

        wallet = MoneroWalletFull.create_wallet(config)
        assert wallet.is_view_only() is False
        wallet.close(save=False)

        for ext in ["", ".keys", ".address.txt"]:
            try:
                os.remove(f"test_wallet_sync{ext}")
            except FileNotFoundError:
                pass

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
            Utils.assert_is_none(subaddress.label)
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
