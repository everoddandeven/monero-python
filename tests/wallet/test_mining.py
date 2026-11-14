from __future__ import annotations

import logging

import pytest
from monero import MoneroDaemonRpc, MoneroMiningStatus, MoneroWallet
from typing_extensions import override

from utils import TestUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletMining")


class BaseTestMoneroWalletMining(BaseTestMoneroWallet):
    """Common wallet mining tests."""

    # Can start and stop mining
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        status: MoneroMiningStatus = daemon.get_mining_status()
        if status.is_active:
            wallet.stop_mining()
        wallet.start_mining(1, False, True)
        wallet.stop_mining()


@pytest.mark.integration
class TestMoneroWalletFullMining(FullWalletSupport, BaseTestMoneroWalletMining):
    """Full wallet mining integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcMining(RpcWalletSupport, BaseTestMoneroWalletMining):
    """Rpc wallet mining integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysMining(KeysWalletSupport, BaseTestMoneroWalletMining):
    """Keys-only wallet mining unit tests."""

    @pytest.mark.not_supported
    @override
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_mining(daemon, wallet)
