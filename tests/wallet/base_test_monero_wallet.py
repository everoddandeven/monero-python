from __future__ import annotations

import logging
from abc import abstractmethod
from configparser import ConfigParser
from typing import Optional

import pytest
from monero import MoneroDaemonRpc, MoneroMiningStatus, MoneroWallet, MoneroWalletConfig
from typing_extensions import override

from utils import (
    BaseTestClass,
    IntegrationTestUtils,
    MiningUtils,
    MultisigSampleCodeTester,
    TestUtils,
    WalletType,
)

logger: logging.Logger = logging.getLogger("TestMoneroWalletCommon")


class BaseTestMoneroWallet(BaseTestClass):
    """Common wallet tests that every Monero wallet implementation should support."""

    _test_wallet: Optional[MoneroWallet] = None
    """Private reference to test wallet instance."""

    @classmethod
    def get_wallet_type(cls) -> WalletType:
        """Wallet type to test."""
        return WalletType.UNDEFINED

    @classmethod
    def supports_save(cls) -> bool:
        wallet_type: WalletType = cls.get_wallet_type()
        return wallet_type == WalletType.FULL or wallet_type == WalletType.RPC

    class Config:
        """Wallet test configuration."""

        seed: str = ""
        """Test wallet seed."""

        @classmethod
        def parse(cls, parser: ConfigParser) -> BaseTestMoneroWallet.Config:
            """Parse wallet test configuration.

            :param ConfigParser parser: configuration parser.
            :returns BaseTestMoneroWallet.Config: wallet test configuration.
            """
            section: str = "test_create_wallet_from_seed"
            if not parser.has_section(section):
                # raise exception if section not found
                raise Exception(f"Cannot find section '{section}' in test_monero_wallet_common.ini")
            config: BaseTestMoneroWallet.Config = cls()
            # parse configuration
            config.seed = parser.get(section, "seed")
            return config

    @classmethod
    def _get_test_daemon(cls) -> MoneroDaemonRpc:
        """Get the daemon to test.

        :returns MoneroDaemonRpc: the daemon to test.
        """
        return TestUtils.get_daemon_rpc()

    @classmethod
    def get_test_wallet(cls) -> MoneroWallet:
        """Get the main wallet to test.

        :returns MoneroWallet: the wallet to test.
        """
        if cls._test_wallet is None:
            wallet_type: WalletType = cls.get_wallet_type()
            if wallet_type == WalletType.FULL:
                cls._test_wallet = TestUtils.get_wallet_full()
            elif wallet_type == WalletType.RPC:
                cls._test_wallet = TestUtils.get_wallet_rpc()
            elif wallet_type == WalletType.KEYS:
                cls._test_wallet = TestUtils.get_wallet_keys()
            else:
                raise Exception("Cannot get test wallet: No wallet type setup for tests")

        return cls._test_wallet

    @abstractmethod
    def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
        """Open a test wallet with default configuration for each wallet type.

        :param MoneroWalletConfig | None config: configures the wallet to open.
        :returns MoneroWallet: is the opened wallet.
        """
        ...

    @abstractmethod
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWallet:
        """Create a test wallet with default configuration for each wallet type.

        :param MoneroWalletConfig config: configures the wallet to create.
        :returns MoneroWallet: is the created wallet.
        """
        ...

    @abstractmethod
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        """Close a test wallet with customization for each wallet type.

        :param MoneroWallet wallet: the wallet to close.
        :param bool save: whether or not to save the wallet.
        """
        ...

    @abstractmethod
    def _get_seed_languages(self) -> list[str]:
        """Get the wallet's supported languages for the seed. This is an
        instance method for wallet rpc and a static utility for other wallets.

        :returns list[str]: the wallet's supported languages.
        """
        ...

    def _open_wallet_from_path(self, path: str, password: str | None) -> MoneroWallet:
        """Open a wallet from path.

        :param str path: wallet path to open.
        :param str | None password: wallet password.
        :returns MoneroWallet: opened wallet.
        """
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.password = password

        return self._open_wallet(config)

    def get_daemon_rpc_uri(self) -> str:
        return TestUtils.DAEMON_RPC_URI

    @classmethod
    def is_random_wallet_config(cls, config: Optional[MoneroWalletConfig]) -> bool:
        """Check if config is valid to create a random wallet.

        :param MoneroWalletConfig | None config: config to check.
        :returns bool: `True` if config is valid to create a random wallet, `False` otherwise.
        """
        assert config is not None
        return config.seed is None and config.primary_address is None

    # Test wallet configuration
    @pytest.fixture(scope="class")
    @classmethod
    def test_config(cls) -> BaseTestMoneroWallet.Config:
        """Test configuration."""
        parser: ConfigParser = ConfigParser()
        parser.read('tests/config/test_monero_wallet_common.ini')
        return BaseTestMoneroWallet.Config.parse(parser)

    # Test daemon fixture
    @pytest.fixture(scope="class")
    @classmethod
    def daemon(cls) -> MoneroDaemonRpc:
        """Test rpc daemon instance."""
        return TestUtils.get_daemon_rpc()

    # Test wallet fixture
    @pytest.fixture(scope="class")
    @classmethod
    def wallet(cls) -> MoneroWallet:
        """Test wallet instance."""
        pytest.skip("No wallet test instance setup")

    # Before all tests
    @override
    def before_all(self) -> None:
        super().before_all()
        IntegrationTestUtils.setup(self.get_wallet_type())

    # After all tests
    @override
    def after_all(self) -> None:
        super().after_all()
        daemon: MoneroDaemonRpc = self._get_test_daemon()
        MiningUtils.try_stop_mining(daemon)
        # the wallet is not closed here: the classes of the topics share it, and TestUtils.close_wallets() closes it
        # when the session ends (see conftest.py)

    # Before each test
    @override
    def before_each(self, request: pytest.FixtureRequest) -> None:
        super().before_each(request)
        daemon: MoneroDaemonRpc = self._get_test_daemon()
        wallet: MoneroWallet = self.get_test_wallet()
        status: MoneroMiningStatus = daemon.get_mining_status()

        if status.is_active is True:
            wallet.stop_mining()

    # After each test
    @override
    def after_each(self, request: pytest.FixtureRequest) -> None:
        super().after_each(request)
        daemon: MoneroDaemonRpc = self._get_test_daemon()
        status: MoneroMiningStatus = daemon.get_mining_status()

        if status.is_active is True:
            logger.warning(f"Mining is active after test {request.node.name}") # type: ignore

    def _test_multisig_sample(self, m: int, n: int) -> None:
        """
        Test multisig sample code.

        :param int m: multisig threshold.
        :param int n: number of participants.
        """
        # create participant wallets
        wallets: list[MoneroWallet] = []

        for i in range(n):
            wallets.append(self._create_wallet(MoneroWalletConfig()))
            logger.debug(f"Created multisig wallet participant {i + 1}")

        tester: MultisigSampleCodeTester = MultisigSampleCodeTester(m, wallets)
        tester.test()

        if self.get_wallet_type() == WalletType.RPC:
            TestUtils.free_wallet_rpc_resources()
