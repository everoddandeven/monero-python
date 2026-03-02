from __future__ import annotations

import pytest
import logging

from random import shuffle
from configparser import ConfigParser
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from monero import (
    MoneroWallet, MoneroWalletRpc, MoneroDaemonRpc, MoneroWalletConfig,
    MoneroTxConfig, MoneroDestination, MoneroRpcConnection, MoneroError,
    MoneroKeyImage, MoneroTxQuery, MoneroUtils, MoneroBlock, MoneroTransferQuery,
    MoneroOutputQuery, MoneroTransfer, MoneroIncomingTransfer, MoneroOutgoingTransfer,
    MoneroTxWallet, MoneroOutputWallet, MoneroTx, MoneroAccount, MoneroSubaddress,
    MoneroMessageSignatureType, MoneroTxPriority
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

    # Setup and teardown of test class
    @pytest.fixture(scope="class", autouse=True)
    def global_setup_and_teardown(self):
        """Executed once before all tests"""
        self.before_all()
        yield
        self.after_all()

    # Setup and teardown of each test
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        self.before_each(request)
        yield
        self.after_each(request)

    # Before all tests
    def before_all(self) -> None:
        """Executed once before all tests"""
        logger.info(f"Setup test class {type(self).__name__}")
        self._setup_blockchain()

    # After all tests
    def after_all(self) -> None:
        """Executed once after all tests"""
        logger.info(f"Teardown test class {type(self).__name__}")
        daemon: MoneroDaemonRpc | None = self._get_test_daemon()
        try:
            daemon.stop_mining()
        except Exception as e:
            logger.debug(str(e))

        # close wallet
        wallet = self.get_test_wallet()
        wallet.close(True)

    # Before each test
    def before_each(self, request: pytest.FixtureRequest) -> None:
        """
        Executed before each test

        :param pytest.FixtureRequest: Request fixture
        """
        logger.info(f"Before {request.node.name}") # type: ignore

        daemon = self._get_test_daemon()
        wallet = self.get_test_wallet()
        status = daemon.get_mining_status()

        if status.is_active is True:
            wallet.stop_mining()

    # After each test
    def after_each(self, request: pytest.FixtureRequest) -> None:
        """
        Executed after each test

        :param pytest.FixtureRequest: Request fixture
        """
        logger.info(f"After {request.node.name}") # type: ignore

        daemon = self._get_test_daemon()
        status = daemon.get_mining_status()

        if status.is_active is True:
            logger.warning(f"Mining is active after test {request.node.name}") # type: ignore


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

    # Can get transactions by hash
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_by_hash(self, wallet: MoneroWallet) -> None:
        # max number of txs to test
        max_num_txs: int = 10

        # fetch all txs for testing
        txs = wallet.get_txs()
        num_txs = len(txs)
        assert num_txs > 1, f"Test requires at least 2 txs to fetch by hash, got {num_txs}"

        # randomly pick a few for fetching by hash
        shuffle(txs)
        txs = txs[0:min(max_num_txs, num_txs)]

        # test fetching by hash
        tx_hash = txs[0].hash
        assert tx_hash is not None
        fetched_tx = wallet.get_tx(tx_hash)
        assert fetched_tx is not None
        assert tx_hash == fetched_tx.hash
        TxUtils.test_tx_wallet(fetched_tx)

        # test fetching by hashes
        tx_id1 = txs[0].hash
        tx_id2 = txs[1].hash
        assert tx_id1 is not None
        assert tx_id2 is not None
        fetched_txs = wallet.get_txs([tx_id1, tx_id2])
        num_fetched_txs = len(fetched_txs)
        assert num_fetched_txs == 2, f"Expected 2 txs, got {num_fetched_txs}"

        # test fetching by hashes as collection
        tx_hashes: list[str] = []
        for tx in txs:
            assert tx.hash is not None
            tx_hashes.append(tx.hash)

        fetched_txs = wallet.get_txs(tx_hashes)
        assert len(txs) == len(fetched_txs)
        for i, tx in enumerate(txs):
            fetched_tx = fetched_txs[i]
            assert tx.hash == fetched_tx.hash
            TxUtils.test_tx_wallet(fetched_tx)

        # test fetching with missing tx hashes
        missing_hash: str = "d01ede9cde813b2a693069b640c4b99c5adbdb49fbbd8da2c16c8087d0c3e320"
        tx_hashes.append(missing_hash)
        fetched_txs = wallet.get_txs(tx_hashes)
        assert len(txs) == len(fetched_txs)
        for i, tx in enumerate(txs):
            fetched_tx = fetched_txs[i]
            assert tx.hash == fetched_tx.hash
            TxUtils.test_tx_wallet(fetched_tx)

    # Can get transactions with additional configuration
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_with_query(self, wallet: MoneroWallet) -> None:
        # get random transactions for testing
        random_txs = TxUtils.get_random_transactions(wallet, None, 3, 5)
        for random_tx in random_txs:
            TxUtils.test_tx_wallet(random_tx, None)

        # get transactions by hash
        tx_hashes: list[str] = []
        for random_tx in random_txs:
            assert random_tx.hash is not None
            tx_hashes.append(random_tx.hash)
            query = MoneroTxQuery()
            query.hash = random_tx.hash
            txs = TxUtils.get_and_test_txs(wallet, query, None, True, TestUtils.REGTEST)
            assert len(txs) == 1
            # txs change with chain so check mergeability
            merged = txs[0]
            merged.merge(random_tx.copy())
            TxUtils.test_tx_wallet(merged)

        # get transactions by hashes
        query = MoneroTxQuery()
        query.hashes = tx_hashes
        txs = TxUtils.get_and_test_txs(wallet, query, None, None, TestUtils.REGTEST)
        assert len(txs) == len(random_txs)
        for tx in txs:
            assert tx.hash in tx_hashes

        # get transactions with an outgoing transfer
        ctx: TxContext = TxContext()
        ctx.has_outgoing_transfer = True
        query = MoneroTxQuery()
        query.is_outgoing = True
        txs = TxUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_outgoing is True
            assert tx.outgoing_transfer is not None
            TxUtils.test_transfer(tx.outgoing_transfer, None)

        # get transactions without an outgoing transfer
        ctx.has_outgoing_transfer = False
        query = MoneroTxQuery()
        query.is_outgoing = False
        txs = TxUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.outgoing_transfer is None

        # get transactions with incoming transfers
        ctx = TxContext()
        ctx.has_incoming_transfers = True
        query = MoneroTxQuery()
        query.is_incoming = True
        txs = TxUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_incoming is True
            assert len(tx.incoming_transfers) > 0
            for transfer in tx.incoming_transfers:
                TxUtils.test_transfer(transfer, None)

        # get transactions associated with an account
        account_idx: int = 1
        query = MoneroTxQuery()
        query.transfer_query = MoneroTransferQuery()
        query.transfer_query.account_index = account_idx
        txs = wallet.get_txs(query)

        for tx in txs:
            found: bool = False
            if tx.is_outgoing:
                assert tx.outgoing_transfer is not None
                if tx.outgoing_transfer.account_index == account_idx:
                    found = True
            elif len(tx.incoming_transfers) > 0:
                for transfer in tx.incoming_transfers:
                    if transfer.account_index == account_idx:
                        found = True
                        break

            assert found, f"Transaction is not associated with account {account_idx}: \n{tx.serialize()}"

        # get txs with manually built query that are confirmed and have an outgoing transfer from account 0
        ctx = TxContext()
        ctx.has_outgoing_transfer = True
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.transfer_query = MoneroTransferQuery()
        tx_query.transfer_query.account_index = 0
        tx_query.transfer_query.outgoing = True
        txs = TxUtils.get_and_test_txs(wallet, tx_query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            if tx.is_confirmed is not True:
                logger.warning(f"{tx.serialize()}")
            assert tx.is_confirmed is True
            assert tx.is_outgoing is True
            assert tx.outgoing_transfer is not None
            assert tx.outgoing_transfer.account_index == 0

        # get txs with outgoing transfers that have destinations to account 1
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.transfer_query = MoneroTransferQuery()
        tx_query.transfer_query.account_index = 0
        tx_query.transfer_query.has_destinations = True

        txs = TxUtils.get_and_test_txs(wallet, tx_query, None, None, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_outgoing is True
            assert tx.outgoing_transfer is not None
            assert len(tx.outgoing_transfer.destinations) > 0

        # include outputs with transactions
        ctx = TxContext()
        ctx.include_outputs = True
        tx_query = MoneroTxQuery()
        tx_query.include_outputs = True
        txs = TxUtils.get_and_test_txs(wallet, tx_query, ctx, True, TestUtils.REGTEST)
        found: bool = False
        for tx in txs:
            if len(tx.outputs) > 0:
                found = True
            else:
                # TODO: monero-wallet-rpc: return outputs for unconfirmed txs
                assert tx.is_outgoing or (tx.is_incoming and tx.is_confirmed is False)

        assert found, "No outputs found in txs"

        # get txs with input query
        # TODO no inputs returned to filter

        # get txs with output query
        tx_query = MoneroTxQuery()
        tx_query.output_query = MoneroOutputQuery()
        tx_query.output_query.is_spent = False
        tx_query.output_query.account_index = 1
        tx_query.output_query.subaddress_index = 2
        txs = wallet.get_txs(tx_query)
        assert len(txs) > 0
        for tx in txs:
            assert len(tx.outputs) > 0
            found = False
            for output in tx.get_outputs_wallet():
                if output.is_spent is False and output.account_index == 1 and output.subaddress_index == 2:
                    found = True
                    break

            if not found:
                raise Exception(f"Tx does not contain specified output")

        # get unlocked txs
        tx_query = MoneroTxQuery()
        tx_query.is_locked = False
        txs = wallet.get_txs(tx_query)
        assert len(txs) > 0
        for tx in txs:
            assert tx.is_locked is False

        # get confirmed transactions sent from/to same wallet with a transfer with destinations
        # TODO implement send from/to multiple tests
        #tx_query = MoneroTxQuery()
        #tx_query.is_incoming = True
        #tx_query.is_outgoing = True
        #tx_query.include_outputs = True
        #tx_query.is_confirmed = True
        #tx_query.transfer_query = MoneroTransferQuery()
        #tx_query.transfer_query.has_destinations = True

        #txs = wallet.get_txs(tx_query)
        #assert len(txs) > 0
        #for tx in txs:
            #assert tx.is_incoming is True
            #assert tx.is_outgoing is True
            #assert tx.is_confirmed is True
            #assert len(tx.get_outputs_wallet()) > 0
            #assert tx.outgoing_transfer is not None
            #assert len(tx.outgoing_transfer.destinations) > 0

    # Validates inputs when getting transactions
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_validate_inputs_get_txs(self, wallet: MoneroWallet) -> None:
        # fetch random txs for testing
        random_txs: list[MoneroTxWallet] = TxUtils.get_random_transactions(wallet, None, 3, 5)

        # valid, invalid, and unknown tx hashes for tests
        tx_hash = random_txs[0].hash
        invalid_hash = "invalid_id"
        unknown_hash1 = "6c4982f2499ece80e10b627083c4f9b992a00155e98bcba72a9588ccb91d0a61"
        unknown_hash2 = "ff397104dd875882f5e7c66e4f852ee134f8cf45e21f0c40777c9188bc92e943"
        assert tx_hash is not None and len(tx_hash) > 0

        # fetch unknown tx hash
        fetched_tx = wallet.get_tx(unknown_hash1)
        assert fetched_tx is None

        # fetch unknown tx hash using query
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = unknown_hash1
        fetched_txs = wallet.get_txs(tx_query)
        assert len(fetched_txs) == 0

        # fetch unknwon tx hash in list
        txs = wallet.get_txs([tx_hash, unknown_hash1])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # fetch unknwon tx hashes in list
        txs = wallet.get_txs([tx_hash, unknown_hash1, unknown_hash2])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # fetch invalid hash
        fetched_tx = wallet.get_tx(invalid_hash)
        assert fetched_tx is None

        # fetch invalid hash list
        txs = wallet.get_txs([tx_hash, invalid_hash])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # fetch invalid hashes in list
        txs = wallet.get_txs([tx_hash, invalid_hash, "invalid_hash_2"])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # test collection of invalid hashes
        tx_query = MoneroTxQuery()
        tx_query.hashes = [tx_hash, invalid_hash, "invalid_hash_2"]
        txs = wallet.get_txs(tx_query)
        assert len(txs) == 1

        # test txs
        for tx in txs:
            TxUtils.test_tx_wallet(tx)

    # Can get transfers in the wallet, accounts, and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_transfers(self, wallet: MoneroWallet) -> None:
        # get all transfers
        TxUtils.get_and_test_transfers(wallet, None, None, True)

        # get transfers by account index
        non_default_incoming: bool = False
        for account in wallet.get_accounts(True):
            transfer_query = MoneroTransferQuery()
            transfer_query.account_index = account.index
            account_transfers = TxUtils.get_and_test_transfers(wallet, transfer_query, None, None)
            for transfer in account_transfers:
                assert transfer.account_index == account.index

            # get transfers by subaddress index
            subaddress_transfers: list[MoneroTransfer] = []
            for subaddress in account.subaddresses:
                subaddress_query = MoneroTransferQuery()
                subaddress_query.account_index = subaddress.account_index
                subaddress_query.subaddress_index = subaddress.index
                transfers = TxUtils.get_and_test_transfers(wallet, subaddress_query, None, None)

                for transfer in transfers:
                    # test account and subaddress indices
                    assert subaddress.account_index == transfer.account_index
                    if transfer.is_incoming() is True:
                        assert isinstance(transfer, MoneroIncomingTransfer)
                        assert subaddress.index == transfer.subaddress_index
                        if transfer.account_index != 0 and transfer.subaddress_index != 0:
                            non_default_incoming = True
                    else:
                        assert isinstance(transfer, MoneroOutgoingTransfer)
                        assert subaddress.index in transfer.subaddress_indices
                        if transfer.account_index != 0:
                            for subaddr_idx in transfer.subaddress_indices:
                                if subaddr_idx > 0:
                                    non_default_incoming = True
                                    break

                    # don't add duplicates
                    # TODO monero-wallet-rpc: duplicate outgoing transfers returned for different
                    # subaddress indices, way to return outgoing subaddress indices?

                    found: bool = False
                    for subaddress_transfer in subaddress_transfers:
                        eq_hash: bool = transfer.tx.hash == subaddress_transfer.tx.hash
                        if transfer.serialize() == subaddress_transfer.serialize() and eq_hash:
                            found = True
                            break

                    if not found:
                        subaddress_transfers.append(transfer)

            assert len(account_transfers) == len(subaddress_transfers)

            # collect unique subaddress indices
            subaddress_indices: set[int] = set()
            for transfer in subaddress_transfers:
                if transfer.is_incoming():
                    assert isinstance(transfer, MoneroIncomingTransfer)
                    assert transfer.subaddress_index is not None
                    subaddress_indices.add(transfer.subaddress_index)
                else:
                    assert isinstance(transfer, MoneroOutgoingTransfer)
                    for idx in transfer.subaddress_indices:
                        subaddress_indices.add(idx)

            # get and test transfers by subaddress indices
            transfer_query = MoneroTransferQuery()
            transfer_query.account_index = account.index
            for idx in subaddress_indices:
                transfer_query.subaddress_indices.append(idx)

            transfers = TxUtils.get_and_test_transfers(wallet, transfer_query, None, None)
            # TODO monero-wallet-rpc: these may not be equal because outgoing transfers are always from subaddress 0 (#5171)
            # and/or incoming transfers from/to same account are occluded (#4500)
            assert len(subaddress_transfers) == len(transfers)
            for transfer in transfers:
                assert transfer.account_index == account.index
                if transfer.is_incoming():
                    assert isinstance(transfer, MoneroIncomingTransfer)
                    assert transfer.subaddress_index in subaddress_indices
                else:
                    assert isinstance(transfer, MoneroOutgoingTransfer)
                    intersections: set[int] = set(subaddress_indices)
                    overlap = intersections.intersection(transfer.subaddress_indices)
                    assert overlap is not None and len(overlap) > 0, "Subaddresses must overlap"

        # ensure transfer found with non-zero account and subaddress indices
        assert non_default_incoming, "No transfers found in non-default account and subaddress; run send-to-multiple tests"

    # Validates inputs when getting transfers
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_validate_inputs_get_transfers(self, wallet: MoneroWallet) -> None:
        # test with invalid hash
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        transfer_query.tx_query = MoneroTxQuery()
        transfer_query.tx_query.hash = "invalid_id"

        transfers: list[MoneroTransfer] = wallet.get_transfers(transfer_query)
        assert len(transfers) == 0

        # test invalid hash in list
        random_txs = TxUtils.get_random_transactions(wallet, None, 3, 5)
        transfer_query.tx_query = MoneroTxQuery()
        random_hash = random_txs[0].hash
        assert random_hash is not None
        transfer_query.tx_query.hashes.append(random_hash)
        transfer_query.tx_query.hashes.append("invalid_id")

        transfers = wallet.get_transfers(transfer_query)
        assert len(transfers) > 0

        tx: MoneroTxWallet = transfers[0].tx
        for transfer in transfers:
            assert transfer.tx == tx

        # test unused subaddress indices
        transfer_query = MoneroTransferQuery()
        transfer_query.account_index = 0
        transfer_query.subaddress_indices.append(1234907) 
        transfers = wallet.get_transfers(transfer_query)

        # test unused subaddress index
        try:
            transfer_query = MoneroTransferQuery()
            transfer_query.account_index = 0
            transfer_query.subaddress_index = -1
            transfers = wallet.get_transfers(transfer_query)
            raise Exception("Should have failed")
        except Exception as e:
            assert "Should have failed" != str(e)

    # Can get outputs in the wallet, accounts, and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_outputs(self, wallet: MoneroWallet) -> None:
        # get all outputs
        TxUtils.get_and_test_outputs(wallet, None, True)

        # get outputs for each account
        non_default_incoming: bool = False
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        for account in accounts:
            # determine if account is used
            is_used: bool = False
            for subaddress in account.subaddresses:
                if subaddress.is_used is True:
                    is_used = True
                    break

            # get outputs by account index
            output_query: MoneroOutputQuery = MoneroOutputQuery()
            output_query.account_index = account.index
            account_outputs = TxUtils.get_and_test_outputs(wallet, output_query, is_used)
            for ouput in account_outputs:
                assert ouput.account_index == account.index

            # get outputs by subaddress index
            subaddress_outputs: list[MoneroOutputWallet] = []
            for subaddress in account.subaddresses:
                subaddr_query: MoneroOutputQuery = MoneroOutputQuery()
                subaddr_query.account_index = account.index
                subaddr_query.subaddress_index = subaddress.index
                outputs = TxUtils.get_and_test_outputs(wallet, subaddr_query, subaddress.is_used)
                for output in outputs:
                    assert subaddress.account_index == output.account_index
                    assert subaddress.index == output.subaddress_index
                    if output.account_index != 0 and output.subaddress_index != 0:
                        non_default_incoming = True
                    subaddress_outputs.append(output)

            assert len(subaddress_outputs) == len(account_outputs)

            # get outputs by subaddress indices
            subaddress_indices: set[int] = set()
            for output in subaddress_outputs:
                assert output.subaddress_index is not None
                subaddress_indices.add(output.subaddress_index)

            output_query = MoneroOutputQuery()
            output_query.account_index = account.index
            for sub_idx in subaddress_indices:
                output_query.subaddress_indices.append(sub_idx)

            outputs = TxUtils.get_and_test_outputs(wallet, output_query, is_used)
            assert len(outputs) == len(subaddress_outputs)

            for output in outputs:
                assert account.index == output.account_index
                assert output.subaddress_index is not None
                assert output.subaddress_index in subaddress_indices

        # ensure output found with non-zero account and subaddress indices
        assert non_default_incoming, "No outputs found in non-default account and subaddress; run send-to-multiple tests"

    # Can get outputs with additional configuration
    #@pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="TODO implement multiple send tests")
    def test_get_outputs_with_query(self, wallet: MoneroWallet) -> None:
        # get unspent outputs to account 0
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.account_index = 0
        output_query.is_spent = False
        outputs: list[MoneroOutputWallet] = TxUtils.get_and_test_outputs(wallet, output_query, None)

        for output in outputs:
            assert output.account_index == 0
            assert output.is_spent is False

        # get spent outputs to account 1
        output_query = MoneroOutputQuery()
        output_query.account_index = 1
        output_query.is_spent = True
        outputs = TxUtils.get_and_test_outputs(wallet, output_query, True)

        for output in outputs:
            assert output.account_index == 1
            assert output.is_spent is True

        # get random transactions
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_confirmed = True
        txs: list[MoneroTxWallet] = TxUtils.get_random_transactions(wallet, tx_query, 3, 5)

        # get outputs with a tx hash
        tx_hashes: list[str] = []
        for tx in txs:
            assert tx.hash is not None
            tx_hashes.append(tx.hash)
            output_query = MoneroOutputQuery()
            output_query.set_tx_query(MoneroTxQuery(), True)
            assert output_query.tx_query is not None
            output_query.tx_query.hash = tx.hash
            outputs = TxUtils.get_and_test_outputs(wallet, output_query, True)

            for output in outputs:
                assert output.tx is not None
                assert output.tx.hash is not None
                assert output.tx.hash in tx_hashes

        # get outputs with tx hashes
        tx_query = MoneroTxQuery()
        tx_query.hashes = tx_hashes
        output_query = MoneroOutputQuery()
        output_query.set_tx_query(tx_query, True)
        outputs = TxUtils.get_and_test_outputs(wallet, output_query, True)

        for output in outputs:
            assert output.tx is not None
            assert output.tx.hash is not None
            assert output.tx.hash in tx_hashes

        # get confirmed outputs to specifi subaddress with pre-built query
        account_idx: int = 0
        subaddress_idx: int = 1
        output_query = MoneroOutputQuery()
        output_query.account_index = account_idx
        output_query.subaddress_index = subaddress_idx
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        output_query.set_tx_query(tx_query, True)
        output_query.min_amount = TxUtils.MAX_FEE
        outputs = TxUtils.get_and_test_outputs(wallet, output_query, True)

        for output in outputs:
            assert output.account_index == account_idx
            assert output.subaddress_index == subaddress_idx
            assert output.tx is not None
            assert output.tx.is_confirmed is True
            assert output.amount is not None
            assert output.amount >= TxUtils.MAX_FEE

        # get output by key image
        output: MoneroOutputWallet = outputs[0]
        assert output.key_image is not None
        assert output.key_image.hex is not None
        output_query = MoneroOutputQuery()
        output_query.key_image = MoneroKeyImage()
        output_query.key_image.hex = output.key_image.hex
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 1
        output_result: MoneroOutputWallet = outputs[0]
        assert output_result.key_image is not None
        assert output.key_image.hex == output_result.key_image.hex

        # get outputs whose transaction is confirmed and has incoming and outgoing transfers
        output_query = MoneroOutputQuery()
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.is_incoming = True
        tx_query.is_outgoing = True
        tx_query.include_outputs = True
        output_query.set_tx_query(tx_query, True)
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) > 0

        for output in outputs:
            assert output.tx is not None
            assert isinstance(output.tx, MoneroTxWallet)
            assert output.tx.is_incoming is True
            assert output.tx.is_outgoing is True
            assert output.tx.is_confirmed is True
            outputs_wallet: list[MoneroOutputWallet] = output.tx.get_outputs_wallet()
            assert len(outputs_wallet) > 0
            assert output in outputs_wallet

    # Validates inputs when getting wallet outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_validate_inputs_get_outputs(self, wallet: MoneroWallet) -> None:
        # test with invalid hash
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.set_tx_query(MoneroTxQuery(), True)
        assert output_query.tx_query is not None
        output_query.tx_query.hash = "invalid_id"

        outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
        assert len(outputs) == 0

        # test invalid hash in list
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.include_outputs = True
        random_txs: list[MoneroTxWallet] = TxUtils.get_random_transactions(wallet, tx_query, 3, 5)

        for random_tx in random_txs:
            assert len(random_tx.outputs) > 0

        output_query = MoneroOutputQuery()
        output_query.set_tx_query(MoneroTxQuery(), False)
        assert output_query.tx_query is not None
        random_hash = random_txs[0].hash
        assert random_hash is not None and len(random_hash) > 0
        output_query.tx_query.hashes = [random_hash, "invalid_id"]

        outputs = wallet.get_outputs(output_query)
        assert len(outputs) > 0
        assert len(outputs) == len(random_txs[0].outputs)

        tx: MoneroTx = outputs[0].tx
        assert isinstance(tx, MoneroTxWallet)

        for output in outputs:
            assert output.tx == tx

    # Can export outputs in hex format
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_export_outputs(self, wallet: MoneroWallet) -> None:
        outputs_hex: str = wallet.export_outputs()
        logger.debug(f"Exported outputs hex: {outputs_hex}")
        # TODO: this will fail if wallet has no outputs; run these tests on new wallet
        assert outputs_hex is not None and len(outputs_hex) > 0

        # wallet exports outputs since last export by default
        outputs_hex = wallet.export_outputs()
        outputs_hex_all = wallet.export_outputs(True)
        assert len(outputs_hex_all) > len(outputs_hex)

    # Can import outputs in hex format
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_import_outputs(self, wallet: MoneroWallet) -> None:
        # export outputs hex
        outputs_hex: str = wallet.export_outputs()
        logger.debug(f"Exported outputs hex {outputs_hex}")
        # import outputs hex
        if len(outputs_hex) > 0:
            num_imported: int = wallet.import_outputs(outputs_hex)
            assert num_imported >= 0

    # Has correct accounting across accounts, subaddresses, txs, transfers and outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_accounting(self, wallet: MoneroWallet) -> None:
        # pre-fetch wallet balances, accounts, subaddresses and txs
        wallet_balance = wallet.get_balance()
        wallet_unlocked_balance = wallet.get_unlocked_balance()
        # includes subaddresses
        accounts = wallet.get_accounts(True)

        # test wallet balance
        GenUtils.test_unsigned_big_integer(wallet_balance)
        GenUtils.test_unsigned_big_integer(wallet_unlocked_balance)
        assert wallet_balance >= wallet_unlocked_balance

        # test that wallet balance equals sum of account balances
        accounts_balance: int = 0
        accounts_unlocked_balance: int = 0
        for account in accounts:
            # test that account balance equals sum of subaddress balances
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)
            assert account.balance is not None
            assert account.unlocked_balance is not None
            accounts_balance += account.balance
            accounts_unlocked_balance += account.unlocked_balance

        assert wallet_balance == accounts_balance
        assert wallet_unlocked_balance == accounts_unlocked_balance

        # TODO test that wallet balance equals net of wallet's incoming and outgoing tx amounts

        # balance may not equal sum of unspent outputs if unconfirmed txs
        # TODO monero-wallet-rpc: reason not to return unspent outputs on unconfirmed txs? then this isn't necessary
        txs = wallet.get_txs()
        has_unconfirmed_tx: bool = False
        for tx in txs:
            if tx.in_tx_pool:
                has_unconfirmed_tx = True

        # wallet balance is sum of all unspent outputs
        wallet_sum: int = 0
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.is_spent = False
        for output in wallet.get_outputs(output_query):
            assert output.amount is not None
            wallet_sum += output.amount

        if wallet_balance != wallet_sum:
            # txs may have changed in between calls to retry test
            wallet_sum = 0
            for output in wallet.get_outputs(output_query):
                assert output.amount is not None
                wallet_sum += output.amount

            if wallet_balance != wallet_sum:
                assert has_unconfirmed_tx, "Wallet balance must equal sum of unspent outputs if no unconfirmed txs"

        # account balances are sum of their unspent outputs
        for account in accounts:
            account_sum: int = 0
            output_query = MoneroOutputQuery()
            output_query.account_index = account.index
            output_query.is_spent = False
            account_outputs = wallet.get_outputs(output_query)
            for output in account_outputs:
                assert output.amount is not None
                account_sum += output.amount

            assert account.balance is not None
            if account.balance != account_sum:
                assert has_unconfirmed_tx, "Account balance must equal sum of its unspent outputs if no unconfirmed txs"

            # subaddress balances are sum of their unspent outputs
            for subaddress in account.subaddresses:
                subaddress_sum: int = 0
                output_query = MoneroOutputQuery()
                output_query.account_index = account.index
                output_query.subaddress_index = subaddress.index
                output_query.is_spent = False
                subaddress_outputs = wallet.get_outputs(output_query)
                for output in subaddress_outputs:
                    assert output.amount is not None
                    subaddress_sum += output.amount

                if subaddress_sum != subaddress.balance:
                    assert has_unconfirmed_tx, "Subaddress balance must equal sum of its unspent outputs if no unconfirmed txs"

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

    # Can sign and verify messages
    # TODO test with view-only wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sign_and_verify_messages(self, wallet: MoneroWallet) -> None:
        msg: str =  "This is a super important message which needs to be signed and verified."
        subaddress1: MoneroSubaddress = MoneroSubaddress()
        subaddress1.account_index = 0
        subaddress1.index = 0
        subaddress2: MoneroSubaddress = MoneroSubaddress()
        subaddress2.account_index = 0
        subaddress2.index = 1
        subaddress3: MoneroSubaddress = MoneroSubaddress()
        subaddress3.account_index = 1
        subaddress3.index = 0
        subaddresses: list[MoneroSubaddress] = [subaddress1, subaddress2, subaddress3]

        # test signing message with subaddresses
        for subaddress in subaddresses:
            assert subaddress.account_index is not None
            assert subaddress.index is not None
            account_idx = subaddress.account_index
            idx = subaddress.index

            # sign and verify message with spend key
            signature: str = wallet.sign_message(msg, MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY, account_idx, idx)
            result = wallet.verify_message(msg, wallet.get_address(account_idx, idx), signature)
            WalletUtils.test_message_signature_result(result, True)
            assert result.signature_type == MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY

            # verify message with incorrect address
            result = wallet.verify_message(msg, wallet.get_address(0, 2), signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with invalid address
            result = wallet.verify_message(msg, "invalid address", signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with external address
            result = wallet.verify_message(msg, TestUtils.get_external_wallet_address(), signature)
            WalletUtils.test_message_signature_result(result, False)

            # sign and verify message with view key
            signature = wallet.sign_message(msg, MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY, account_idx, idx)
            result = wallet.verify_message(msg, wallet.get_address(account_idx, idx), signature)
            WalletUtils.test_message_signature_result(result, True)
            assert result.signature_type == MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY

            # verify message with incorrect address
            result = wallet.verify_message(msg, wallet.get_address(0, 2), signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with invalid address
            result = wallet.verify_message(msg, "invalid address", signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with external address
            result = wallet.verify_message(msg, TestUtils.get_external_wallet_address(), signature)
            WalletUtils.test_message_signature_result(result, False)

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

    # Can freeze and thaw outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_freeze_outputs(self, wallet: MoneroWallet) -> None:
        # get an available output
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.is_spent = False
        output_query.is_frozen = False
        output_query.set_tx_query(MoneroTxQuery(), True)
        assert output_query.tx_query is not None
        output_query.tx_query.is_locked = False
        outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
        assert len(outputs) > 0
        for output in outputs:
            assert output.is_frozen is False

        output: MoneroOutputWallet = outputs[0]
        assert output.tx is not None
        assert isinstance(output.tx, MoneroTxWallet)
        assert output.tx.is_locked is False
        assert output.is_spent is False
        assert output.is_frozen is False
        assert output.key_image is not None
        assert output.key_image.hex is not None
        assert wallet.is_output_frozen(output.key_image.hex) is False

        # freeze output by key image
        output_query = MoneroOutputQuery()
        output_query.is_frozen = True
        num_frozen_before: int = len(wallet.get_outputs(output_query))
        wallet.freeze_output(output.key_image.hex)
        is_frozen: bool = wallet.is_output_frozen(output.key_image.hex)
        assert is_frozen

        # test querying
        frozen_outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
        num_frozen: int = len(frozen_outputs)
        assert num_frozen == num_frozen_before + 1
        output_query = MoneroOutputQuery()
        output_query.key_image = MoneroKeyImage()
        output_query.key_image.hex = output.key_image.hex
        output_query.is_frozen = True
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 1
        output_frozen: MoneroOutputWallet = outputs[0]
        assert output_frozen.is_frozen is True
        assert output_frozen.key_image is not None
        assert output.key_image.hex == output_frozen.key_image.hex

        # try to sweep frozen output
        try:
            tx_config: MoneroTxConfig = MoneroTxConfig()
            tx_config.address = wallet.get_primary_address()
            tx_config.key_image = output.key_image.hex
            wallet.sweep_output(tx_config)
            raise Exception("Should have thrown error")
        except Exception as e:
            if "No outputs found" != str(e):
                raise

        # try to freeze empty key image
        try:
            wallet.freeze_output("")
            raise Exception("Should have thrown error")
        except Exception as e:
            if "Must specify key image to freeze" != str(e):
                raise

        # try to freeze bad key image
        try:
            wallet.freeze_output("123")
            raise Exception("Should have thrown error")
        except Exception as e:
            logger.debug(e)
            #if "Bad key image" != str(e):
            #    raise

        # thaw output by key image
        wallet.thaw_output(output.key_image.hex)
        is_frozen = wallet.is_output_frozen(output.key_image.hex)
        assert is_frozen is False

        # test querying
        output_query = MoneroOutputQuery()
        output_query.is_frozen = True
        assert num_frozen_before == len(wallet.get_outputs(output_query))

        output_query = MoneroOutputQuery()
        output_query.key_image = MoneroKeyImage()
        output_query.key_image.hex = output.key_image.hex
        output_query.is_frozen = True
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 0

        output_query.is_frozen = False
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 1

        output_thawed: MoneroOutputWallet = outputs[0]
        assert output_thawed.is_frozen is False
        assert output_thawed.key_image is not None
        assert output_thawed.key_image.hex == output.key_image.hex

    # Provides key images of spent outputs
    def test_input_key_images(self, wallet: MoneroWallet) -> None:
        # get subaddress to test input key images
        subaddress: Optional[MoneroSubaddress] = WalletUtils.select_subaddress_with_min_balance(wallet, TxUtils.MAX_FEE)
        assert subaddress is not None, "No subaddress with outputs found for test input key images; fund wallet"
        assert subaddress.account_index is not None
        assert subaddress.index is not None
        account_index: int = subaddress.account_index
        subaddress_index: int = subaddress.index

        # test unrelayed single transaction
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = account_index
        tx_config.destinations.append(MoneroDestination(wallet.get_primary_address(), TxUtils.MAX_FEE))
        spend_tx: MoneroTxWallet = wallet.create_tx(tx_config)
        TxUtils.test_spend_tx(spend_tx)

        # test unrelayed split transactions
        txs: list[MoneroTxWallet] = wallet.create_txs(tx_config)
        for tx in txs:
            TxUtils.test_spend_tx(tx)

        # test unrelayed sweep dust
        dust_key_images: list[str] = []
        txs = wallet.sweep_dust(False)
        for tx in txs:
            TxUtils.test_spend_tx(tx)
            for tx_input in tx.inputs:
                assert tx_input.key_image is not None
                assert tx_input.key_image.hex is not None
                dust_key_images.append(tx_input.key_image.hex)

        # get available outputs above min amount
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.account_index = account_index
        output_query.subaddress_index = subaddress_index
        output_query.is_spent = False
        output_query.is_frozen = False
        output_query.min_amount = TxUtils.MAX_FEE
        output_query.set_tx_query(MoneroTxQuery(), True)
        assert output_query.tx_query is not None
        output_query.tx_query.is_locked = False
        outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)

        assert len(outputs) > 0, "No outputs found"
        logger.debug(f"Found {len(outputs)} outputs")

        # filter dust outputs
        dust_outputs: list[MoneroOutputWallet] = []
        for output in outputs:
            assert output.key_image is not None
            assert output.key_image.hex is not None
            if output.key_image.hex in dust_key_images:
                dust_outputs.append(output)

        logger.debug(f"Found {len(dust_outputs)} dust outputs")

        # remove dust outputs from outputs
        for dust_output in dust_outputs:
            if dust_output in outputs:
                outputs.remove(dust_output)

        assert len(outputs) > 0, "No available outputs found"
        logger.debug(f"Using {len(outputs)} available outputs")

        # test unrelayed sweep output
        tx_config = MoneroTxConfig()
        tx_config.address = wallet.get_primary_address()
        output_key_image = outputs[0].key_image
        assert output_key_image is not None
        tx_config.key_image = output_key_image.hex
        spend_tx = wallet.sweep_output(tx_config)
        TxUtils.test_spend_tx(spend_tx)

        # test unrelayed sweep wallet ensuring all non-dust outputs are spent
        available_key_images: set[str] = set()
        for output in outputs:
            assert output.key_image is not None
            assert output.key_image.hex is not None
            available_key_images.add(output.key_image.hex)
        swept_key_images: set[str] = set()
        tx_config = MoneroTxConfig()
        tx_config.account_index = account_index
        tx_config.subaddress_indices.append(subaddress_index)
        tx_config.address = wallet.get_primary_address()
        txs = wallet.sweep_unlocked(tx_config)

        for tx in txs:
            TxUtils.test_spend_tx(tx)
            for input_wallet in tx.inputs:
                assert input_wallet.key_image is not None
                assert input_wallet.key_image.hex is not None
                swept_key_images.add(input_wallet.key_image.hex)

        assert len(swept_key_images) > 0

        # max skipped output is less than max fee amount
        max_skipped_output: Optional[MoneroOutputWallet] = None
        for output in outputs:
            assert output.key_image is not None
            assert output.key_image.hex is not None
            assert output.amount is not None
            if output.key_image.hex not in swept_key_images:
                if max_skipped_output is None or max_skipped_output.amount < output.amount: # type: ignore
                    max_skipped_output = output

        if max_skipped_output is not None:
            assert max_skipped_output.amount is not None
            assert max_skipped_output.amount < TxUtils.MAX_FEE

    #region Test Relays

    # Validates inputs when sending funds
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_validate_inputs_sending_funds(self, wallet: MoneroWallet) -> None:
        # try sending with invalid address
        try:
            tx_config = MoneroTxConfig()
            tx_config.address = "my invalid address"
            tx_config.account_index = 0
            tx_config.amount = TxUtils.MAX_FEE
            wallet.create_tx(tx_config)
            raise Exception("Should have thrown")
        except Exception as e:
            if str(e) != "Invalid destination address":
                raise

    # Can send to self
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_to_self(self, wallet: MoneroWallet) -> None:
        # wait for txs to confirm and for sufficient unlocked balance
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        amount: int = TxUtils.MAX_FEE * 3
        TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(wallet, 0, None, amount)

        # collect sender balances before
        balance1 = wallet.get_balance()
        unlocked_balance1 = wallet.get_unlocked_balance()

        # test error sending funds to self with integrated subaddress
        # TODO (monero-project): sending funds to self 
        # with integrated subaddress throws error: https://github.com/monero-project/monero/issues/8380

        try:
            tx_config = MoneroTxConfig()
            tx_config.account_index = 0
            subaddress = wallet.get_subaddress(0, 1)
            assert subaddress.address is not None
            address = subaddress.address
            tx_config.address = MoneroUtils.get_integrated_address(TestUtils.NETWORK_TYPE, address, '').integrated_address
            tx_config.amount = amount
            tx_config.relay = True
            wallet.create_tx(tx_config)
            raise Exception("Should have failed sending to self with integrated subaddress")
        except Exception as e:
            if "Total received by" not in str(e):
                raise

        # send funds to self
        tx_config = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.address = wallet.get_integrated_address().integrated_address
        tx_config.amount = amount
        tx_config.relay = True

        tx = wallet.create_tx(tx_config)

        # test balances after
        balance2: int = wallet.get_balance()
        unlocked_balance2: int = wallet.get_unlocked_balance()

        # unlocked balance should decrease
        assert unlocked_balance2 < unlocked_balance1
        assert tx.fee is not None
        expected_balance = balance1 - tx.fee
        assert expected_balance == balance2, "Balance after send was not balance before - fee"

    # Can send to external address
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS is disabled")
    def test_send_to_external(self, wallet: MoneroWallet) -> None:
        recipient: Optional[MoneroWallet] = None
        try:
            # wait for txs to confirm and for sufficient unlocked balance
            TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
            amount: int = TxUtils.MAX_FEE * 3
            TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(wallet, 0, None, amount)

            # create recipient wallet
            recipient = self._create_wallet(MoneroWalletConfig())

            balance1: int = wallet.get_balance()
            unlocked_balance1: int = wallet.get_unlocked_balance()

            # send funds to recipient
            tx_config: MoneroTxConfig = MoneroTxConfig()
            tx_config.account_index = 0
            tx_config.address = wallet.get_integrated_address(recipient.get_primary_address(), "54491f3bb3572a37").integrated_address
            tx_config.amount = amount
            tx_config.relay = True
            tx: MoneroTxWallet = wallet.create_tx(tx_config)

            # test sender balances after
            balance2: int = wallet.get_balance()
            unlocked_balance2: int = wallet.get_unlocked_balance()

            # unlocked balance should decrease
            assert unlocked_balance2 < unlocked_balance1
            assert tx.fee is not None
            expected_balance = balance1 - tx.get_outgoing_amount() - tx.fee
            assert expected_balance == balance2, "Balance after send was not balance before - net tx amount - fee (5 - 1 != 4 test)"

            # test recipient balance after
            recipient.sync()
            tx_query: MoneroTxQuery = MoneroTxQuery()
            tx_query.is_confirmed = False
            txs = wallet.get_txs(tx_query)

            assert len(txs) > 0
            assert amount == recipient.get_balance()

        finally:
            if recipient is not None:
                self._close_wallet(recipient)

    # Can scan transactions by id
    def test_scan_txs(self, wallet: MoneroWallet) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.seed = wallet.get_seed()
        config.restore_height = 0
        scan_wallet: MoneroWallet = self._create_wallet(config)
        logger.debug(f"Created scan wallet")
        TxUtils.test_scan_txs(wallet, scan_wallet)

    # Can get the default fee priority
    def test_get_default_fee_priority(self, wallet: MoneroWallet) -> None:
        default_priority: MoneroTxPriority = wallet.get_default_fee_priority()
        assert int(default_priority) > 0

    #endregion

    #endregion
