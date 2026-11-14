from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroDestination,
    MoneroError,
    MoneroNetworkType,
    MoneroRpcConnection,
    MoneroTxConfig,
    MoneroTxWallet,
    MoneroUtils,
    MoneroVersion,
    MoneroWallet,
    MoneroWalletConfig,
    MoneroWalletFull,
    MoneroWalletKeys,
    MoneroWalletRpc,
)
from typing_extensions import override

from utils import (
    AssertUtils,
    GenUtils,
    StringUtils,
    SyncProgressTester,
    TestUtils,
    TestUtils as Utils,
    TxWalletUtils,
    ViewOnlyAndOfflineWalletTester,
    WalletErrorUtils,
    WalletUtils,
)
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletCreation")


class BaseTestMoneroWalletCreation(BaseTestMoneroWallet):
    """Common wallet creation tests."""

    # Can create a random wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        wallet: MoneroWallet = self._create_wallet(config)
        path: str = wallet.get_path()

        try:
            MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
            MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
            MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
            MoneroUtils.validate_mnemonic(wallet.get_seed())
            if not isinstance(wallet, MoneroWalletRpc):
                # TODO monero-wallet-rpc: get seed language
                assert MoneroWallet.DEFAULT_LANGUAGE == wallet.get_seed_language()
        finally:
            self._close_wallet(wallet)

        # attempt to create wallet at same path
        config = MoneroWalletConfig()
        config.path = path
        with pytest.raises(Exception) as exc_info:
            self._create_wallet(config)
        assert str(exc_info.value) == "Wallet already exists: " + path

        # attempt to create wallet with unknown language
        config = MoneroWalletConfig()
        config.language = "english"
        with pytest.raises(Exception) as exc_info:
            self._create_wallet(config)
        assert str(exc_info.value) == "Unknown language: english"

    # Can create a wallet from a seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed(self, wallet: MoneroWallet, test_config: BaseTestMoneroWallet.Config) -> None:
        # save for comparison
        primary_address: str = wallet.get_primary_address()
        private_view_key: str = wallet.get_private_view_key()
        private_spend_key: str = wallet.get_private_spend_key()

        # recreate test wallet from seed
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = TestUtils.SEED
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT

        w: MoneroWallet = self._create_wallet(config)
        path: str = w.get_path()
        try:
            assert primary_address == w.get_primary_address()
            assert private_view_key == w.get_private_view_key()
            assert private_spend_key == w.get_private_spend_key()
            assert TestUtils.SEED, w.get_seed()
            if not isinstance(w, MoneroWalletRpc):
                assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()
        finally:
            self._close_wallet(w)

        # attempt to create wallet with two missing words
        config = MoneroWalletConfig()
        config.seed = test_config.seed
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
        with pytest.raises(Exception) as exc_info:
            self._create_wallet(config)
        assert str(exc_info.value) == "Invalid mnemonic"

        # attempt to create wallet at same path
        config = MoneroWalletConfig()
        config.path = path
        with pytest.raises(Exception) as exc_info:
            self._create_wallet(config)
        assert str(exc_info.value) == "Wallet already exists: " + path

    # Can create a wallet from a seed with offset
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed_with_offset(self) -> None:
        # create test wallet with offset
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = TestUtils.SEED
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
        config.seed_offset = "my secret offset!"
        wallet: MoneroWallet = self._create_wallet(config)
        try:
            MoneroUtils.validate_mnemonic(wallet.get_seed())
            assert TestUtils.SEED != wallet.get_seed()
            MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
            assert TestUtils.ADDRESS != wallet.get_primary_address()
            if not isinstance(wallet, MoneroWalletRpc):
                # TODO monero-wallet-rpc: support
                assert MoneroWallet.DEFAULT_LANGUAGE == wallet.get_seed_language()
        finally:
            self._close_wallet(wallet)

    # Can create a wallet from keys
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # save for comparison
        primary_address: str = wallet.get_primary_address()
        private_view_key: str = wallet.get_private_view_key()
        private_spend_key: str = wallet.get_private_spend_key()

        # recreate test wallet from keys
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_view_key = private_view_key
        config.private_spend_key = private_spend_key
        config.restore_height = daemon.get_height()
        w: MoneroWallet = self._create_wallet(config)
        path: str = w.get_path()

        try:
            assert primary_address == w.get_primary_address()
            assert private_view_key == w.get_private_view_key()
            assert private_spend_key == w.get_private_spend_key()
            if not w.is_connected_to_daemon():
                # TODO monero-project: keys wallets not connected
                logger.warning(f"WARNING: {WalletErrorUtils.CREATED_WALLET_KEYS_ERROR}")
            assert w.is_connected_to_daemon(), WalletErrorUtils.CREATED_WALLET_KEYS_ERROR
            if not isinstance(w, MoneroWalletRpc):
                # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                MoneroUtils.validate_mnemonic(w.get_seed())
                assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()
        finally:
            self._close_wallet(w)

        # recreate test wallet from spend key
        if not isinstance(w, MoneroWalletRpc): # TODO monero-wallet-rpc: cannot create wallet from spend key?
            config = MoneroWalletConfig()
            config.private_spend_key = private_spend_key
            config.restore_height = daemon.get_height()
            w = self._create_wallet(config)

            try:
                assert primary_address == w.get_primary_address()
                assert private_view_key == w.get_private_view_key()
                assert private_spend_key == w.get_private_spend_key()
                if not w.is_connected_to_daemon():
                    # TODO monero-project: keys wallets not connected
                    logger.warning(f"{WalletErrorUtils.CREATED_WALLET_KEYS_ERROR}")
                assert w.is_connected_to_daemon(), WalletErrorUtils.CREATED_WALLET_KEYS_ERROR
                if not isinstance(w, MoneroWalletRpc):
                    # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                    MoneroUtils.validate_mnemonic(w.get_seed())
                    assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()
            finally:
                self._close_wallet(w)

        # attempt to create wallet at same path
        config = MoneroWalletConfig()
        config.path = path
        with pytest.raises(Exception) as exc_info:
            self._create_wallet(config)
        assert str(exc_info.value) == "Wallet already exists: " + path

    # Can create wallets with subaddress lookahead
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        receiver: MoneroWallet | None = None
        try:
            # create wallet with high subaddress lookahead
            config: MoneroWalletConfig = MoneroWalletConfig()
            config.account_lookahead = 1
            config.subaddress_lookahead = 100000
            receiver = self._create_wallet(config)

            # transfer funds to subaddress with high index
            tx_config: MoneroTxConfig = MoneroTxConfig()
            tx_config.account_index = 0
            dest: MoneroDestination = MoneroDestination()
            dest.address = receiver.get_subaddress(0, 85000).address
            dest.amount = TxWalletUtils.MAX_FEE
            tx_config.destinations.append(dest)
            tx_config.relay = True

            wallet.create_tx(tx_config)

            # observe unconfirmed funds
            GenUtils.wait_for(1000)
            receiver.sync()
            assert receiver.get_balance() > 0
        finally:
            if receiver is not None:
                self._close_wallet(receiver)

    # Can get the wallet's version
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_version(self, wallet: MoneroWallet) -> None:
        version: MoneroVersion = wallet.get_version()
        assert version.number is not None
        assert version.number > 0
        assert version.is_release is not None

    # Can get the wallet's path
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_path(self) -> None:
        # create random wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        wallet: MoneroWallet = self._create_wallet(config)

        # set a random attribute
        #String uuid = UUID.randomUUID().toString()
        uuid: str = StringUtils.get_random_string()
        wallet.set_attribute("uuid", uuid)

        # record the wallet's path then save and close
        path: str = wallet.get_path()
        self._close_wallet(wallet, True)

        # re-open the wallet using its path
        wallet = self._open_wallet_from_path(path, None)

        # test the attribute
        assert uuid == wallet.get_attribute("uuid")
        self._close_wallet(wallet)

    # Can change the wallet password
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_change_password(self) -> None:
        # create random wallet
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.password = TestUtils.WALLET_PASSWORD
        wallet: MoneroWallet = self._create_wallet(config)
        path: str = wallet.get_path()

        # change password
        new_password: str = ""
        wallet.change_password(TestUtils.WALLET_PASSWORD, new_password)

        # close wallet without saving
        self._close_wallet(wallet)

        # old password does not work (password change is auto saved)
        config = MoneroWalletConfig()
        config.path = path
        config.password = TestUtils.WALLET_PASSWORD
        with pytest.raises(Exception) as exc_info:
            self._open_wallet(config)
        # TODO: different errors from rpc and wallet2
        e_str = str(exc_info.value).lower()
        assert "failed to open wallet" in e_str or "invalid password" in e_str

        # open wallet with new password
        config = MoneroWalletConfig()
        config.path = path
        config.password = new_password
        wallet = self._open_wallet(config)

        # change password with incorrect password
        with pytest.raises(Exception) as exc_info:
            wallet.change_password("badpassword", new_password)
        assert "Invalid original password." == str(exc_info.value)
        # save and close
        self._close_wallet(wallet, True)

        # open wallet
        config = MoneroWalletConfig()
        config.path = path
        config.password = new_password
        wallet = self._open_wallet(config)

        # close wallet
        self._close_wallet(wallet)

    # Can save and close the wallet in a single call
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_save_and_close(self) -> None:
        # create random wallet
        password: str = ""
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.password = password
        wallet: MoneroWallet = self._create_wallet(config)
        path: str = wallet.get_path()

        # set an attribute
        uuid: str = StringUtils.get_random_string()
        wallet.set_attribute("id", uuid)

        # close the wallet without saving
        self._close_wallet(wallet)

        # re-open the wallet and ensure attribute was not saved
        config = MoneroWalletConfig()
        config.path = path
        config.password = password
        wallet = self._open_wallet(config)
        assert wallet.get_attribute("id") == ""

        # set the attribute and close with saving
        wallet.set_attribute("id", uuid)
        self._close_wallet(wallet, True)

        # re-open the wallet and ensure attribute was saved
        wallet = self._open_wallet(config)
        assert uuid == wallet.get_attribute("id")
        self._close_wallet(wallet)

    # Supports view-only and offline wallets to create, sign and submit transactions
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False and TestUtils.TEST_RELAYS is False, reason="TEST_NON_RELAYS and TEST_RELAYS disabled")
    def test_view_only_and_offline_wallets(self, wallet: MoneroWallet) -> None:
        # create view-only and offline wallets
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.primary_address = wallet.get_primary_address()
        config.private_view_key = wallet.get_private_view_key()
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
        view_only_wallet: MoneroWallet = self._create_wallet(config)

        config = MoneroWalletConfig()
        config.primary_address = wallet.get_primary_address()
        config.private_view_key = wallet.get_private_view_key()
        config.private_spend_key = wallet.get_private_spend_key()
        config.server = MoneroRpcConnection(TestUtils.OFFLINE_SERVER_URI)
        config.restore_height = 0
        offline_wallet: MoneroWallet = self._create_wallet(config)
        assert offline_wallet.is_connected_to_daemon() is False
        view_only_wallet.sync()

        # test tx signing with wallets
        try:
            tester: ViewOnlyAndOfflineWalletTester = ViewOnlyAndOfflineWalletTester(wallet, view_only_wallet, offline_wallet)
            tester.test()
        finally:
            self._close_wallet(view_only_wallet)
            self._close_wallet(offline_wallet)

    # Can get and set arbitrary key/value attributes
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_attributes(self, wallet: MoneroWallet) -> None:
        # set attributes
        attrs: dict[str, str] = {}
        for i in range(5):
            key: str = f"attr{i}"
            val: str = StringUtils.get_random_string()
            attrs[key] = val
            wallet.set_attribute(key, val)

        # test attributes
        for key in attrs:
            val = attrs[key]
            assert val == wallet.get_attribute(key)

        # get an undefined attribute
        assert wallet.get_attribute("unset_key") == ""


