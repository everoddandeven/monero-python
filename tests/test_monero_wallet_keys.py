import pytest
import logging

from typing import Optional
from typing_extensions import override
from monero import (
    MoneroWalletKeys, MoneroWalletConfig, MoneroWallet,
    MoneroUtils, MoneroAccount, MoneroSubaddress
)
from utils import TestUtils as Utils

from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletKeys")


class TestMoneroWalletKeys(BaseTestMoneroWallet):

    _account_indices: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    _subaddress_indices: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    _wallet: MoneroWalletKeys = Utils.get_wallet_keys() # type: ignore

    @pytest.fixture(autouse=True)
    @override
    def before_each(self, request: pytest.FixtureRequest):
        logger.info(f"Before test {request.node.name}") # type: ignore
        yield
        logger.info(f"After test {request.node.name}") # type: ignore

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
        return self._wallet.get_seed_languages()

    @override
    def get_test_wallet(self) -> MoneroWallet:
        return Utils.get_wallet_keys()

    #endregion

    #region Disabled Tests

    @pytest.mark.skip(reason="Wallet path not supported")
    @override
    def test_get_path(self) -> None:
        return super().test_get_path()

    @pytest.mark.skip(reason="Connection not supported")
    @override
    def test_set_daemon_connection(self):
        return super().test_set_daemon_connection()

    @pytest.mark.skip(reason="Sync not supported")
    @override
    def test_sync_without_progress(self):
        return super().test_sync_without_progress()

    @pytest.mark.skip(reason="Subaddress lookahead not supported")
    @override
    def test_subaddress_lookahead(self) -> None:
        return super().test_subaddress_lookahead()

    @pytest.mark.skip(reason="Not implemented")
    @override
    def test_decode_integrated_address(self):
        return super().test_decode_integrated_address()

    @pytest.mark.skip(reason="Get address index not supported")
    @override
    def test_get_address_indices(self):
        return super().test_get_address_indices()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_wallet_equality_ground_truth(self):
        return super().test_wallet_equality_ground_truth()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_get_height(self):
        return super().test_get_height()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_get_height_by_date(self):
        return super().test_get_height_by_date()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_get_all_balances(self):
        return super().test_get_all_balances()

    @pytest.mark.skip(reason="Account creation not supported")
    @override
    def test_create_account_without_label(self):
        return super().test_create_account_without_label()

    @pytest.mark.skip(reason="Account/label creation not supported")
    @override
    def test_create_account_with_label(self):
        return super().test_create_account_with_label()

    @pytest.mark.skip(reason="Label creation not supported")
    @override
    def test_set_account_label(self):
        return super().test_set_account_label()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_get_subaddresses_by_indices(self):
        return super().test_get_subaddresses_by_indices()

    @pytest.mark.skip(reason="Subaddress creation not supported")
    @override
    def test_create_subaddress(self):
        return super().test_create_subaddress()

    @pytest.mark.skip(reason="Labels not supported")
    @override
    def test_set_subaddress_label(self):
        return super().test_set_subaddress_label()

    @pytest.mark.skip(reason="Tx note not supported")
    @override
    def test_set_tx_note(self) -> None:
        return super().test_set_tx_note()

    @pytest.mark.skip(reason="Tx note not supported")
    @override
    def test_set_tx_notes(self) -> None:
        return super().test_set_tx_notes()

    @pytest.mark.skip(reason="Export key images not supported")
    @override
    def test_export_key_images(self):
        return super().test_export_key_images()

    @pytest.mark.skip(reason="Import key images not supported")
    @override
    def test_get_new_key_images_from_last_import(self):
        return super().test_get_new_key_images_from_last_import()

    @pytest.mark.skip(reason="Import key images not supported")
    @override
    def test_import_key_images(self):
        return super().test_import_key_images()

    @pytest.mark.skip(reason="Payment uri not supported")
    @override
    def test_get_payment_uri(self):
        return super().test_get_payment_uri()

    @pytest.mark.skip(reason="Mining not supported")
    @override
    def test_mining(self):
        return super().test_mining()

    #endregion

    #region Tests

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        e1: Exception | None = None
        try:
            config = MoneroWalletConfig()
            wallet = self._create_wallet(config)
            e2: Exception | None = None

            try:
                MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
                MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
                MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
                MoneroUtils.validate_mnemonic(wallet.get_seed())
                # TODO monero-wallet-rpc: get seed language
                Utils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
            except Exception as e:
                e2 = e

            if e2 is not None:
                raise e2

        # attempt to create wallet with unknown language
            try:
                config = MoneroWalletConfig()
                config.language = "english"
                self._create_wallet(config)
                raise Exception("Should have thrown error")
            except Exception as e:
                Utils.assert_equals("Unknown language: english", str(e))

        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed(self, test_config: BaseTestMoneroWallet.Config) -> None:
        e1: Exception | None = None
        try:

            # save for comparison
            primary_address = self._wallet.get_primary_address()
            private_view_key = self._wallet.get_private_view_key()
            private_spend_key = self._wallet.get_private_spend_key()

            # recreate test wallet from seed
            config = MoneroWalletConfig()
            config.seed = Utils.SEED

            wallet: MoneroWallet = self._create_wallet(config)
            e2: Exception | None = None
            try:
                Utils.assert_equals(primary_address, wallet.get_primary_address())
                Utils.assert_equals(private_view_key, wallet.get_private_view_key())
                Utils.assert_equals(private_spend_key, wallet.get_private_spend_key())
                Utils.assert_equals(Utils.SEED, wallet.get_seed())
                Utils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
            except Exception as e:
                e2 = e

            if e2 is not None:
                raise e2

            # attempt to create wallet with two missing words
            try:
                config = MoneroWalletConfig()
                config.seed = test_config.seed
                self._create_wallet(config)
            except Exception as e:
                Utils.assert_equals("Invalid mnemonic", str(e))

        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_seed_with_offset(self) -> None:
        e1: Exception | None = None
        try:
            # create test wallet with offset
            config = MoneroWalletConfig()
            config.seed = Utils.SEED
            config.seed_offset = "my secret offset!"
            wallet: MoneroWallet = self._create_wallet(config)
            e2: Exception | None = None
            try:
                MoneroUtils.validate_mnemonic(wallet.get_seed())
                Utils.assert_not_equals(Utils.SEED, wallet.get_seed())
                MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
                Utils.assert_not_equals(Utils.ADDRESS, wallet.get_primary_address())
                # TODO monero-wallet-rpc: support
                Utils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
            except Exception as e:
                e2 = e

            if e2 is not None:
                raise e2
        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_wallet_from_keys(self) -> None:
        e1: Exception | None = None
        try:
            # save for comparison
            primary_address = self._wallet.get_primary_address()
            private_view_key = self._wallet.get_private_view_key()
            private_spend_key = self._wallet.get_private_spend_key()

            # recreate test wallet from keys
            config = MoneroWalletConfig()
            config.primary_address = primary_address
            config.private_view_key = private_view_key
            config.private_spend_key = private_spend_key
            wallet: MoneroWallet = self._create_wallet(config)
            e2: Exception | None = None
            try:
                Utils.assert_equals(primary_address, wallet.get_primary_address())
                Utils.assert_equals(private_view_key, wallet.get_private_view_key())
                Utils.assert_equals(private_spend_key, wallet.get_private_spend_key())
                # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                MoneroUtils.validate_mnemonic(wallet.get_seed())
                Utils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

            except Exception as e:
                e2 = e

            self._close_wallet(wallet)
            if e2 is not None:
                raise e2

            # recreate test wallet from spend key
            config = MoneroWalletConfig()
            config.primary_address = primary_address
            config.private_spend_key = private_spend_key
            wallet = self._create_wallet(config)
            e2 = None
            try:
                Utils.assert_equals(primary_address, wallet.get_primary_address())
                Utils.assert_equals(private_view_key, wallet.get_private_view_key())
                Utils.assert_equals(private_spend_key, wallet.get_private_spend_key())
                # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                MoneroUtils.validate_mnemonic(wallet.get_seed())
                Utils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

            except Exception as e:
                e2 = e

            self._close_wallet(wallet)
            if e2 is not None:
                raise e2

        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address(self):
        Utils.assert_equals(self._wallet.get_primary_address(), (self._wallet.get_address(0, 0)))
        accounts = self._get_test_accounts(True)

        for account in accounts:
            assert account is not None
            assert account.index is not None
            assert account.primary_address is not None
            MoneroUtils.validate_address(account.primary_address, Utils.NETWORK_TYPE)

            for subaddress in account.subaddresses:
                assert subaddress is not None
                assert subaddress.index is not None
                Utils.assert_equals(subaddress.address, self._wallet.get_address(account.index, subaddress.index))

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address_out_of_range(self):
        accounts = self._get_test_accounts(True)
        account_idx = len(accounts) - 1
        subaddress_idx = len(accounts[account_idx].subaddresses)
        address = self._wallet.get_address(account_idx, subaddress_idx)
        Utils.assert_not_none(address)
        Utils.assert_true(len(address) > 0)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_account(self):
        accounts = self._get_test_accounts()
        assert len(accounts) > 0
        for account in accounts:
            Utils.test_account(account, False)

            # test without subaddresses
            assert account.index is not None
            retrieved = self._wallet.get_account(account.index)
            assert len(retrieved.subaddresses) == 0

            # test with subaddresses
            retrieved = self._wallet.get_account(account.index)
            retrieved.subaddresses = self._wallet.get_subaddresses(account.index, self._subaddress_indices)

    @override
    def test_get_accounts_without_subaddresses(self):
        accounts = self._get_test_accounts()
        assert len(accounts) > 0
        for account in accounts:
            Utils.test_account(account, False)
            assert len(account.subaddresses) == 0

    @override
    def test_get_accounts_with_subaddresses(self):
        accounts = self._get_test_accounts(True)
        assert len(accounts) > 0
        for account in accounts:
            Utils.test_account(account, False)
            assert len(account.subaddresses) > 0

    @override
    def test_get_subaddresses(self):
        wallet = self._wallet
        accounts = self._get_test_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index, self._subaddress_indices)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                Utils.test_subaddress(subaddress, False)
                assert account.index == subaddress.account_index

    @override
    def test_get_subaddress_by_index(self):
        accounts = self._get_test_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = self._wallet.get_subaddresses(account.index, self._subaddress_indices)
            assert len(subaddresses) > 0

            for subaddress in subaddresses:
                assert subaddress.index is not None
                Utils.test_subaddress(subaddress, False)
                Utils.assert_subaddress_equal(subaddress, self._get_subaddress(account.index, subaddress.index))
                # test plural call with single subaddr number
                Utils.assert_subaddress_equal(
                    subaddress, self._wallet.get_subaddresses(account.index, [subaddress.index])[0]
                )

    #endregion

    #region Utils

    def _get_subaddress(self, account_idx: int, subaddress_idx: int) -> Optional[MoneroSubaddress]:
        subaddress_indices: list[int] = [subaddress_idx]
        subaddresses = self._wallet.get_subaddresses(account_idx, subaddress_indices)

        if len(subaddresses) == 0:
            return None

        return subaddresses[0]

    def _get_test_accounts(self, include_subaddresses: bool = False) -> list[MoneroAccount]:
        account_indices = self._account_indices
        subaddress_indices = self._subaddress_indices
        accounts: list[MoneroAccount] = []
        for account_idx in account_indices:
            account = self._wallet.get_account(account_idx)

            if include_subaddresses:
                account.subaddresses = self._wallet.get_subaddresses(account_idx, subaddress_indices)

            accounts.append(account)

        return accounts

    #endregion
