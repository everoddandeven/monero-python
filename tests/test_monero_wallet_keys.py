import pytest
import logging

from typing import Optional
from typing_extensions import override
from monero import (
    MoneroWalletKeys, MoneroWalletConfig, MoneroWallet,
    MoneroUtils, MoneroAccount, MoneroSubaddress,
    MoneroError, MoneroDaemonRpc, MoneroDaemon
)
from utils import TestUtils as Utils, AssertUtils, WalletUtils

from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletKeys")


@pytest.mark.unit
class TestMoneroWalletKeys(BaseTestMoneroWallet):
    """Keys-only wallet unit tests"""

    _account_indices: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    _subaddress_indices: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @pytest.fixture(scope="class", autouse=True)
    @override
    def before_all(self):
        pass

    @pytest.fixture(scope="class")
    @override
    def wallet(self) -> MoneroWalletKeys:
        """Test keys wallet instance"""
        return Utils.get_wallet_keys()

    @pytest.fixture(scope="class")
    @override
    def daemon(self) -> MoneroDaemonRpc:
        return MoneroDaemon() # type: ignore

    #region Overrides

    @classmethod
    @override
    def is_random_wallet_config(cls, config: Optional[MoneroWalletConfig]) -> bool:
        assert config is not None
        return super().is_random_wallet_config(config) and config.private_spend_key is None

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig]):
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()

        random: bool = self.is_random_wallet_config(config)
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE

        # create wallet
        if random:
            wallet = MoneroWalletKeys.create_wallet_random(config)
        elif config.seed is not None and config.seed != "":
            wallet = MoneroWalletKeys.create_wallet_from_seed(config)
        elif config.primary_address is not None and config.private_view_key is not None:
            wallet = MoneroWalletKeys.create_wallet_from_keys(config)
        elif config.primary_address is not None and config.private_spend_key is not None:
            wallet = MoneroWalletKeys.create_wallet_from_keys(config)
        else:
            raise Exception("Invalid configuration")

        return wallet

    @override
    def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
        raise NotImplementedError("TestMoneroWalletKeys._open_wallet(): not supported")

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        # not supported by keys wallet
        pass

    @override
    def _get_seed_languages(self) -> list[str]:
        return self.get_test_wallet().get_seed_languages()

    @override
    def get_test_wallet(self) -> MoneroWalletKeys:
        return Utils.get_wallet_keys()

    #endregion

    #region Not Supported Tests

    @pytest.mark.not_supported
    @override
    def test_send(self, wallet: MoneroWallet) -> None:
        return super().test_send(wallet)

    @pytest.mark.not_implemented
    @override
    def test_send_with_payment_id(self, wallet: MoneroWallet) -> None:
        return super().test_send_with_payment_id(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_then_relay(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_then_relay_split(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_txs_wallet(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_wallet(wallet)

    @pytest.mark.not_supported
    @override
    def test_daemon(self, wallet: MoneroWallet) -> None:
        return super().test_daemon(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_max_peer_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_path(self) -> None:
        return super().test_get_path()

    @pytest.mark.not_supported
    @override
    def test_set_daemon_connection(self):
        return super().test_set_daemon_connection()

    @pytest.mark.not_supported
    @override
    def test_sync_without_progress(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet):
        return super().test_sync_without_progress(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        return super().test_subaddress_lookahead(wallet)

    @pytest.mark.xfail(raises=MoneroError, reason="monero_wallet_keys::get_integrated_address() not implemented")
    @override
    def test_decode_integrated_address(self, wallet: MoneroWallet):
        return super().test_decode_integrated_address(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_address_indices(self, wallet: MoneroWallet):
        return super().test_get_address_indices(wallet)

    @pytest.mark.not_supported
    @override
    def test_wallet_equality_ground_truth(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet):
        return super().test_wallet_equality_ground_truth(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_get_height(self, wallet: MoneroWallet):
        return super().test_get_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet):
        return super().test_get_height_by_date(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_all_balances(self, wallet: MoneroWallet):
        return super().test_get_all_balances(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_account_without_label(self, wallet: MoneroWallet):
        return super().test_create_account_without_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_account_with_label(self, wallet: MoneroWallet):
        return super().test_create_account_with_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_account_label(self, wallet: MoneroWallet):
        return super().test_set_account_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_subaddresses_by_indices(self, wallet: MoneroWallet):
        return super().test_get_subaddresses_by_indices(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_subaddress(self, wallet: MoneroWallet):
        return super().test_create_subaddress(wallet)

    @pytest.mark.xfail(raises=MoneroError, reason="Keys-only wallet does not have enumerable set of subaddresses")
    @override
    def test_set_subaddress_label(self, wallet: MoneroWallet):
        return super().test_set_subaddress_label(wallet)

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
    def test_export_key_images(self, wallet: MoneroWallet):
        return super().test_export_key_images(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet):
        return super().test_get_new_key_images_from_last_import(wallet)

    @pytest.mark.not_supported
    @override
    def test_import_key_images(self, wallet: MoneroWallet):
        return super().test_import_key_images(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_payment_uri(self, wallet: MoneroWallet):
        return super().test_get_payment_uri(wallet)

    @pytest.mark.not_supported
    @override
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet):
        return super().test_mining(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_change_password(self) -> None:
        return super().test_change_password()

    @pytest.mark.not_supported
    @override
    def test_save_and_close(self) -> None:
        return super().test_save_and_close()

    #endregion

    #region Tests

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        config = MoneroWalletConfig()
        wallet = self._create_wallet(config)

        # validate wallet
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
        MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
        MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        # TODO monero-wallet-rpc: get seed language
        AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

        # attempt to create wallet with unknown language
        try:
            config = MoneroWalletConfig()
            config.language = "english"
            self._create_wallet(config)
            raise Exception("Should have thrown error")
        except Exception as e:
            AssertUtils.assert_equals("Unknown language: english", str(e))

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed(self, wallet: MoneroWallet, test_config: BaseTestMoneroWallet.Config) -> None:
        # save for comparison
        primary_address = wallet.get_primary_address()
        private_view_key = wallet.get_private_view_key()
        private_spend_key = wallet.get_private_spend_key()

        # recreate test wallet from seed
        config = MoneroWalletConfig()
        config.seed = Utils.SEED
        w: MoneroWallet = self._create_wallet(config)

        AssertUtils.assert_equals(primary_address, w.get_primary_address())
        AssertUtils.assert_equals(private_view_key, w.get_private_view_key())
        AssertUtils.assert_equals(private_spend_key, w.get_private_spend_key())
        AssertUtils.assert_equals(Utils.SEED, w.get_seed())
        AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, w.get_seed_language())

        # attempt to create wallet with two missing words
        try:
            config = MoneroWalletConfig()
            config.seed = test_config.seed
            self._create_wallet(config)
        except Exception as e:
            AssertUtils.assert_equals("Invalid mnemonic", str(e))

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed_with_offset(self) -> None:
        # create test wallet with offset
        config = MoneroWalletConfig()
        config.seed = Utils.SEED
        config.seed_offset = "my secret offset!"
        wallet: MoneroWallet = self._create_wallet(config)

        MoneroUtils.validate_mnemonic(wallet.get_seed())
        AssertUtils.assert_not_equals(Utils.SEED, wallet.get_seed())
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
        AssertUtils.assert_not_equals(Utils.ADDRESS, wallet.get_primary_address())
        # TODO monero-wallet-rpc: support
        AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_keys(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # save for comparison
        primary_address = wallet.get_primary_address()
        private_view_key = wallet.get_private_view_key()
        private_spend_key = wallet.get_private_spend_key()

        # recreate test wallet from keys
        config = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_view_key = private_view_key
        config.private_spend_key = private_spend_key
        w: MoneroWallet = self._create_wallet(config)

        try:
            AssertUtils.assert_equals(primary_address, w.get_primary_address())
            AssertUtils.assert_equals(private_view_key, w.get_private_view_key())
            AssertUtils.assert_equals(private_spend_key, w.get_private_spend_key())
            # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
            MoneroUtils.validate_mnemonic(w.get_seed())
            AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, w.get_seed_language())
        finally:
            self._close_wallet(w)

        # recreate test wallet from spend key
        config = MoneroWalletConfig()
        config.primary_address = primary_address
        config.private_spend_key = private_spend_key
        w = self._create_wallet(config)

        try:
            AssertUtils.assert_equals(primary_address, w.get_primary_address())
            AssertUtils.assert_equals(private_view_key, w.get_private_view_key())
            AssertUtils.assert_equals(private_spend_key, w.get_private_spend_key())
            # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
            MoneroUtils.validate_mnemonic(w.get_seed())
            AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, w.get_seed_language())
        finally:
            self._close_wallet(w)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address(self, wallet: MoneroWallet):
        AssertUtils.assert_equals(wallet.get_primary_address(), (wallet.get_address(0, 0)))
        accounts = self._get_test_accounts(wallet, True)

        for account in accounts:
            assert account is not None
            assert account.index is not None
            assert account.primary_address is not None
            MoneroUtils.validate_address(account.primary_address, Utils.NETWORK_TYPE)

            for subaddress in account.subaddresses:
                assert subaddress is not None
                assert subaddress.index is not None
                AssertUtils.assert_equals(subaddress.address, wallet.get_address(account.index, subaddress.index))

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet):
        accounts = self._get_test_accounts(wallet, True)
        account_idx = len(accounts) - 1
        subaddress_idx = len(accounts[account_idx].subaddresses)
        address = wallet.get_address(account_idx, subaddress_idx)
        AssertUtils.assert_not_none(address)
        AssertUtils.assert_true(len(address) > 0)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_account(self, wallet: MoneroWallet):
        accounts = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, Utils.NETWORK_TYPE, False)

            # test without subaddresses
            assert account.index is not None
            retrieved = wallet.get_account(account.index)
            assert len(retrieved.subaddresses) == 0

            # test with subaddresses
            retrieved = wallet.get_account(account.index)
            retrieved.subaddresses = wallet.get_subaddresses(account.index, self._subaddress_indices)

    @override
    def test_get_accounts_without_subaddresses(self, wallet: MoneroWallet):
        accounts = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, Utils.NETWORK_TYPE, False)
            assert len(account.subaddresses) == 0

    @override
    def test_get_accounts_with_subaddresses(self, wallet: MoneroWallet):
        accounts = self._get_test_accounts(wallet, True)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, Utils.NETWORK_TYPE, False)
            assert len(account.subaddresses) > 0

    @override
    def test_get_subaddresses(self, wallet: MoneroWallet):
        wallet = wallet
        accounts = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index, self._subaddress_indices)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                WalletUtils.test_subaddress(subaddress, False)
                assert account.index == subaddress.account_index

    @override
    def test_get_subaddress_by_index(self, wallet: MoneroWallet):
        accounts = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index, self._subaddress_indices)
            assert len(subaddresses) > 0

            for subaddress in subaddresses:
                assert subaddress.index is not None
                WalletUtils.test_subaddress(subaddress, False)
                AssertUtils.assert_subaddress_equal(subaddress, self._get_subaddress(wallet, account.index, subaddress.index))
                # test plural call with single subaddr number
                AssertUtils.assert_subaddress_equal(
                    subaddress, wallet.get_subaddresses(account.index, [subaddress.index])[0]
                )

    #endregion

    #region Utils

    def _get_subaddress(self, wallet: MoneroWallet, account_idx: int, subaddress_idx: int) -> Optional[MoneroSubaddress]:
        subaddress_indices: list[int] = [subaddress_idx]
        subaddresses = wallet.get_subaddresses(account_idx, subaddress_indices)

        if len(subaddresses) == 0:
            return None

        return subaddresses[0]

    def _get_test_accounts(self, wallet: MoneroWallet, include_subaddresses: bool = False) -> list[MoneroAccount]:
        account_indices = self._account_indices
        subaddress_indices = self._subaddress_indices
        accounts: list[MoneroAccount] = []
        for account_idx in account_indices:
            account = wallet.get_account(account_idx)

            if include_subaddresses:
                account.subaddresses = wallet.get_subaddresses(account_idx, subaddress_indices)

            accounts.append(account)

        return accounts

    #endregion
