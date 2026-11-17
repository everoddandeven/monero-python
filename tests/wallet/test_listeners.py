from __future__ import annotations

import logging
from time import monotonic, sleep

import pytest
from monero import MoneroDaemonRpc, MoneroTxConfig, MoneroTxWallet, MoneroWallet, MoneroWalletConfig
from typing_extensions import override

from utils import MiningUtils, TestUtils, TxWalletUtils, WalletNotificationCollector, WalletNotificationsTester
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, LightWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletListeners")

_SAME_ACCOUNT_NOTIFICATIONS: str = (
    "TODO monero-project: wallet2 counts the funds sent to the account that they come from as change, on the full wallet and on the "
    "rpc one: the tx has a smaller incoming amount (none when sweeping) and the output received by that account is not notified, so "
    "the balances and the received outputs differ from the expected ones. Check it with monero-java before removing this mark"
)
"""Why the notifications tests that send to the same account fail."""


class BaseTestMoneroWalletListeners(BaseTestMoneroWallet):
    """Common wallet listeners tests."""

    # Can stop listening
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_stop_listening(self) -> None:
        # create wallet and start background synchronizing
        wallet: MoneroWallet = self._create_wallet(MoneroWalletConfig())

        # add listener
        listener: WalletNotificationCollector = WalletNotificationCollector()
        wallet.add_listener(listener)
        assert len(wallet.get_listeners()) == 1
        sleep(1)

        # remove listener and close
        wallet.remove_listener(listener)
        assert len(wallet.get_listeners()) == 0
        self._close_wallet(wallet)

    # Can be created and receive funds
    # TODO this test is flaky on monero-wallet-rpc because of mining speed
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=[])
    def test_create_and_receive(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # create random wallet
        receiver: MoneroWallet = self._create_wallet(MoneroWalletConfig())
        try:
            # listen for received funds
            my_listener: WalletNotificationCollector = WalletNotificationCollector()
            receiver.add_listener(my_listener)
            assert len(receiver.get_listeners()) > 0

            # wait for txs to confirm and for sufficient unlocked balance
            TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
            TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(wallet, 0, None, TxWalletUtils.MAX_FEE)

            # send funds to the receiver
            tx_config: MoneroTxConfig = MoneroTxConfig()
            tx_config.account_index = 0
            tx_config.address = receiver.get_primary_address()
            tx_config.amount = TxWalletUtils.MAX_FEE
            tx_config.relay = True
            sent_tx: MoneroTxWallet = wallet.create_tx(tx_config)
            assert sent_tx.hash is not None

            # wait for funds to confirm
            MiningUtils.try_start_mining()
            while True:
                tx: MoneroTxWallet | None = wallet.get_tx(sent_tx.hash)
                assert tx is not None
                assert tx.is_confirmed is not None
                if tx.is_confirmed:
                    logger.debug(f"Confirmed tx at height {tx.get_height()}")
                    break

                assert tx.is_failed is False, f"Tx failed in mempool: {tx.hash}"
                daemon.wait_for_next_block_header()

            # receiver should notify listeners of received outputs within a few rpc refresh / poll periods
            deadline: float = monotonic() + TestUtils.SYNC_PERIOD_IN_MS * 10 / 1000
            while len(my_listener.outputs_received) == 0 and monotonic() < deadline:
                sleep(1)
            assert len(my_listener.outputs_received) > 0
        finally:
            logger.debug("Closing receiver wallet...")
            self._close_wallet(receiver)
            logger.debug("Closed receiver wallet")
            MiningUtils.try_stop_mining()

    #region Notifications

    def _test_wallet_notifications(
        self, test_name: str, daemon: MoneroDaemonRpc, wallet: MoneroWallet, same_wallet: bool, same_account: bool,
        sweep_output: bool, create_then_relay: bool, unlock_delay: int
    ) -> None:
        """Send funds from the test wallet and test the notifications of the sender and of the receiver until the funds unlock.

        :param str test_name: name of the test, for the report of the issues.
        :param MoneroDaemonRpc daemon: daemon of the test network.
        :param MoneroWallet wallet: test wallet, that sends the funds.
        :param bool same_wallet: send to the test wallet, otherwise to a new one.
        :param bool same_account: send to the account the funds come from.
        :param bool sweep_output: sweep an output instead of sending to multiple accounts.
        :param bool create_then_relay: create the tx without relaying it, then relay it.
        :param int unlock_delay: blocks to wait before testing the unlock notifications.
        """
        receiver: MoneroWallet = wallet if same_wallet else self._create_wallet(MoneroWalletConfig())
        try:
            tester: WalletNotificationsTester = WalletNotificationsTester(
                wallet, receiver, daemon, same_account, sweep_output, create_then_relay, unlock_delay
            )
            tester.test(test_name)
        finally:
            if receiver is not wallet:
                self._close_wallet(receiver)

    # Can generate notifications sending to different wallet
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_notifications_different_wallet(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        self._test_wallet_notifications("test_notifications_different_wallet", daemon, wallet, False, False, False, False, 0)

    # Can generate notifications sending to different wallet when relayed
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_notifications_different_wallet_when_relayed(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        self._test_wallet_notifications("test_notifications_different_wallet_when_relayed", daemon, wallet, False, False, False, True, 3)

    # Can generate notifications sending to different account
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_notifications_different_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        self._test_wallet_notifications("test_notifications_different_accounts", daemon, wallet, True, False, False, False, 0)

    # Can generate notifications sending to same account
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_notifications_same_account(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        self._test_wallet_notifications("test_notifications_same_account", daemon, wallet, True, True, False, False, 0)

    # Can generate notifications sweeping output to different account
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_notifications_different_account_sweep_output(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        self._test_wallet_notifications("test_notifications_different_account_sweep_output", daemon, wallet, True, False, True, False, 0)

    # Can generate notifications sweeping output to same account when relayed
    @pytest.mark.skipif(TestUtils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_notifications_same_account_sweep_output_when_relayed(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        self._test_wallet_notifications(
            "test_notifications_same_account_sweep_output_when_relayed", daemon, wallet, True, True, True, True, 0
        )

    #endregion

@pytest.mark.integration
class TestMoneroWalletFullListeners(FullWalletSupport, BaseTestMoneroWalletListeners):
    """Full wallet listeners integration tests."""

    @pytest.mark.xfail(reason=_SAME_ACCOUNT_NOTIFICATIONS, raises=AssertionError, strict=True)
    @override
    def test_notifications_same_account(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_same_account(daemon, wallet)

    @pytest.mark.xfail(reason=_SAME_ACCOUNT_NOTIFICATIONS, raises=AssertionError, strict=True)
    @override
    def test_notifications_same_account_sweep_output_when_relayed(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_same_account_sweep_output_when_relayed(daemon, wallet)


@pytest.mark.integration
class TestMoneroWalletRpcListeners(RpcWalletSupport, BaseTestMoneroWalletListeners):
    """Rpc wallet listeners integration tests."""

    @pytest.mark.xfail(reason=_SAME_ACCOUNT_NOTIFICATIONS, raises=AssertionError, strict=True)
    @override
    def test_notifications_same_account(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_same_account(daemon, wallet)

    @pytest.mark.xfail(reason=_SAME_ACCOUNT_NOTIFICATIONS, raises=AssertionError, strict=True)
    @override
    def test_notifications_same_account_sweep_output_when_relayed(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_same_account_sweep_output_when_relayed(daemon, wallet)


@pytest.mark.integration
class TestMoneroWalletLightListeners(LightWalletSupport, BaseTestMoneroWalletListeners):
    """Light wallet listeners integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysListeners(KeysWalletSupport, BaseTestMoneroWalletListeners):
    """Keys-only wallet listeners unit tests."""

    @pytest.mark.not_supported
    @override
    def test_stop_listening(self) -> None:
        return super().test_stop_listening()

    @pytest.mark.not_supported
    @override
    def test_create_and_receive(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_create_and_receive(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_notifications_different_wallet(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_different_wallet(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_notifications_different_wallet_when_relayed(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_different_wallet_when_relayed(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_notifications_different_accounts(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_different_accounts(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_notifications_same_account(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_same_account(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_notifications_different_account_sweep_output(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_different_account_sweep_output(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_notifications_same_account_sweep_output_when_relayed(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_notifications_same_account_sweep_output_when_relayed(daemon, wallet)
