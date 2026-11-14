from __future__ import annotations

import logging

import pytest
from monero import MoneroDaemonRpc, MoneroTxConfig, MoneroWallet
from typing_extensions import override

from utils import TestUtils, TxWalletUtils, WalletSendUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletUpdateLocked")


class BaseTestMoneroWalletUpdateLocked(BaseTestMoneroWallet):
    """Common wallet update locked tests."""

    # TODO: test sending to multiple accounts
    # Can update a locked tx sent from/to the same account as blocks are added to the chain
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=["Daemon is busy", r"Cannot reconcile integrals:.*m_is_incoming"])
    def test_update_locked_same_account(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE
        config.account_index = 0
        config.can_split = False
        config.relay = True
        WalletSendUtils.test_send_and_update_txs(daemon, wallet, config)

    # Can update split locked txs sent from/to the same account as blocks are added to the chain
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=["Daemon is busy", r"Cannot reconcile integrals:.*m_is_incoming"])
    def test_update_locked_same_account_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE
        config.account_index = 0
        config.can_split = True
        config.relay = True
        WalletSendUtils.test_send_and_update_txs(daemon, wallet, config)

    # TODO on wallet full is flaky due to `Cannot reconcile integrals:  0 vs  1. tx wallet m_is_incoming` error
    # Can update a locked tx sent from/to different accounts as blocks are added to the chain
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=["Daemon is busy", r"Cannot reconcile integrals:.*m_is_incoming"])
    def test_update_locked_different_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = wallet.get_subaddress(1, 0).address
        config.amount = TxWalletUtils.MAX_FEE
        config.account_index = 0
        config.can_split = False
        config.relay = True
        WalletSendUtils.test_send_and_update_txs(daemon, wallet, config)

    # Can update locked, split txs sent from/to different accounts as blocks are added to the chain
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=["Daemon is busy", r"Cannot reconcile integrals:.*m_is_incoming"])
    def test_update_locked_different_accounts_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = wallet.get_subaddress(1, 0).address
        config.amount = TxWalletUtils.MAX_FEE
        config.account_index = 0
        config.can_split = True
        config.relay = True
        WalletSendUtils.test_send_and_update_txs(daemon, wallet, config)


@pytest.mark.integration
class TestMoneroWalletFullUpdateLocked(FullWalletSupport, BaseTestMoneroWalletUpdateLocked):
    """Full wallet update locked integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcUpdateLocked(RpcWalletSupport, BaseTestMoneroWalletUpdateLocked):
    """Rpc wallet update locked integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysUpdateLocked(KeysWalletSupport, BaseTestMoneroWalletUpdateLocked):
    """Keys-only wallet update locked unit tests."""

    @pytest.mark.not_supported
    @override
    def test_update_locked_same_account(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_same_account(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_update_locked_same_account_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_same_account_split(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_update_locked_different_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_different_accounts(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_update_locked_different_accounts_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_update_locked_different_accounts_split(daemon, wallet)
