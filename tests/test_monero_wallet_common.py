from __future__ import annotations

import pytest
import logging

from configparser import ConfigParser
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from monero import (
    MoneroWallet, MoneroWalletRpc, MoneroDaemonRpc, MoneroWalletConfig,
    MoneroTxConfig, MoneroDestination, MoneroRpcConnection, MoneroError,
    MoneroKeyImage, MoneroTxQuery, MoneroUtils, MoneroBlock
)
from utils import (
    TestUtils, WalletEqualityUtils, MiningUtils,
    StringUtils, AssertUtils, TxUtils,
    TxContext, GenUtils, WalletUtils,
    SingleTxSender, BlockchainUtils
)

logger: logging.Logger = logging.getLogger("TestMoneroWalletCommon")


# Base class for common wallet tests
class BaseTestMoneroWallet(ABC):
    """Common wallet tests that every Monero wallet implementation should support"""
    CREATED_WALLET_KEYS_ERROR: str = "Wallet created from keys is not connected to authenticated daemon"

    _funded: bool = False
    """Indicates if test wallet is funded"""

    class Config:
        """Wallet test configuration"""
        seed: str = ""
        """Test wallet seed"""

        @classmethod
        def parse(cls, parser: ConfigParser) -> BaseTestMoneroWallet.Config:
            """
            Parse wallet test configuration

            :param ConfigParser parser: Configuration parser
            :return BaseTestMoneroWallet.Config: Wallet test configuration
            """
            section = "test_create_wallet_from_seed"
            if not parser.has_section(section):
                # raise exception if section not found
                raise Exception(f"Cannot find section '{section}' in test_monero_wallet_common.ini")
            config = cls()
            # parse configuration
            config.seed = parser.get(section, "seed")
            return config

    #region Private Methods

    def _setup_blockchain(self) -> None:
        BlockchainUtils.setup_blockchain(TestUtils.NETWORK_TYPE)
        self.fund_test_wallet()

    @classmethod
    def _get_test_daemon(cls) -> MoneroDaemonRpc:
        """
        Get the daemon to test.

        :return MoneroDaemonRpc: the daemon to test
        """
        return TestUtils.get_daemon_rpc()

    @abstractmethod
    def get_test_wallet(self) -> MoneroWallet:
        """
        Get the main wallet to test.

        :return MoneroWallet: the wallet to test
        """
        ...

    @abstractmethod
    def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
        """
        Open a test wallet with default configuration for each wallet type.

        :param Optional[MoneroWalletConfig] config: configures the wallet to open
        :return MoneroWallet: is the opened wallet
        """
        ...

    @abstractmethod
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWallet:
        """
        Create a test wallet with default configuration for each wallet type.

        :param MoneroWalletConfig config: configures the wallet to create
        :return MoneroWallet: is the created wallet
        """
        ...

    @abstractmethod
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        """
        Close a test wallet with customization for each wallet type.

        :param MoneroWallet wallet: the wallet to close
        :param bool save: whether or not to save the wallet
        """
        ...

    @abstractmethod
    def _get_seed_languages(self) -> list[str]:
        """
        Get the wallet's supported languages for the seed. This is an
        instance method for wallet rpc and a static utility for other wallets.

        :return list[str]: the wallet's supported languages
        """
        ...

    def _open_wallet_from_path(self, path: str, password: str | None) -> MoneroWallet:
        config = MoneroWalletConfig()
        config.path = path
        config.password = password

        return self._open_wallet(config)

    def get_daemon_rpc_uri(self) -> str:
        return TestUtils.DAEMON_RPC_URI

    def fund_test_wallet(self) -> None:
        if self._funded:
            return

        wallet = self.get_test_wallet()
        tx = MiningUtils.fund_wallet(wallet, 1)
        if tx is not None:
            BlockchainUtils.wait_for_blocks(11)
        self._funded = True

    @classmethod
    def is_random_wallet_config(cls, config: Optional[MoneroWalletConfig]) -> bool:
        assert config is not None
        return config.seed is None and config.primary_address is None

    #endregion

    #region Fixtures

    # Test wallet configuration
    @pytest.fixture(scope="class")
    def test_config(self) -> BaseTestMoneroWallet.Config:
        """Test configuration"""
        parser = ConfigParser()
        parser.read('tests/config/test_monero_wallet_common.ini')
        return BaseTestMoneroWallet.Config.parse(parser)

    # Test daemon fixture
    @pytest.fixture(scope="class")
    def daemon(self) -> MoneroDaemonRpc:
        """Test rpc daemon instance"""
        return TestUtils.get_daemon_rpc()

    # Test wallet fixture
    @pytest.fixture(scope="class")
    def wallet(self) -> MoneroWallet:
        """Test wallet instance"""
        pytest.skip("No wallet test instance setup")

    # Before all tests
    @pytest.fixture(scope="class", autouse=True)
    def before_all(self) -> None:
        """Executed once before all tests"""
        self._setup_blockchain()

    # Setup and teardown of each test
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        self.before_each(request)
        yield
        self.after_each(request)

    # Before each test
    def before_each(self, request: pytest.FixtureRequest) -> None:
        """
        Executed before each test

        :param pytest.FixtureRequest: Request fixture
        """
        logger.info(f"Before {request.node.name}") # type: ignore

    # After each test
    def after_each(self, request: pytest.FixtureRequest) -> None:
        """
        Executed after each test

        :param pytest.FixtureRequest: Request fixture
        """
        logger.info(f"After {request.node.name}") # type: ignore

    #endregion

    #region Tests

    # Can get the daemon's max peer height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        height = wallet.get_daemon_max_peer_height()
        assert height > 0

    # Can get the daemon's height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_daemon(self, wallet: MoneroWallet) -> None:
        assert wallet.is_connected_to_daemon(), "Wallet is not connected to daemon"
        daemon_height = wallet.get_daemon_height()
        assert daemon_height > 0

    # Can create a random wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_random(self) -> None:
        """
        Can create a random wallet.
        """
        config = MoneroWalletConfig()
        wallet = self._create_wallet(config)
        path = wallet.get_path()

        try:
            MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
            MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
            MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
            MoneroUtils.validate_mnemonic(wallet.get_seed())
            if not isinstance(wallet, MoneroWalletRpc):
                # TODO monero-wallet-rpc: get seed language
                AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
        finally:
            self._close_wallet(wallet)

        # attempt to create wallet at same path
        try:
            config = MoneroWalletConfig()
            config.path = path
            self._create_wallet(config)
        except Exception as e:
            AssertUtils.assert_equals("Wallet already exists: " + path, str(e))

        # attempt to create wallet with unknown language
        try:
            config = MoneroWalletConfig()
            config.language = "english"
            self._create_wallet(config)
            raise Exception("Should have thrown error")
        except Exception as e:
            AssertUtils.assert_equals("Unknown language: english", str(e))

    # Can create a wallet from a seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed(self, wallet: MoneroWallet, test_config: BaseTestMoneroWallet.Config) -> None:
        # save for comparison
        primary_address = wallet.get_primary_address()
        private_view_key = wallet.get_private_view_key()
        private_spend_key = wallet.get_private_spend_key()

        # recreate test wallet from seed
        config = MoneroWalletConfig()
        config.seed = TestUtils.SEED
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT

        w: MoneroWallet = self._create_wallet(config)
        path = w.get_path()
        try:
            AssertUtils.assert_equals(primary_address, w.get_primary_address())
            AssertUtils.assert_equals(private_view_key, w.get_private_view_key())
            AssertUtils.assert_equals(private_spend_key, w.get_private_spend_key())
            AssertUtils.assert_equals(TestUtils.SEED, w.get_seed())
            if not isinstance(w, MoneroWalletRpc):
                AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, w.get_seed_language())
        finally:
            self._close_wallet(w)

        # attempt to create wallet with two missing words
        try:
            config = MoneroWalletConfig()
            config.seed = test_config.seed
            config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
            self._create_wallet(config)
        except Exception as e:
            AssertUtils.assert_equals("Invalid mnemonic", str(e))

        # attempt to create wallet at same path
        try:
            config = MoneroWalletConfig()
            config.path = path
            self._create_wallet(config)
            raise Exception("Should have thrown error")
        except Exception as e:
            AssertUtils.assert_equals("Wallet already exists: " + path, str(e))

    # Can create a wallet from a seed with offset
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed_with_offset(self) -> None:
        # create test wallet with offset
        config = MoneroWalletConfig()
        config.seed = TestUtils.SEED
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
        config.seed_offset = "my secret offset!"
        wallet: MoneroWallet = self._create_wallet(config)
        try:
            MoneroUtils.validate_mnemonic(wallet.get_seed())
            AssertUtils.assert_not_equals(TestUtils.SEED, wallet.get_seed())
            MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
            AssertUtils.assert_not_equals(TestUtils.ADDRESS, wallet.get_primary_address())
            if not isinstance(wallet, MoneroWalletRpc):
                # TODO monero-wallet-rpc: support
                AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
        finally:
            self._close_wallet(wallet)

    # Can create a wallet from keys
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
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
        config.restore_height = daemon.get_height()
        w: MoneroWallet = self._create_wallet(config)
        path = w.get_path()

        try:
            AssertUtils.assert_equals(primary_address, w.get_primary_address())
            AssertUtils.assert_equals(private_view_key, w.get_private_view_key())
            AssertUtils.assert_equals(private_spend_key, w.get_private_spend_key())
            if not w.is_connected_to_daemon():
                # TODO monero-project: keys wallets not connected
                logger.warning(f"WARNING: {self.CREATED_WALLET_KEYS_ERROR}")
            AssertUtils.assert_true(w.is_connected_to_daemon(), self.CREATED_WALLET_KEYS_ERROR)
            if not isinstance(w, MoneroWalletRpc):
                # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                MoneroUtils.validate_mnemonic(w.get_seed())
                AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, w.get_seed_language())
        finally:
            self._close_wallet(w)

        # recreate test wallet from spend key
        if not isinstance(w, MoneroWalletRpc): # TODO monero-wallet-rpc: cannot create wallet from spend key?
            config = MoneroWalletConfig()
            config.private_spend_key = private_spend_key
            config.restore_height = daemon.get_height()
            w = self._create_wallet(config)

            try:
                AssertUtils.assert_equals(primary_address, w.get_primary_address())
                AssertUtils.assert_equals(private_view_key, w.get_private_view_key())
                AssertUtils.assert_equals(private_spend_key, w.get_private_spend_key())
                if not w.is_connected_to_daemon():
                    # TODO monero-project: keys wallets not connected
                    logger.warning(f"{self.CREATED_WALLET_KEYS_ERROR}")
                AssertUtils.assert_true(w.is_connected_to_daemon(), self.CREATED_WALLET_KEYS_ERROR)
                if not isinstance(w, MoneroWalletRpc):
                    # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
                    MoneroUtils.validate_mnemonic(w.get_seed())
                    AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, w.get_seed_language())
            finally:
                self._close_wallet(w)

        # attempt to create wallet at same path
        try:
            config = MoneroWalletConfig()
            config.path = path
            self._create_wallet(config)
            raise Exception("Should have thrown error")
        except Exception as e:
            AssertUtils.assert_equals("Wallet already exists: " + path, str(e))

    # Can create wallets with subaddress lookahead
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
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
            dest.amount = TxUtils.MAX_FEE
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
        version = wallet.get_version()
        assert version.number is not None
        assert version.number > 0
        assert version.is_release is not None

    # Can get the wallet's path
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_path(self) -> None:
        # create random wallet
        config = MoneroWalletConfig()
        wallet = self._create_wallet(config)

        # set a random attribute
        #String uuid = UUID.randomUUID().toString()
        uuid = StringUtils.get_random_string()
        wallet.set_attribute("uuid", uuid)

        # record the wallet's path then save and close
        path = wallet.get_path()
        self._close_wallet(wallet, True)

        # re-open the wallet using its path
        wallet = self._open_wallet_from_path(path, None)

        # test the attribute
        AssertUtils.assert_equals(uuid, wallet.get_attribute("uuid"))
        self._close_wallet(wallet)

    # Can set the daemon connection
    def test_set_daemon_connection(self) -> None:
        # create random wallet with default daemon connection
        config = MoneroWalletConfig()
        wallet = self._create_wallet(config)
        daemon_rpc_uri = self.get_daemon_rpc_uri()
        connection = MoneroRpcConnection(
            daemon_rpc_uri, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        AssertUtils.assert_true(wallet.is_connected_to_daemon()) # uses default localhost connection

        # set empty server uri
        wallet.set_daemon_connection("")
        AssertUtils.assert_equals(None, wallet.get_daemon_connection())
        AssertUtils.assert_false(wallet.is_connected_to_daemon())

        # set offline server uri
        wallet.set_daemon_connection(TestUtils.OFFLINE_SERVER_URI)
        connection = MoneroRpcConnection(TestUtils.OFFLINE_SERVER_URI, "", "")
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        AssertUtils.assert_false(wallet.is_connected_to_daemon())

        # set daemon with wrong credentials
        wallet.set_daemon_connection(daemon_rpc_uri, "wronguser", "wrongpass")
        connection = MoneroRpcConnection(daemon_rpc_uri, "wronguser", "wrongpass")
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        if "" == TestUtils.DAEMON_RPC_USERNAME:
            # TODO: monerod without authentication works with bad credentials?
            AssertUtils.assert_true(wallet.is_connected_to_daemon())
        else:
            AssertUtils.assert_false(wallet.is_connected_to_daemon())

        # set daemon with authentication
        wallet.set_daemon_connection(
            daemon_rpc_uri, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        connection = MoneroRpcConnection(
            daemon_rpc_uri, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        AssertUtils.assert_true(wallet.is_connected_to_daemon())

        # nullify daemon connection
        wallet.set_daemon_connection(None)
        AssertUtils.assert_equals(None, wallet.get_daemon_connection())
        wallet.set_daemon_connection(daemon_rpc_uri)
        connection = MoneroRpcConnection(daemon_rpc_uri)
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        wallet.set_daemon_connection(None)
        AssertUtils.assert_equals(None, wallet.get_daemon_connection())

        # set daemon uri to non-daemon
        if not TestUtils.IN_CONTAINER: # TODO sometimes this fails in container...
            wallet.set_daemon_connection("www.getmonero.org")
            connection = MoneroRpcConnection("www.getmonero.org")
            AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
            AssertUtils.assert_false(wallet.is_connected_to_daemon())

        # set daemon to invalid uri
        wallet.set_daemon_connection("abc123")
        AssertUtils.assert_false(wallet.is_connected_to_daemon())

        # attempt to sync
        try:
            wallet.sync()
            raise Exception("Exception expected")
        except Exception as e:
            AssertUtils.assert_equals("Wallet is not connected to daemon", str(e))
        finally:
            self._close_wallet(wallet)

    # Can get the seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_seed(self, wallet: MoneroWallet) -> None:
        seed = wallet.get_seed()
        MoneroUtils.validate_mnemonic(seed)
        AssertUtils.assert_equals(TestUtils.SEED, seed)

    # Can get the language of the seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_seed_language(self, wallet: MoneroWallet) -> None:
        language = wallet.get_seed_language()
        AssertUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, language)

    # Can get a list of supported languages for the seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_seed_languages(self) -> None:
        languages = self._get_seed_languages()
        assert len(languages) > 0
        for language in languages:
            assert len(language) > 0

    # Can get the private view key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_private_view_key(self, wallet: MoneroWallet) -> None:
        private_view_key = wallet.get_private_view_key()
        MoneroUtils.validate_private_view_key(private_view_key)

    # Can get the private spend key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_private_spend_key(self, wallet: MoneroWallet) -> None:
        private_spend_key = wallet.get_private_spend_key()
        MoneroUtils.validate_private_spend_key(private_spend_key)

    # Can get the public view key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_public_view_key(self, wallet: MoneroWallet) -> None:
        public_view_key = wallet.get_public_view_key()
        MoneroUtils.validate_private_spend_key(public_view_key)

    # Can get the public spend key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_public_spend_key(self, wallet: MoneroWallet) -> None:
        public_spend_key = wallet.get_public_spend_key()
        MoneroUtils.validate_private_spend_key(public_spend_key)

    # Can get the primary address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_primary_address(self, wallet: MoneroWallet) -> None:
        primary_address = wallet.get_primary_address()
        MoneroUtils.validate_address(primary_address, TestUtils.NETWORK_TYPE)
        AssertUtils.assert_equals(wallet.get_address(0, 0), primary_address)

    # Can get the address of a subaddress at a specified account and subaddress index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_address(self, wallet: MoneroWallet) -> None:
        AssertUtils.assert_equals(wallet.get_primary_address(), (wallet.get_address(0, 0)))
        for account in wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert account.index is not None
                assert subaddress.index is not None
                AssertUtils.assert_equals(subaddress.address, wallet.get_address(account.index, subaddress.index))

    # Can get addresses out of range of used accounts and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts(True)
        account_idx = len(accounts) - 1
        subaddress_idx = len(accounts[account_idx].subaddresses)
        address = wallet.get_address(account_idx, subaddress_idx)
        AssertUtils.assert_not_none(address)
        AssertUtils.assert_true(len(address) > 0)

    # Can get the account and subaddress indices of an address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_address_indices(self, wallet: MoneroWallet) -> None:
        # get last subaddress to test
        accounts = wallet.get_accounts(True)
        account_idx = len(accounts) - 1
        subaddress_idx = len(accounts[account_idx].subaddresses) - 1
        address = wallet.get_address(account_idx, subaddress_idx)
        AssertUtils.assert_not_none(address)

        # get address index
        subaddress = wallet.get_address_index(address)
        AssertUtils.assert_equals(account_idx, subaddress.account_index)
        AssertUtils.assert_equals(subaddress_idx, subaddress.index)

        # test valid but unfound address
        non_wallet_address = TestUtils.get_external_wallet_address()
        try:
            wallet.get_address_index(non_wallet_address)
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_equals("Address doesn't belong to the wallet", str(e))

        # test invalid address
        try:
            wallet.get_address_index("this is definitely not an address")
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_equals("Invalid address", str(e))

    # Can decode an integrated address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_decode_integrated_address(self, wallet: MoneroWallet) -> None:
        integrated_address = wallet.get_integrated_address('', "03284e41c342f036")
        decoded_address = wallet.decode_integrated_address(integrated_address.integrated_address)
        AssertUtils.assert_equals(integrated_address, decoded_address)

        # decode invalid address
        try:
            wallet.decode_integrated_address("bad address")
            raise Exception("Should have failed decoding bad address")
        except Exception as e:
            AssertUtils.assert_equals("Invalid address", str(e))

    # Can sync (without progress)
    # TODO test syncing from start height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sync_without_progress(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        num_blocks = 100
        chain_height = daemon.get_height()
        AssertUtils.assert_true(chain_height >= num_blocks)
        result = wallet.sync(chain_height - num_blocks) # sync end of chain
        AssertUtils.assert_true(result.num_blocks_fetched >= 0)
        AssertUtils.assert_not_none(result.received_money)

    # Is equal to a ground truth wallet accoring to on-chain data
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_wallet_equality_ground_truth(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool([wallet])
        wallet_gt = TestUtils.create_wallet_ground_truth(
            TestUtils.NETWORK_TYPE, TestUtils.SEED, None, TestUtils.FIRST_RECEIVE_HEIGHT
        )
        try:
            WalletEqualityUtils.test_wallet_equality_on_chain(wallet_gt, wallet)
        finally:
            wallet_gt.close()

    # Can get the current height that the wallet is synchronized to
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height(self, wallet: MoneroWallet) -> None:
        height = wallet.get_height()
        assert height >= 0

    # Can get a blockchain height by date
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        # collect dates to test starting 100 days ago
        day_ms = 24 * 60 * 60 * 1000
        # TODO monero-project: today's date can throw exception as "in future" so we test up to yesterday
        yesterday = GenUtils.current_timestamp() - day_ms
        dates: list[datetime] = []
        i = 99

        while i >= 0:
            # subtract i days
            dates.append(datetime.fromtimestamp((yesterday - day_ms * i) / 1000))
            i -= 1

        # test heights by date
        last_height: Optional[int] = None
        for date in dates:
            height = wallet.get_height_by_date(date.year + 1900, date.month + 1, date.day)
            assert (height >= 0)
            if last_height is not None:
                assert (height >= last_height)
            last_height = height

        assert last_height is not None
        assert (last_height >= 0)
        height = wallet.get_height()
        assert (height >= 0)

        # test future date
        try:
            tomorrow = datetime.fromtimestamp((yesterday + day_ms * 2) / 1000)
            wallet.get_height_by_date(tomorrow.year + 1900, tomorrow.month + 1, tomorrow.day)
            raise Exception("Expected exception on future date")
        except MoneroError as err:
            assert "specified date is in the future" == str(err)

    # Can get the locked and unlocked balances of the wallet, accounts and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_all_balances(self, wallet: MoneroWallet) -> None:
        # fetch accounts with all info as reference
        accounts = wallet.get_accounts(True)
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

        GenUtils.test_unsigned_big_integer(accounts_balance)
        GenUtils.test_unsigned_big_integer(accounts_unlocked_balance)
        assert wallet.get_balance() == accounts_balance
        assert wallet.get_unlocked_balance() == accounts_unlocked_balance

    # Can get accounts without subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_accounts_without_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)
            assert len(account.subaddresses) == 0

    # Can get accounts with subaddress
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_accounts_with_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts(True)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)
            assert len(account.subaddresses) > 0

    # Can get an account at a specified index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_account(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)

            # test without subaddresses
            assert account.index is not None
            retrieved = wallet.get_account(account.index)
            assert len(retrieved.subaddresses) == 0

            # test with subaddresses
            retrieved = wallet.get_account(account.index, True)
            assert len(retrieved.subaddresses) > 0

    # Can create a new account without a label
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_account_without_label(self, wallet: MoneroWallet) -> None:
        accounts_before = wallet.get_accounts()
        created_account = wallet.create_account()
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)
        assert len(accounts_before) == len(wallet.get_accounts()) - 1

    # Can create a new account with a label
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_account_with_label(self, wallet: MoneroWallet) -> None:
        # create account with label
        accounts_before = wallet.get_accounts()
        label = StringUtils.get_random_string()
        created_account = wallet.create_account(label)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)
        assert created_account.index is not None
        assert len(accounts_before) == len(wallet.get_accounts()) - 1
        assert label == wallet.get_subaddress(created_account.index, 0).label

        # fetch and test account
        created_account = wallet.get_account(created_account.index)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)

        # create account with same label
        created_account = wallet.create_account(label)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)
        assert len(accounts_before) == len(wallet.get_accounts()) - 2
        assert created_account.index is not None
        assert label == wallet.get_subaddress(created_account.index, 0).label

        # fetch and test account
        created_account = wallet.get_account(created_account.index)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)

    # Can set account labels
    def test_set_account_label(self, wallet: MoneroWallet) -> None:
        # create account
        if len(wallet.get_accounts()) < 2:
            wallet.create_account()

        # set account label
        label = StringUtils.get_random_string()
        wallet.set_account_label(1, label)
        assert label == wallet.get_subaddress(1, 0).label

    # Can get subaddresses at a aspecified account index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                WalletUtils.test_subaddress(subaddress)
                assert account.index == subaddress.account_index

    # Can get subaddresses at a specified account index and subaddress indices
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddresses_by_indices(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:

            # get subaddresses
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0

            # remove a subaddress for query if possible
            if len(subaddresses) > 1:
                # TODO implement remove (needs operator == overload)
                #subaddresses.remove(subaddresses[0])
                pass

            # get subaddress indices
            subaddress_indices: list[int] = []
            for subaddress in subaddresses:
                assert subaddress.index is not None
                subaddress_indices.append(subaddress.index)
            assert len(subaddress_indices) > 0

            # fetch subaddresses by indices
            fetched_subaddresses = wallet.get_subaddresses(account.index, subaddress_indices)

            # original subaddresses (minus one removed if applicable) is equal to fetched subaddresses
            AssertUtils.assert_subaddresses_equal(subaddresses, fetched_subaddresses)

    # Can get subaddress at a specified account index and subaddress index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_by_index(self, wallet: MoneroWallet) -> None:
        accounts = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                assert subaddress.index is not None
                WalletUtils.test_subaddress(subaddress)
                AssertUtils.assert_subaddress_equal(subaddress, wallet.get_subaddress(account.index, subaddress.index))
                # test plural call with single subaddr number
                AssertUtils.assert_subaddress_equal(
                    subaddress, wallet.get_subaddresses(account.index, [subaddress.index])[0]
                )

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_subaddress(self, wallet: MoneroWallet) -> None:
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
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses_new) - 1 == len(subaddresses)
            AssertUtils.assert_subaddress_equal(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = wallet.get_subaddresses(account_idx)
            uuid = StringUtils.get_random_string()
            subaddress = wallet.create_subaddress(account_idx, uuid)
            assert (uuid == subaddress.label)
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses) == len(subaddresses_new) - 1
            AssertUtils.assert_subaddress_equal(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            account_idx += 1

    # Can set subaddress labels
    def test_set_subaddress_label(self, wallet: MoneroWallet) -> None:
        # create subaddresses
        while len(wallet.get_subaddresses(0)) < 3:
            wallet.create_subaddress(0)

        # set subaddress labels
        subaddress_idx = 0
        while subaddress_idx < len(wallet.get_subaddresses(0)):
            label = StringUtils.get_random_string()
            wallet.set_subaddress_label(0, subaddress_idx, label)
            assert label == wallet.get_subaddress(0, subaddress_idx).label
            subaddress_idx += 1

    #region Txs Tests

    def _test_send_to_single(self, wallet: MoneroWallet, can_split: bool, relay: Optional[bool] = None, payment_id: Optional[str] = None) -> None:
        config = MoneroTxConfig()
        config.can_split = can_split
        config.relay = relay
        config.payment_id = payment_id
        sender = SingleTxSender(wallet, config)
        sender.send()

    # Can send to an address in a single transaction
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send(self, wallet: MoneroWallet) -> None:
        self._test_send_to_single(wallet, False)

    # Can send to an address in a single transaction with a payment id
    # NOTE this test will be invalid when payment hashes are fully removed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_with_payment_id(self, wallet: MoneroWallet) -> None:
        integrated_address = wallet.get_integrated_address()
        assert integrated_address.payment_id is not None
        payment_id = integrated_address.payment_id
        try:
            self._test_send_to_single(wallet, False, None, f"{payment_id}{payment_id}{payment_id}")
            raise Exception("Should have thrown")
        except Exception as e:
            msg = "Standalone payment IDs are obsolete. Use subaddresses or integrated addresses instead"
            assert msg == str(e)

    # Can send to an address with split transactions
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_split(self, wallet: MoneroWallet) -> None:
        self._test_send_to_single(wallet, True, True)

    # Can create then relay a transaction to send to a single address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_then_relay(self, wallet: MoneroWallet) -> None:
        self._test_send_to_single(wallet, True, False)

    # Can create then relay split transactions to send to a single address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_then_relay_split(self, wallet: MoneroWallet) -> None:
        self._test_send_to_single(wallet, True)

    # Can get transactions in the wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_wallet(self, wallet: MoneroWallet) -> None:
        #non_default_incoming: bool = False
        txs = TxUtils.get_and_test_txs(wallet, None, None, True, TestUtils.REGTEST)
        assert len(txs) > 0, "Wallet has no txs to test"
        # TODO make consistent with test funded wallet
        # assert TestUtils.FIRST_RECEIVE_HEIGHT == txs[0].get_height(), "First tx's restore height must match the restore height in TestUtils"

        # build test context
        ctx = TxContext()
        ctx.wallet = wallet

        # test each transaction
        block_per_height: dict[int, MoneroBlock] = {}
        for i, tx in enumerate(txs):
            TxUtils.test_tx_wallet(tx, ctx)

            # test merging equivalent txs
            it = txs[i] # is the same as tx
            copy1 = it.copy()
            copy2 = it.copy()

            if copy1.is_confirmed:
                assert it.block is not None
                copy1.block = it.block.copy()
                copy1.block.txs = [copy1]

            if copy2.is_confirmed:
                assert it.block is not None
                copy2.block = it.block.copy()
                copy2.block.txs = [copy2]

            copy1.merge(copy2)
            TxUtils.test_tx_wallet(copy1, ctx)

            # find non-default incoming
            for transfer in it.incoming_transfers:
                assert transfer.account_index is not None
                assert transfer.subaddress_index is not None
                #if transfer.account_index != 0 and transfer.subaddress_index != 0:
                #    non_default_incoming = True

            # ensure unique block reference per height
            if it.is_confirmed:
                h = it.get_height()
                assert h is not None
                block = block_per_height.get(h)
                if block is None:
                    assert it.block is not None
                    block_per_height[i] = it.block
                else:
                    AssertUtils.assert_equals(block, it.block)
                    assert block == it.block, "Block references for same height must be same"

        # ensure non-default account and subaddress testes
        # TODO enable this after setting send-to-multiple order
        #assert non_default_incoming, "No incoming transfers found to non-default account and subaddress; run send-to-multiple tests first"

    # Can get and set a transaction note
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        txs = TxUtils.get_random_transactions(wallet, None, 1, 5)

        # set notes
        uuid = StringUtils.get_random_string()
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

    # Can get and set multiple transaction notes
    # TODO why does getting cached txs take 2 seconds when should already be cached?
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_tx_notes(self, wallet: MoneroWallet) -> None:
        # set tx notes
        uuid = StringUtils.get_random_string()
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

    #endregion

    # Can export signed key images
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_export_key_images(self, wallet: MoneroWallet) -> None:
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

    # Can get new key images from the last import
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
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

    # Can import key images
    # TODO monero-project: importing key images can cause erasure of incoming transfers per wallet2.cpp:11957
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
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
        GenUtils.test_unsigned_big_integer(result.spent_amount, has_spent)
        GenUtils.test_unsigned_big_integer(result.unspent_amount, has_unspent)

    # Can convert between a tx config and payment URI
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_payment_uri(self, wallet: MoneroWallet) -> None:
        # test with address and amount
        config1 = MoneroTxConfig()
        dest = MoneroDestination()
        dest.address = wallet.get_address(0, 0)
        dest.amount = 0
        config1.destinations.append(dest)
        uri = wallet.get_payment_uri(config1)
        config2 = wallet.parse_payment_uri(uri)
        AssertUtils.assert_equals(config1, config2)

        # test with subaddress and all fields
        subaddress = wallet.get_subaddress(0, 1)
        assert subaddress.address is not None
        config1.destinations[0].address = subaddress.address
        config1.destinations[0].amount = 425000000000
        config1.recipient_name = "John Doe"
        config1.note = "OMZG XMR FTW"
        uri = wallet.get_payment_uri(config1)
        config2 = wallet.parse_payment_uri(uri)
        AssertUtils.assert_equals(config1, config2)

        # test with undefined address
        address = config1.destinations[0].address
        config1.destinations[0].address = None
        try:
            wallet.get_payment_uri(config1)
            raise Exception("Should have thrown RPC exception with invalid parameters")
        except Exception as e:
            assert "Cannot make URI from supplied parameters" in str(e), str(e)

        config1.destinations[0].address = address

        # test with standalone payment id
        config1.payment_id = "03284e41c342f03603284e41c342f03603284e41c342f03603284e41c342f036"
        try:
            wallet.get_payment_uri(config1)
            raise Exception("Should have thrown RPC exception with invalid parameters")
        except Exception as e:
            assert "Cannot make URI from supplied parameters" in str(e), str(e)

    # Can start and stop mining
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        status = daemon.get_mining_status()
        if status.is_active:
            wallet.stop_mining()
        wallet.start_mining(2, False, True)
        wallet.stop_mining()

    # Can change the wallet password
    def test_change_password(self) -> None:
        # create random wallet
        config = MoneroWalletConfig()
        config.password = TestUtils.WALLET_PASSWORD
        wallet = self._create_wallet(config)
        path: str = wallet.get_path()

        # change password
        new_password: str = ""
        wallet.change_password(TestUtils.WALLET_PASSWORD, new_password)

        # close wallet without saving
        self._close_wallet(wallet)

        # old password does not work (password change is auto saved)
        try:
            config = MoneroWalletConfig()
            config.path = path
            config.password = TestUtils.WALLET_PASSWORD
            self._open_wallet(config)
            raise Exception("Should have thrown")
        except Exception as e:
            # TODO: different errors from rpc and wallet2
            e_str = str(e).lower()
            assert "failed to open wallet" in e_str or "invalid password" in e_str, e_str

        # open wallet with new password
        config = MoneroWalletConfig()
        config.path = path
        config.password = new_password
        wallet = self._open_wallet(config)

        # change password with incorrect password
        try:
            wallet.change_password("badpassword", new_password)
            raise Exception("Should have throw")
        except Exception as e:
            e_str = str(e)
            assert "Invalid original password." == e_str, e_str

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
        config = MoneroWalletConfig()
        config.password = password
        wallet = self._create_wallet(config)
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

    #endregion