@pytest.mark.integration
class TestMoneroWalletFullCreation(FullWalletSupport, BaseTestMoneroWalletCreation):
    """Full wallet creation integration tests."""

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

        # cannot get daemon chain height: wallet2 masks errors from untrusted daemons
        with pytest.raises(Exception) as exc_info:
            wallet.get_daemon_height()
        assert str(exc_info.value) == "daemon error"

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
        wallet.start_syncing()  # succeeds while offline, syncing when a daemon becomes reachable

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
        assert wallet.get_restore_height() == restore_height
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

    # Can be closed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_close(self) -> None:
        # create test wallet
        path: str = Utils.get_random_wallet_path()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        wallet: MoneroWalletFull = self._create_wallet(config)
        wallet.sync()
        assert wallet.get_height() > 1, "Wallet height is still 1"
        assert wallet.is_synced(), "Wallet is not synced"
        assert wallet.is_closed() is False

        # close wallet
        wallet.close()

        assert wallet.is_closed()

        # attempt to interact with the wallet
        with pytest.raises(Exception) as exc_info:
            wallet.get_height()
        WalletErrorUtils.test_wallet_is_closed_error(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            wallet.get_seed()
        WalletErrorUtils.test_wallet_is_closed_error(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            wallet.sync()
        WalletErrorUtils.test_wallet_is_closed_error(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            wallet.start_syncing()
        WalletErrorUtils.test_wallet_is_closed_error(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            wallet.stop_syncing()
        WalletErrorUtils.test_wallet_is_closed_error(exc_info.value)

        # re-open the wallet
        config = MoneroWalletConfig()
        config.path = path

        wallet = self._open_wallet(config)
        assert wallet.is_closed() is False
        wallet.sync()
        assert wallet.get_daemon_height() == wallet.get_height()
        assert wallet.is_closed() is False

        # close the wallet
        wallet.close()
        assert wallet.is_closed()


@pytest.mark.integration
class TestMoneroWalletRpcCreation(RpcWalletSupport, BaseTestMoneroWalletCreation):
    """Rpc wallet creation integration tests."""

    # Can create a wallet with a randomly generated seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_random_rpc(self) -> None:
        # create random wallet with defaults
        path: str = StringUtils.get_random_string()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        wallet: MoneroWalletRpc = self._create_wallet(config)
        seed: str = wallet.get_seed()
        MoneroUtils.validate_mnemonic(seed)
        assert Utils.SEED != seed
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
        # very quick because restore height is chain height
        wallet.sync()
        self._close_wallet(wallet)

        # create random wallet non defaults
        path = StringUtils.get_random_string()
        config = MoneroWalletConfig()
        config.path = path
        config.language = "Spanish"
        wallet = self._create_wallet(config)
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        assert seed != wallet.get_seed()
        seed = wallet.get_seed()
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)

        # attempt to create wallet which already exists
        with pytest.raises(MoneroError) as exc_info:
            wallet.create_wallet(config)
        assert str(exc_info.value) == f"Wallet already exists: {path}"
        assert seed == wallet.get_seed()

        self._close_wallet(wallet)

    # Can create a RPC wallet from a seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed_rpc(self, daemon: MoneroDaemonRpc) -> None:
        # create wallet with seed and defaults
        path: str = StringUtils.get_random_string()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        wallet: MoneroWalletRpc = self._create_wallet(config)

        # validate wallet
        assert Utils.SEED == wallet.get_seed()
        assert Utils.ADDRESS == wallet.get_primary_address()
        wallet.sync()
        assert daemon.get_height() == wallet.get_height()
        txs: list[MoneroTxWallet] = wallet.get_txs()
        # expect used wallet
        assert len(txs) > 0, "Wallet is not used"
        assert Utils.FIRST_RECEIVE_HEIGHT == txs[0].get_height()
        # TODO: monero-wallet-rpc: if wallet is not closed, primary address will not change
        self._close_wallet(wallet)

        # create wallet with non-defaults
        path = StringUtils.get_random_string()
        config = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        config.language = "German"
        config.seed_offset = "my offset!"
        config.save_current = False
        wallet = self._create_wallet(config)

        # validate wallet
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        assert wallet.get_seed() != Utils.SEED
        assert wallet.get_primary_address() != Utils.ADDRESS
        assert not wallet.is_view_only()
        wallet.sync()
        assert daemon.get_height() == wallet.get_height()
        txs = wallet.get_txs()
        # expect non used wallet
        assert len(txs) == 0, "Wallet is used"
        self._close_wallet(wallet)

    # Can open wallets
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_open_wallet(self)-> None:
        # create names of tests wallets
        num_test_wallets: int = 1
        names: list[str] = [ ]
        for i in range(num_test_wallets):
            logger.debug(f"Creating test wallet {i + 1}")
            names.append(StringUtils.get_random_string())

        # create test wallets
        seeds: list[str] = []
        for name in names:
            config: MoneroWalletConfig = MoneroWalletConfig()
            config.path = name
            wallet: MoneroWalletRpc = self._create_wallet(config)
            seeds.append(wallet.get_seed())
            self._close_wallet(wallet, True)

        # open test wallets
        wallets: list[MoneroWalletRpc] = []
        for i in range(num_test_wallets):
            config: MoneroWalletConfig = MoneroWalletConfig()
            config.path = names[i]
            config.password = Utils.WALLET_PASSWORD
            wallet: MoneroWalletRpc = self._open_wallet(config)
            assert seeds[i] == wallet.get_seed()
            wallets.append(wallet)

        # attempt to open non-existent
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = "btc_integrity"
        config.password = Utils.WALLET_PASSWORD
        with pytest.raises(Exception):
            self._open_wallet(config)

        # close wallets:
        for wallet in wallets:
            self._close_wallet(wallet)

    # Can save the wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_save(self, wallet: MoneroWallet) -> None:
        wallet.save()

    # Can close a wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_close(self, daemon: MoneroDaemonRpc) -> None:
        # create a test wallet
        path: str = StringUtils.get_random_string()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        wallet: MoneroWalletRpc = self._create_wallet(config)
        wallet.sync()

        # close the wallet
        wallet.close()
        Utils.free_wallet_rpc_resource(wallet)

        # attempt to interact with the wallet
        with pytest.raises(Exception) as exc_info:
            wallet.get_height()
        WalletErrorUtils.test_no_wallet_file_error(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            wallet.get_seed()
        WalletErrorUtils.test_no_wallet_file_error(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            wallet.sync()
        WalletErrorUtils.test_no_wallet_file_error(exc_info.value)

        # re-open the wallet
        wallet.open_wallet(path, Utils.WALLET_PASSWORD)
        wallet.sync()
        assert daemon.get_height() == wallet.get_height()

        # close the wallet
        self._close_wallet(wallet, True)

    # Can stop the RPC server
    @pytest.mark.skip(reason="Disabled so server not actually stopped")
    def test_stop(self, wallet: MoneroWalletRpc) -> None:
        wallet.stop()

    @pytest.mark.not_supported
    @override
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        return super().test_subaddress_lookahead(wallet)


@pytest.mark.unit
class TestMoneroWalletKeysCreation(KeysWalletSupport, BaseTestMoneroWalletCreation):
    """Keys-only wallet creation unit tests."""

    @pytest.mark.not_supported
    @override
    def test_get_path(self) -> None:
        return super().test_get_path()

    @pytest.mark.not_supported
    @override
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        return super().test_subaddress_lookahead(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_attributes(self, wallet: MoneroWallet) -> None:
        return super().test_set_attributes(wallet)

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
    def test_view_only_and_offline_wallets(self, wallet: MoneroWallet) -> None:
        return super().test_view_only_and_offline_wallets(wallet)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        wallet: MoneroWalletKeys = self._create_wallet(config)

        # validate wallet
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
        MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
        MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        # TODO monero-wallet-rpc: get seed language
        assert MoneroWallet.DEFAULT_LANGUAGE == wallet.get_seed_language()

        # attempt to create wallet with unknown language
        config = MoneroWalletConfig()
        config.language = "english"
        with pytest.raises(Exception, match="Unknown language: english"):
            self._create_wallet(config)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed(self, wallet: MoneroWallet, test_config: BaseTestMoneroWallet.Config) -> None:
        # save for comparison
        primary_address: str = wallet.get_primary_address()
        private_view_key: str = wallet.get_private_view_key()
        private_spend_key: str = wallet.get_private_spend_key()

        # recreate test wallet from seed
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = Utils.SEED
        w: MoneroWallet = self._create_wallet(config)

        assert primary_address == w.get_primary_address()
        assert private_view_key == w.get_private_view_key()
        assert private_spend_key == w.get_private_spend_key()
        assert Utils.SEED == w.get_seed()
        assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()

        # attempt to create wallet with two missing words
        config = MoneroWalletConfig()
        config.seed = test_config.seed
        with pytest.raises(Exception) as exc_info:
            self._create_wallet(config)
        assert str(exc_info.value) == "Invalid mnemonic"

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed_with_offset(self) -> None:
        # create test wallet with offset
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = Utils.SEED
        config.seed_offset = "my secret offset!"
        wallet: MoneroWallet = self._create_wallet(config)

        MoneroUtils.validate_mnemonic(wallet.get_seed())
        assert Utils.SEED != wallet.get_seed()
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
        assert Utils.ADDRESS != wallet.get_primary_address()
        assert MoneroWallet.DEFAULT_LANGUAGE == wallet.get_seed_language()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_keys(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # save for comparison
        primary_address: str = wallet.get_primary_address()
        private_view_key: str = wallet.get_private_view_key()
        private_spend_key: str = wallet.get_private_spend_key()

        # recreate test wallet from keys
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_view_key = private_view_key
        config.private_spend_key = private_spend_key
        w: MoneroWallet = self._create_wallet(config)
        WalletUtils.test_wallet_keys(primary_address, private_view_key, private_spend_key, w)
        assert w.get_network_type() == Utils.NETWORK_TYPE
        assert not w.is_closed()
        w.close()

        # recreate test wallet from spend key
        config = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_spend_key = private_spend_key
        w = self._create_wallet(config)
        WalletUtils.test_wallet_keys(primary_address, private_view_key, private_spend_key, w)
        assert w.get_network_type() == Utils.NETWORK_TYPE
        assert not w.is_closed()
        w.close()

        # recreate test wallet from view keys
        config = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_view_key = private_view_key
        w = self._create_wallet(config)
        logger.info(f"Created wallet with config: {config.serialize()}")
        assert primary_address == w.get_primary_address()
        assert private_view_key == w.get_private_view_key()
        assert w.get_network_type() == Utils.NETWORK_TYPE
        assert w.is_view_only()
        # a view-only keys wallet has no seed
        with pytest.raises(RuntimeError, match="watch-only"):
            w.get_seed()
        assert not w.is_closed()
        w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys_no_keys(self) -> None:
        """
        create_wallet_from_keys() must require at least one of the private spend/view keys.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        with pytest.raises(RuntimeError, match="Neither spend key nor view key supplied"):
            MoneroWalletKeys.create_wallet_from_keys(config)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys_invalid_spend_key(self) -> None:
        """
        create_wallet_from_keys() must fail to parse a malformed private spend key.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        config.private_spend_key = "not-a-valid-hex-secret-key"
        with pytest.raises(RuntimeError, match="failed to parse secret spend key"):
            MoneroWalletKeys.create_wallet_from_keys(config)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys_invalid_view_key(self) -> None:
        """
        create_wallet_from_keys() must fail to parse a malformed private view key.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        config.primary_address = Utils.ADDRESS
        config.private_view_key = "not-a-valid-hex-secret-key"
        with pytest.raises(RuntimeError, match="failed to parse secret view key"):
            MoneroWalletKeys.create_wallet_from_keys(config)

    # Test invalid wallet configuration
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_keys_view_key_without_address(self) -> None:
        """
        create_wallet_from_keys() must require a primary address when a private view key is given.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        config.private_view_key = "a" * 64

        with pytest.raises(RuntimeError, match="must provide address if providing private view key"):
            MoneroWalletKeys.create_wallet_from_keys(config)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_is_closed(self) -> None:
        """A keys-only wallet reports its open/closed state and rejects use once closed."""
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)

        # a freshly created wallet is open
        assert w.is_closed() is False
        primary_address: str = w.get_primary_address()

        # closing it (without saving) marks it closed
        w.close()
        assert w.is_closed() is True

        # any accessor now raises "Wallet is closed"
        with pytest.raises(RuntimeError, match="Wallet is closed"):
            w.get_primary_address()
        with pytest.raises(RuntimeError, match="Wallet is closed"):
            w.get_private_view_key()

        # closing an already-closed wallet is a no-op (and does not re-raise)
        w.close()
        assert w.is_closed() is True

        # sanity: the address read before closing is unaffected
        MoneroUtils.validate_address(primary_address, Utils.NETWORK_TYPE)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_close_with_save_not_supported(self) -> None:
        """`close(save=True)` is rejected because a keys-only wallet has nothing to persist."""
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)

        with pytest.raises(RuntimeError, match="does not support saving"):
            w.close(True)

        # the failed save-and-close left the wallet open
        assert w.is_closed() is False
        w.close()
