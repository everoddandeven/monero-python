from __future__ import annotations

import logging
from time import monotonic, sleep

import pytest
from monero import MoneroDaemonRpc, MoneroTxConfig, MoneroTxWallet, MoneroWallet, MoneroWalletConfig
from typing_extensions import override

from utils import MiningUtils, TestUtils, TxWalletUtils, WalletNotificationCollector
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletListeners")


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
            logger.debug(f"Closing receiver wallet...")
            self._close_wallet(receiver)
            logger.debug(f"Closed receiver wallet")
            MiningUtils.try_stop_mining()


@pytest.mark.integration
class TestMoneroWalletFullListeners(FullWalletSupport, BaseTestMoneroWalletListeners):
    """Full wallet listeners integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcListeners(RpcWalletSupport, BaseTestMoneroWalletListeners):
    """Rpc wallet listeners integration tests."""


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
