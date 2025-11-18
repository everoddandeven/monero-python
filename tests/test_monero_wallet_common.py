from __future__ import annotations
import pytest
from configparser import ConfigParser
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from monero import (
    MoneroWallet, MoneroWalletRpc, MoneroDaemonRpc, MoneroWalletConfig,
    MoneroTxConfig, MoneroDestination, MoneroRpcConnection, MoneroError,
    MoneroKeyImage, MoneroTxQuery, MoneroUtils
)
from utils import MoneroTestUtils as TestUtils, WalletEqualityUtils


@pytest.mark.monero_wallet_common
class BaseTestMoneroWallet(ABC):
    CREATED_WALLET_KEYS_ERROR: str = "Wallet created from keys is not connected to authenticated daemon"
    _wallet: MoneroWallet
    _daemon: MoneroDaemonRpc

    class Config:
        seed: str = ""

        @classmethod
        def parse(cls, parser: ConfigParser) -> BaseTestMoneroWallet.Config:
            section = "test_create_wallet_from_seed"
            if not parser.has_section(section):
                raise Exception(f"Cannot find section '{section}' in test_monero_wallet_common.ini")
            config = cls()
            config.seed = parser.get(section, "seed")
            return config

    # region Private Methods

    @classmethod
    def _get_test_daemon(cls) -> MoneroDaemonRpc:
        return TestUtils.get_daemon_rpc()

    @abstractmethod
    def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
        ...

    @abstractmethod
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWallet:
        ...

    @abstractmethod
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        ...

    @abstractmethod
    def _get_seed_languages(self) -> list[str]:
        ...

    def _open_wallet_from_path(self, path: str, password: str | None) -> MoneroWallet:
        config = MoneroWalletConfig()
        config.path = path
        config.password = password

        return self._open_wallet(config)

    @abstractmethod
    def get_test_wallet(self) -> MoneroWallet:
        ...

    @classmethod
    def is_random_wallet_config(cls, config: MoneroWalletConfig) -> bool:
        return config.seed is None and config.primary_address is None

    # endregion

    #region Fixtures

    @pytest.fixture(scope="class")
    def config(self) -> BaseTestMoneroWallet.Config:
        parser = ConfigParser()
        parser.read('config/test_monero_wallet_common.ini')
        return BaseTestMoneroWallet.Config.parse(parser)

    #endregion

    # region Tests
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        e1: Exception | None = None
        try:
            config = MoneroWalletConfig()
            wallet = self._create_wallet(config)
            path = wallet.get_path()
            e2: Exception | None = None

            try:
                MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
                MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
                MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
                MoneroUtils.validate_mnemonic(wallet.get_seed())
                if not isinstance(wallet, MoneroWalletRpc):
                    # TODO monero-wallet-rpc: get seed language
                    TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
            except Exception as e:
                e2 = e

            self._close_wallet(wallet)
            if e2 is not None:
                raise e2

            # attempt to create wallet at same path
            try:
                config = MoneroWalletConfig()
                config.path = path
                self._create_wallet(config)
            except Exception as e:
                TestUtils.assert_equals("Wallet already exists: " + path, str(e))

            # attempt to create wallet with unknown language
            try:
                config = MoneroWalletConfig()
                config.language = "english"
                raise Exception("Should have thrown error")
            except Exception as e:
                TestUtils.assert_equals("Unknown language: english", str(e))

        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed(self, test_config: BaseTestMoneroWallet.Config) -> None:
        e1: Exception | None = None
        try:

            # save for comparison
            primary_address = self._wallet.get_primary_address()
            private_view_key = self._wallet.get_private_view_key()
            private_spend_key = self._wallet.get_private_spend_key()

            # recreate test wallet from seed
            config = MoneroWalletConfig()
            config.seed = TestUtils.SEED
            config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT

            wallet: MoneroWallet = self._create_wallet(config)
            path = wallet.get_path()
            e2: Exception | None = None
            try:
                TestUtils.assert_equals(primary_address, wallet.get_primary_address())
                TestUtils.assert_equals(private_view_key, wallet.get_private_view_key())
                TestUtils.assert_equals(private_spend_key, wallet.get_private_spend_key())
                TestUtils.assert_equals(TestUtils.SEED, wallet.get_seed())
                if not isinstance(wallet, MoneroWalletRpc):
                    TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
            except Exception as e:
                e2 = e

            self._close_wallet(wallet)
            if e2 is not None:
                raise e2

            # attempt to create wallet with two missing words
            try:
                config = MoneroWalletConfig()
                config.seed = test_config.seed
                config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
                self._create_wallet(config)
            except Exception as e:
                TestUtils.assert_equals("Invalid mnemonic", str(e))

            # attempt to create wallet at same path
            try:
                config = MoneroWalletConfig()
                config.path = path
                self._create_wallet(config)
                raise Exception("Should have thrown error")
            except Exception as e:
                TestUtils.assert_equals("Wallet already exists: " + path, str(e))

        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed_with_offset(self) -> None:
        e1: Exception | None = None
        try:

            # create test wallet with offset
            config = MoneroWalletConfig()
            config.seed = TestUtils.SEED
            config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
            config.seed_offset = "my secret offset!"
            wallet: MoneroWallet = self._create_wallet(config)
            e2: Exception | None = None
            try:
                MoneroUtils.validate_mnemonic(wallet.get_seed())
                TestUtils.assert_not_equals(TestUtils.SEED, wallet.get_seed())
                MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
                TestUtils.assert_not_equals(TestUtils.ADDRESS, wallet.get_primary_address())
                if not isinstance(wallet, MoneroWalletRpc):
                    # TODO monero-wallet-rpc: support
                    TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
            except Exception as e:
                e2 = e

            self._close_wallet(wallet)
            if e2 is not None:
                raise e2
        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
            config.restore_height = self._daemon.get_height()
            wallet: MoneroWallet = self._create_wallet(config)
            path = wallet.get_path()
            e2: Exception | None = None
            try:
                TestUtils.assert_equals(primary_address, wallet.get_primary_address())
                TestUtils.assert_equals(private_view_key, wallet.get_private_view_key())
                TestUtils.assert_equals(private_spend_key, wallet.get_private_spend_key())
                if not wallet.is_connected_to_daemon():
                    # TODO monero-project: keys wallets not connected
                    print(f"WARNING: {self.CREATED_WALLET_KEYS_ERROR}")
                TestUtils.assert_true(wallet.is_connected_to_daemon(), self.CREATED_WALLET_KEYS_ERROR)
                if not isinstance(wallet, MoneroWalletRpc):
                    # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                    MoneroUtils.validate_mnemonic(wallet.get_seed())
                    TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

            except Exception as e:
                e2 = e

            self._close_wallet(wallet)
            if e2 is not None:
                raise e2

            # recreate test wallet from spend key
            if not isinstance(wallet, MoneroWalletRpc): # TODO monero-wallet-rpc: cannot create wallet from spend key?
                config = MoneroWalletConfig()
                config.private_spend_key = private_spend_key
                config.restore_height = self._daemon.get_height()
                wallet = self._create_wallet(config)
                e2 = None
                try:
                    TestUtils.assert_equals(primary_address, wallet.get_primary_address())
                    TestUtils.assert_equals(private_view_key, wallet.get_private_view_key())
                    TestUtils.assert_equals(private_spend_key, wallet.get_private_spend_key())
                    if not wallet.is_connected_to_daemon():
                        # TODO monero-project: keys wallets not connected
                        print(f"WARNING: {self.CREATED_WALLET_KEYS_ERROR}")
                    TestUtils.assert_true(wallet.is_connected_to_daemon(), self.CREATED_WALLET_KEYS_ERROR)
                    if not isinstance(wallet, MoneroWalletRpc):
                        # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                        MoneroUtils.validate_mnemonic(wallet.get_seed())
                        TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

                except Exception as e:
                    e2 = e
                
                self._close_wallet(wallet)
                if e2 is not None:
                    raise e2

            # attempt to create wallet at same path
            try:
                config = MoneroWalletConfig()
                config.path = path
                self._create_wallet(config)
                raise Exception("Should have thrown error")
            except Exception as e:
                TestUtils.assert_equals("Wallet already exists: " + path, str(e))

        except Exception as e:
            e1 = e

        if e1 is not None:
            raise e1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_subaddress_lookahead(self) -> None:
        e1: Exception | None = None
        receiver: MoneroWallet | None = None
        try:
            # create wallet with high subaddress lookahead
            config = MoneroWalletConfig()
            config.account_lookahead = 1
            config.subaddress_lookahead = 100000
            receiver = self._create_wallet(config)

            # transfer funds to subaddress with high index
            tx_config = MoneroTxConfig()
            tx_config.account_index = 0
            dest = MoneroDestination()
            dest.address = receiver.get_subaddress(0, 85000).address
            dest.amount = TestUtils.MAX_FEE
            tx_config.destinations.append(dest)
            tx_config.relay = True

            self._wallet.create_tx(tx_config)

            # observe unconfirmed funds
            TestUtils.wait_for(1000)
            receiver.sync()
            assert receiver.get_balance() > 0
        except Exception as e:
            e1 = e

        if receiver is not None:
            self._close_wallet(receiver)
        if e1 is not None:
            raise e1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_version(self) -> None:
        version = self._wallet.get_version()
        assert version.number is not None
        assert version.number > 0
        assert version.is_release is not None

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_path(self) -> None:
        # create random wallet
        config = MoneroWalletConfig()
        wallet = self._create_wallet(config)

        # set a random attribute
        #String uuid = UUID.randomUUID().toString()
        uuid = TestUtils.get_random_string()
        wallet.set_attribute("uuid", uuid)

        # record the wallet's path then save and close
        path = wallet.get_path()
        self._close_wallet(wallet, True)

        # re-open the wallet using its path
        wallet = self._open_wallet_from_path(path, None)

        # test the attribute
        TestUtils.assert_equals(uuid, wallet.get_attribute("uuid"))
        self._close_wallet(wallet)

    def test_set_daemon_connection(self):

        # create random wallet with default daemon connection
        config = MoneroWalletConfig()
        wallet = self._create_wallet(config)
        connection = MoneroRpcConnection(
            TestUtils.DAEMON_RPC_URI, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        TestUtils.assert_equals(connection, wallet.get_daemon_connection())
        TestUtils.assert_true(wallet.is_connected_to_daemon()) # uses default localhost connection

        # set empty server uri
        wallet.set_daemon_connection("")
        TestUtils.assert_equals(None, wallet.get_daemon_connection())
        TestUtils.assert_false(wallet.is_connected_to_daemon())

        # set offline server uri
        wallet.set_daemon_connection(TestUtils.OFFLINE_SERVER_URI)
        connection = MoneroRpcConnection(TestUtils.OFFLINE_SERVER_URI, "", "")
        TestUtils.assert_equals(connection, wallet.get_daemon_connection())
        TestUtils.assert_false(wallet.is_connected_to_daemon())

        # set daemon with wrong credentials
        wallet.set_daemon_connection(TestUtils.DAEMON_RPC_URI, "wronguser", "wrongpass")
        connection = MoneroRpcConnection(TestUtils.DAEMON_RPC_URI, "wronguser", "wrongpass")
        TestUtils.assert_equals(connection, wallet.get_daemon_connection())
        if "" == TestUtils.DAEMON_RPC_USERNAME:
            # TODO: monerod without authentication works with bad credentials?
            TestUtils.assert_true(wallet.is_connected_to_daemon())
        else:
            TestUtils.assert_false(wallet.is_connected_to_daemon())

        # set daemon with authentication
        wallet.set_daemon_connection(
            TestUtils.DAEMON_RPC_URI, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        connection = MoneroRpcConnection(
            TestUtils.DAEMON_RPC_URI, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        TestUtils.assert_equals(connection, wallet.get_daemon_connection())
        TestUtils.assert_true(wallet.is_connected_to_daemon())

        # nullify daemon connection
        wallet.set_daemon_connection(None)
        TestUtils.assert_equals(None, wallet.get_daemon_connection())
        wallet.set_daemon_connection(TestUtils.DAEMON_RPC_URI)
        connection = MoneroRpcConnection(TestUtils.DAEMON_RPC_URI)
        TestUtils.assert_equals(connection, wallet.get_daemon_connection())
        wallet.set_daemon_connection(None)
        TestUtils.assert_equals(None, wallet.get_daemon_connection())

        # set daemon uri to non-daemon
        wallet.set_daemon_connection("www.getmonero.org")
        connection = MoneroRpcConnection("www.getmonero.org")
        TestUtils.assert_equals(connection, wallet.get_daemon_connection())
        TestUtils.assert_false(wallet.is_connected_to_daemon())

        # set daemon to invalid uri
        wallet.set_daemon_connection("abc123")
        TestUtils.assert_false(wallet.is_connected_to_daemon())

        # attempt to sync
        try:
            wallet.sync()
            raise Exception("Exception expected")
        except Exception as e:
            TestUtils.assert_equals("Wallet is not connected to daemon", str(e))
        finally:
            self._close_wallet(wallet)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_seed(self):
        seed = self._wallet.get_seed()
        MoneroUtils.validate_mnemonic(seed)
        TestUtils.assert_equals(TestUtils.SEED, seed)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_seed_language(self):
        language = self._wallet.get_seed_language()
        TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, language)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_seed_languages(self):
        languages = self._get_seed_languages()
        assert len(languages) > 0
        for language in languages:
            assert len(language) > 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_private_view_key(self):
        private_view_key = self._wallet.get_private_view_key()
        MoneroUtils.validate_private_view_key(private_view_key)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_private_spend_key(self):
        private_spend_key = self._wallet.get_private_spend_key()
        MoneroUtils.validate_private_spend_key(private_spend_key)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_public_view_key(self):
        public_view_key = self._wallet.get_public_view_key()
        MoneroUtils.validate_private_spend_key(public_view_key)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_public_spend_key(self):
        public_spend_key = self._wallet.get_public_spend_key()
        MoneroUtils.validate_private_spend_key(public_spend_key)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_primary_address(self):
        primary_address = self._wallet.get_primary_address()
        MoneroUtils.validate_address(primary_address, TestUtils.NETWORK_TYPE)
        TestUtils.assert_equals(self._wallet.get_address(0, 0), primary_address)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_subaddress_address(self):
        TestUtils.assert_equals(self._wallet.get_primary_address(), (self._wallet.get_address(0, 0)))
        for account in self._wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert account.index is not None
                assert subaddress.index is not None
                TestUtils.assert_equals(subaddress.address, self._wallet.get_address(account.index, subaddress.index))

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_subaddress_address_out_of_range(self):
        accounts = self._wallet.get_accounts(True)
        account_idx = len(accounts) - 1
        subaddress_idx = len(accounts[account_idx].subaddresses)
        address = self._wallet.get_address(account_idx, subaddress_idx)
        TestUtils.assert_not_none(address)
        TestUtils.assert_true(len(address) > 0)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_address_indices(self):
        wallet = self._wallet
        # get last subaddress to test
        accounts = wallet.get_accounts(True)
        account_idx = len(accounts) - 1
        subaddress_idx = len(accounts[account_idx].subaddresses) - 1
        address = wallet.get_address(account_idx, subaddress_idx)
        TestUtils.assert_not_none(address)

        # get address index
        subaddress = wallet.get_address_index(address)
        TestUtils.assert_equals(account_idx, subaddress.account_index)
        TestUtils.assert_equals(subaddress_idx, subaddress.index)

        # test valid but unfound address
        non_wallet_address = TestUtils.get_external_wallet_address()
        try:
            wallet.get_address_index(non_wallet_address)
            raise Exception("Should have thrown exception")
        except Exception as e:
            TestUtils.assert_equals("Address doesn't belong to the wallet", str(e))

        # test invalid address
        try:
            wallet.get_address_index("this is definitely not an address")
            raise Exception("Should have thrown exception")
        except Exception as e:
            TestUtils.assert_equals("Invalid address", str(e))

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_decode_integrated_address(self):
        wallet = self._wallet
        integrated_address = wallet.get_integrated_address('', "03284e41c342f036")
        decoded_address = wallet.decode_integrated_address(integrated_address.integrated_address)
        TestUtils.assert_equals(integrated_address, decoded_address)

        # decode invalid address
        try:
            wallet.decode_integrated_address("bad address")
            raise Exception("Should have failed decoding bad address")
        except Exception as e:
            TestUtils.assert_equals("Invalid address", str(e))

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_sync_without_progress(self):
        wallet = self._wallet
        daemon = self._daemon
        num_blocks = 100
        chain_height = daemon.get_height()
        TestUtils.assert_true(chain_height >= num_blocks)
        result = wallet.sync(chain_height - num_blocks) # sync end of chain
        TestUtils.assert_true(result.num_blocks_fetched >= 0)
        TestUtils.assert_not_none(result.received_money)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_wallet_equality_ground_truth(self):
        wallet = self._wallet
        daemon = self._daemon
        TestUtils.WALLET_TX_TRACKER.wait_for_wallet_txs_to_clear_pool(daemon, TestUtils.SYNC_PERIOD_IN_MS, [wallet])
        wallet_gt = TestUtils.create_wallet_ground_truth(
            TestUtils.NETWORK_TYPE, TestUtils.SEED, None, TestUtils.FIRST_RECEIVE_HEIGHT
        )
        try:
            WalletEqualityUtils.test_wallet_equality_on_chain(
                daemon, TestUtils.SYNC_PERIOD_IN_MS, TestUtils.WALLET_TX_TRACKER, wallet_gt, wallet
            )
        finally:
            wallet_gt.close()

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_height(self):
        height = self._wallet.get_height()
        assert height >= 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_height_by_date(self):
        # collect dates to test starting 100 days ago
        day_ms = 24 * 60 * 60 * 1000
        # TODO monero-project: today's date can throw exception as "in future" so we test up to yesterday
        yesterday = TestUtils.current_timestamp() - day_ms
        dates: list[datetime] = []
        i = 99

        while i >= 0:
            dates.append(datetime.fromtimestamp((yesterday - day_ms * i) / 1000)) # subtract i days
            i -= 1

        # test heights by date
        last_height: Optional[int] = None
        for date in dates:
            height = self._wallet.get_height_by_date(date.year + 1900, date.month + 1, date.day)
            assert (height >= 0)
            if last_height is not None:
                assert (height >= last_height)
            last_height = height

        assert last_height is not None
        assert (last_height >= 0)
        height = self._wallet.get_height()
        assert (height >= 0)

        # test future date
        try:
            tomorrow = datetime.fromtimestamp((yesterday + day_ms * 2) / 1000)
            self._wallet.get_height_by_date(tomorrow.year + 1900, tomorrow.month + 1, tomorrow.day)
            raise Exception("Expected exception on future date")
        except MoneroError as err:
            assert "specified date is in the future" == str(err)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_all_balances(self):
        # fetch accounts with all info as reference
        accounts = self._wallet.get_accounts(True)
        wallet = self._wallet
        # test that balances add up between accounts and wallet
        accounts_balance = 0
        accounts_unlocked_balance = 0
        for account in accounts:
            assert account.index is not None
            assert account.balance is not None
            assert account.unlocked_balance is not None
            accounts_balance += account.balance
            accounts_unlocked_balance += account.unlocked_balance

            # test that balances add up between subaddresses and accounts
            subaddresses_balance = 0
            subaddresses_unlocked_balance = 0
            for subaddress in account.subaddresses:
                assert subaddress.account_index is not None
                assert subaddress.index is not None
                assert subaddress.balance is not None
                assert subaddress.unlocked_balance is not None
                subaddresses_balance += subaddress.balance
                subaddresses_unlocked_balance += subaddress.unlocked_balance

                # test that balances are consistent with get_accounts() call
                assert wallet.get_balance(subaddress.account_index, subaddress.index) == subaddress.balance
                unlocked_balance = wallet.get_unlocked_balance(subaddress.account_index, subaddress.index)
                assert unlocked_balance == subaddress.unlocked_balance

            assert wallet.get_balance(account.index) == subaddresses_balance
            assert wallet.get_unlocked_balance(account.index) == subaddresses_unlocked_balance

        TestUtils.test_unsigned_big_integer(accounts_balance)
        TestUtils.test_unsigned_big_integer(accounts_unlocked_balance)
        assert wallet.get_balance() == accounts_balance
        assert wallet.get_unlocked_balance() == accounts_unlocked_balance

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_accounts_without_subaddresses(self):
        accounts = self._wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            TestUtils.test_account(account)
            assert len(account.subaddresses) == 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_accounts_with_subaddresses(self):
        accounts = self._wallet.get_accounts(True)
        assert len(accounts) > 0
        for account in accounts:
            TestUtils.test_account(account)
            assert len(account.subaddresses) > 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_account(self):
        accounts = self._wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            TestUtils.test_account(account)

            # test without subaddresses
            assert account.index is not None
            retrieved = self._wallet.get_account(account.index)
            assert len(retrieved.subaddresses) == 0

            # test with subaddresses
            retrieved = self._wallet.get_account(account.index, True)
            assert len(retrieved.subaddresses) > 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_create_account_without_label(self):
        accounts_before = self._wallet.get_accounts()
        created_account = self._wallet.create_account()
        TestUtils.test_account(created_account)
        assert len(accounts_before) == len(self._wallet.get_accounts()) - 1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_create_account_with_label(self):
        wallet = self._wallet
        # create account with label
        accounts_before = wallet.get_accounts()
        label = TestUtils.get_random_string()
        created_account = wallet.create_account(label)
        TestUtils.test_account(created_account)
        assert created_account.index is not None
        assert len(accounts_before) == len(wallet.get_accounts()) - 1
        assert label == wallet.get_subaddress(created_account.index, 0).label

        # fetch and test account
        created_account = wallet.get_account(created_account.index)
        TestUtils.test_account(created_account)

        # create account with same label
        created_account = wallet.create_account(label)
        TestUtils.test_account(created_account)
        assert len(accounts_before) == len(wallet.get_accounts()) - 2
        assert created_account.index is not None
        assert label == wallet.get_subaddress(created_account.index, 0).label

        # fetch and test account
        created_account = wallet.get_account(created_account.index)
        TestUtils.test_account(created_account)

    def test_set_account_label(self):
        # create account
        wallet = self._wallet
        if len(wallet.get_accounts()) < 2:
            wallet.create_account()

        # set account label
        label = TestUtils.get_random_string()
        wallet.set_account_label(1, label)
        assert label == wallet.get_subaddress(1, 0).label

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_subaddresses(self):
        wallet = self._wallet
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                TestUtils.test_subaddress(subaddress)
                assert account.index == subaddress.account_index

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_subaddresses_by_indices(self):
        wallet = self._wallet
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:

            # get subaddresses
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0

            # remove a subaddress for query if possible
            if len(subaddresses) > 1:
                subaddresses.remove(subaddresses[0])

            # get subaddress indices
            subaddress_indices: list[int] = []
            for subaddress in subaddresses:
                assert subaddress.index is not None
                subaddress_indices.append(subaddress.index)
            assert len(subaddress_indices) > 0

            # fetch subaddresses by indices
            fetched_subaddresses = wallet.get_subaddresses(account.index, subaddress_indices)

            # original subaddresses (minus one removed if applicable) is equal to fetched subaddresses
            assert TestUtils.assert_subaddresses_equal(subaddresses, fetched_subaddresses)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_subaddress_by_index(self):
        wallet = self._wallet
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                assert subaddress.index is not None
                TestUtils.test_subaddress(subaddress)
                TestUtils.assert_subaddress_equal(subaddress, wallet.get_subaddress(account.index, subaddress.index))
                # test plural call with single subaddr number
                TestUtils.assert_subaddress_equal(
                    subaddress, wallet.get_subaddresses(account.index, [subaddress.index])[0]
                )

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_create_subaddress(self):
        wallet = self._wallet
        # create subaddresses across accounts
        accounts = wallet.get_accounts()
        if len(accounts) < 2:
            wallet.create_account()
        accounts = wallet.get_accounts()
        assert len(accounts) > 1
        account_idx = 0
        while account_idx < 2:

            # create subaddress with no label
            subaddresses = wallet.get_subaddresses(account_idx)
            subaddress = wallet.create_subaddress(account_idx)
            assert subaddress.label is None
            TestUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses_new) - 1 == len(subaddresses)
            TestUtils.assert_subaddress_equal(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = wallet.get_subaddresses(account_idx)
            uuid = TestUtils.get_random_string()
            subaddress = wallet.create_subaddress(account_idx, uuid)
            assert (uuid == subaddress.label)
            TestUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses) == len(subaddresses_new) - 1
            TestUtils.assert_subaddress_equal(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            account_idx += 1

    def test_set_subaddress_label(self):
        wallet = self._wallet
        # create subaddresses
        while len(wallet.get_subaddresses(0)) < 3:
            wallet.create_subaddress(0)

        # set subaddress labels
        subaddress_idx = 0
        while subaddress_idx < len(wallet.get_subaddresses(0)):
            label = TestUtils.get_random_string()
            wallet.set_subaddress_label(0, subaddress_idx, label)
            assert (label == wallet.get_subaddress(0, subaddress_idx).label)
            subaddress_idx += 1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_set_tx_note(self) -> None:
        wallet = self._wallet
        txs = TestUtils.get_random_transactions(wallet, None, 1, 5)

        # set notes
        uuid = TestUtils.get_random_string()
        i: int = 0

        while i < len(txs):
            tx_hash = txs[i].hash
            assert tx_hash is not None
            wallet.set_tx_note(tx_hash, f"{uuid}{i}")
            i += 1

        i = 0
        # get notes
        while i < len(txs):
            tx_hash = txs[i].hash
            assert tx_hash is not None
            assert wallet.get_tx_note(tx_hash) == f"{uuid}{i}"
            i += 1

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_set_tx_notes(self):
        wallet = self._wallet
        # set tx notes
        uuid = TestUtils.get_random_string()
        txs = wallet.get_txs()
        assert len(txs) >= 3, "Test requires 3 or more wallet transactions run send tests"
        tx_hashes: list[str] = []
        tx_notes: list[str] = []
        i = 0
        while i < len(tx_hashes):
            tx_hash = txs[i].hash
            assert tx_hash is not None
            tx_hashes.append(tx_hash)
            tx_notes.append(f"{uuid}{i}")
            i += 1

        wallet.set_tx_notes(tx_hashes, tx_notes)

        # get tx notes
        tx_notes = wallet.get_tx_notes(tx_hashes)
        for tx_note in tx_notes:
            assert f"{uuid}{i}" == tx_note

        # TODO: test that get transaction has note

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_export_key_images(self):
        wallet = self._wallet
        images = wallet.export_key_images(True)
        assert len(images) > 0, "No signed key images in wallet"

        for image in images:
            assert isinstance(image, MoneroKeyImage)
            assert image.hex is not None and len(image.hex) > 0
            assert image.signature is not None and len(image.signature) > 0

        # wallet exports key images since last export by default
        images = wallet.export_key_images()
        images_all: list[MoneroKeyImage] = wallet.export_key_images(True)
        assert len(images_all) > len(images)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_new_key_images_from_last_import(self):
        wallet = self._wallet
        # get outputs hex
        outputs_hex = wallet.export_outputs()

        # import outputs hex
        if outputs_hex != "":
            num_imported = wallet.import_outputs(outputs_hex)
            assert num_imported >= 0

        # get and test new key images from last import
        images = wallet.get_new_key_images_from_last_import()
        if len(images) == 0:
            # TODO: these are already known to the wallet, so no new key images will be imported
            raise Exception("No new key images in last import")
        for image in images:
            assert image.hex is not None and len(image.hex) > 0
            assert image.signature is not None and len(image.signature) > 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_import_key_images(self):
        wallet = self._wallet
        images = wallet.export_key_images()
        assert len(images) > 0, "Wallet does not have any key images run send tests"
        result = wallet.import_key_images(images)
        assert result.height is not None and result.height > 0

        # determine if non-zero spent and unspent amounts are expected
        query = MoneroTxQuery()
        query.is_outgoing = True
        query.is_confirmed = True
        txs = wallet.get_txs(query)
        balance = wallet.get_balance()
        has_spent = len(txs) > 0
        has_unspent = balance > 0

        # test amounts
        TestUtils.test_unsigned_big_integer(result.spent_amount, has_spent)
        TestUtils.test_unsigned_big_integer(result.unspent_amount, has_unspent)

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_payment_uri(self):
        wallet = self._wallet
        # test with address and amount
        config1 = MoneroTxConfig()
        config1.address = wallet.get_address(0, 0)
        config1.amount = 0
        uri = wallet.get_payment_uri(config1)
        config2 = wallet.parse_payment_uri(uri)
        TestUtils.assert_equals(config1, config2)

        # test with subaddress and all fields
        config1.destinations[0].address = wallet.get_subaddress(0, 1).address
        config1.destinations[0].amount = 425000000000
        config1.recipient_name = "John Doe"
        config1.note = "OMZG XMR FTW"
        uri = wallet.get_payment_uri(config1)
        config2 = wallet.parse_payment_uri(uri)
        TestUtils.assert_equals(config1, config2)

        # test with undefined address
        address = config1.destinations[0].address
        config1.destinations[0].address = None
        try:
            wallet.get_payment_uri(config1)
            raise Exception("Should have thrown RPC exception with invalid parameters")
        except Exception as e:
            assert str(e).index("Cannot make URI from supplied parameters") >= 0

        config1.destinations[0].address = address

        # test with standalone payment id
        config1.payment_id = "03284e41c342f03603284e41c342f03603284e41c342f03603284e41c342f036"
        try:
            wallet.get_payment_uri(config1)
            raise Exception("Should have thrown RPC exception with invalid parameters")
        except Exception as e:
            assert str(e).index("Cannot make URI from supplied parameters") >= 0

    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_mining(self):
        daemon = self._daemon
        wallet = self._wallet

        status = daemon.get_mining_status()
        if status.is_active:
            wallet.stop_mining()
        wallet.start_mining(2, False, True)
        wallet.stop_mining()

    # endregion
