from __future__ import annotations

import logging

import pytest
from monero import MoneroDaemonRpc, MoneroSubmitTxResult, MoneroTxConfig, MoneroTxWallet, MoneroWallet
from typing_extensions import override

from utils import TestUtils, TxWalletUtils, WalletSendUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletPool")


class BaseTestMoneroWalletPool(BaseTestMoneroWallet):
    """Common wallet pool tests."""

    # Can sync with txs in the pool sent from/to the same account
    # TODO this test fails because wallet does not recognize pool tx sent from/to same account
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_sync_with_pool_same_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.account_index = 0
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE * 5
        config.relay = True
        WalletSendUtils.test_sync_with_pool_submit(daemon, wallet, config)

    # Can sync with txs submitted and flushed from the pool
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    @pytest.mark.skipif(TestUtils.CI, reason="CI is too slow to catchup failed txs (see wallet2::process_unconfirmed_transfer)")
    def test_sync_with_pool_submit_and_flush(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        logger.warning("This test takes at least 500 seconds (~8 minutes) to catchup failed txs (see wallet2::process_unconfirmed_transfer).")
        config: MoneroTxConfig = MoneroTxConfig()
        config.account_index = 2
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE * 5
        config.relay = False
        WalletSendUtils.test_sync_with_pool_submit(daemon, wallet, config)

    # Can sync with txs submitted and relayed from the pool
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_with_pool_submit_and_relay(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.account_index = 2
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE * 5
        config.relay = True
        WalletSendUtils.test_sync_with_pool_submit(daemon, wallet, config)

    # can sync with txs relayed to the pool
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(TestUtils.LITE_MODE, reason="LITE_MODE enabled")
    def test_sync_with_pool_relay(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # wait one time for wallet txs in the pool to clear
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # record wallet balances before submitting tx to pool
        balance_before: int = wallet.get_balance()
        unlocked_balance_before: int = wallet.get_unlocked_balance()

        # create config
        config: MoneroTxConfig = MoneroTxConfig()
        config.account_index = 2
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE * 5

        # create tx to relay
        tx: MoneroTxWallet = wallet.create_tx(config)
        assert tx.hash is not None
        assert tx.full_hex is not None
        assert tx.fee is not None

        # create another tx using same config which would be double spend
        tx_double_spend: MoneroTxWallet = wallet.create_tx(config)
        assert tx_double_spend.hash is not None
        assert tx_double_spend.full_hex is not None

        # relay first tx directly to daemon
        result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex)
        assert result.is_good, "Transaction could not be submitted to the pool"

        # sync wallet which updates from pool
        wallet.sync()

        # collect issues to report at end of test
        issues: list[str] = []

        # wallet should be aware of tx
        fetched: MoneroTxWallet | None = wallet.get_tx(tx.hash)
        assert fetched is not None, "Wallet should be aware of its tx in pool after syncing"

        # test wallet balances
        if unlocked_balance_before == wallet.get_unlocked_balance():
            issues.append("unlocked balance should have decreased after relaying tx directly to the daemon")

        if balance_before == wallet.get_balance():
            issues.append("balance should have decreased after relaying tx directly to the daemon")

        expected_balance: int = balance_before - tx.fee
        if expected_balance != wallet.get_balance():
            issues.append(f"expected balance after relaying tx directly to the daemon to be {expected_balance} but was {wallet.get_balance()}")

        # submit double spend tx
        result_double_spend: MoneroSubmitTxResult = daemon.submit_tx_hex(tx_double_spend.full_hex)
        if result_double_spend.is_good:
            daemon.flush_tx_pool(tx_double_spend.hash)
            issues.append("Tx submit result should have been double spend")

        # sync wallet which updates from pool
        wallet.sync()

        # create tx using same config which is no longer double spend
        tx2: MoneroTxWallet | None = None
        try:
            config_copy: MoneroTxConfig = config.copy()
            config_copy.relay = True
            tx2 = wallet.create_tx(config_copy)
        except Exception as e:
            logger.warning(e)
            # TODO monero-project: this fails meaning wallet did not recognize tx relayed directly to pool
            issues.append("creating and sending tx through wallet should succeed after syncing wallet with pool but creates a double spend")

        # submit the transaction to the pool and test
        if tx2 is not None:
            assert tx2.hash is not None
            assert tx2.full_hex is not None
            result2: MoneroSubmitTxResult = daemon.submit_tx_hex(tx2.full_hex, True)
            if result2.is_double_spend:
                issues.append("creating and submitting tx to daemon should succeed after syncing wallet with pool but was a double spend")
            else:
                assert result2.is_good

            wallet.sync()
            if wallet.get_tx(tx2.hash) is None:
                issues.append("wallet should be aware of tx created and relayed through it after syncing with pool")

            daemon.flush_tx_pool(tx2.hash)

        # should be no issues
        for issue in issues:
            logger.warning(issue)

        assert len(issues) == 0, f"test_sync_with_pool_relay has {len(issues)} issues"


@pytest.mark.integration
class TestMoneroWalletFullPool(FullWalletSupport, BaseTestMoneroWalletPool):
    """Full wallet pool integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcPool(RpcWalletSupport, BaseTestMoneroWalletPool):
    """Rpc wallet pool integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysPool(KeysWalletSupport, BaseTestMoneroWalletPool):
    """Keys-only wallet pool unit tests."""

    @pytest.mark.not_supported
    @override
    def test_sync_with_pool_same_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_same_accounts(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_sync_with_pool_submit_and_flush(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_submit_and_flush(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_sync_with_pool_submit_and_relay(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_submit_and_relay(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_sync_with_pool_relay(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_sync_with_pool_relay(daemon, wallet)
