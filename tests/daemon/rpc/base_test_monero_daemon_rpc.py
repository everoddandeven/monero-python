from __future__ import annotations

import logging

import pytest
from monero import MoneroDaemonRpc, MoneroWalletRpc
from typing_extensions import override

from utils import BaseTestClass, BinaryBlockContext, IntegrationTestUtils, TestUtils as Utils, WalletType

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpc")


class BaseTestMoneroDaemonRpc(BaseTestClass):
    """Rpc daemon integration tests."""

    BINARY_BLOCK_CTX: BinaryBlockContext = BinaryBlockContext()

    _test_wallet: MoneroWalletRpc | None = None

    @override
    def before_all(self) -> None:
        # setup wallet rpc for tests
        IntegrationTestUtils.setup(WalletType.RPC)

    @pytest.fixture(scope="class")
    @classmethod
    def daemon(cls) -> MoneroDaemonRpc:
        """Test rpc daemon instance"""
        return Utils.get_daemon_rpc()

    @pytest.fixture(scope="class")
    @classmethod
    def wallet(cls) -> MoneroWalletRpc:
        """Test rpc wallet instance"""
        if cls._test_wallet is None:
            cls._test_wallet = Utils.get_wallet_rpc()

        return cls._test_wallet
