from __future__ import annotations

import logging
from typing import Optional

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroFeeEstimate,
    MoneroIntegratedAddress,
    MoneroSubaddress,
    MoneroTxConfig,
    MoneroTxPriority,
    MoneroTxQuery,
    MoneroTxWallet,
    MoneroUtils,
    MoneroWallet,
    MoneroWalletConfig,
)
from typing_extensions import override

from utils import TestUtils, TxWalletUtils, WalletSendUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletSend")


class BaseTestMoneroWalletSend(BaseTestMoneroWallet):
    """Common wallet send tests."""

    # Validates inputs when sending funds
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5, only_rerun=[])
    def test_validate_inputs_sending_funds(self, wallet: MoneroWallet) -> None:
        # try sending with invalid address
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.address = "my invalid address"
        tx_config.account_index = 0
        tx_config.amount = TxWalletUtils.MAX_FEE
        with pytest.raises(Exception) as exc_info:
            wallet.create_tx(tx_config)
        assert str(exc_info.value) == "Invalid destination address"

    # Can send to self
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_to_self(self, wallet: MoneroWallet) -> None:
        # wait for txs to confirm and for sufficient unlocked balance
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        amount: int = TxWalletUtils.MAX_FEE * 3
        TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(wallet, 0, None, amount)

        # collect sender balances before
        balance1: int = wallet.get_balance()
        unlocked_balance1: int = wallet.get_unlocked_balance()

        # test error sending funds to self with integrated subaddress
        # TODO (monero-project): sending funds to self
        # with integrated subaddress throws error: https://github.com/monero-project/monero/issues/8380

        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = 0
        subaddress: MoneroSubaddress = wallet.get_subaddress(0, 1)
        assert subaddress.address is not None
        address: str = subaddress.address
        tx_config.address = MoneroUtils.get_integrated_address(TestUtils.NETWORK_TYPE, address, '').integrated_address
        tx_config.amount = amount
        tx_config.relay = True
        with pytest.raises(Exception, match="Total received by"):
            wallet.create_tx(tx_config)

        # send funds to self
        tx_config = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.address = wallet.get_integrated_address().integrated_address
        tx_config.amount = amount
        tx_config.relay = True

        tx: MoneroTxWallet = wallet.create_tx(tx_config)

        # test balances after
        balance2: int = wallet.get_balance()
        unlocked_balance2: int = wallet.get_unlocked_balance()

        # unlocked balance should decrease
        assert unlocked_balance2 < unlocked_balance1
        assert tx.fee is not None
        expected_balance: int = balance1 - tx.fee
        assert expected_balance == balance2, "Balance after send was not balance before - fee"

    # Can send to external address
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_to_external(self, wallet: MoneroWallet) -> None:
        recipient: Optional[MoneroWallet] = None
        try:
            # wait for txs to confirm and for sufficient unlocked balance
            TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
            amount: int = TxWalletUtils.MAX_FEE * 3
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
            expected_balance: int = balance1 - tx.get_outgoing_amount() - tx.fee
            assert expected_balance == balance2, "Balance after send was not balance before - net tx amount - fee (5 - 1 != 4 test)"

            tx_query: MoneroTxQuery = MoneroTxQuery()
            tx_query.is_confirmed = False
            txs: list[MoneroTxWallet] = wallet.get_txs(tx_query)
            assert len(txs) > 0

            # test recipient balance after
            recipient.sync()
            assert amount == recipient.get_balance()

        finally:
            if recipient is not None:
                self._close_wallet(recipient)

    # Can send to multiple subaddresses in a single transaction
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_to_multiple(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_multiple(wallet, 5, 3, False)

    # Can send to multiple addresses in split transactions
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_to_multiple_split(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_multiple(wallet, 3, 15, True)

    # Can send dust to multiple addresses in split transactions
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_dust_to_multiple_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        estimate: MoneroFeeEstimate = daemon.get_fee_estimate()
        assert estimate.fee is not None
        dust_amount: int = int(estimate.fee / 2)
        WalletSendUtils.test_send_to_multiple(wallet, 5, 3, True, dust_amount)

    # Can subtract fees from destinations
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_subtract_fee_from(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_multiple(wallet, 5, 3, False, None, True)

    # Cannot subtract fees from destinations in split transactions
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_subtract_fee_from_split(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_multiple(wallet, 3, 15, True, None, True)

    # Can send from multiple subaddresses in a single transaction
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_from_subaddresses(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_from_multiple(wallet, None)

    # Can send from multiple subaddresses in split transactions
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_from_subaddresses_split(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_from_multiple(wallet, True)

    # Can send to an address in a single transaction
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_single(wallet, False)

    # Can send to an address in a single transaction with a payment id
    # NOTE this test will be invalid when payment hashes are fully removed
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_with_payment_id(self, wallet: MoneroWallet) -> None:
        integrated_address: MoneroIntegratedAddress = wallet.get_integrated_address()
        assert integrated_address.payment_id is not None
        payment_id: str = integrated_address.payment_id
        msg = "Standalone payment IDs are obsolete. Use subaddresses or integrated addresses instead"
        with pytest.raises(Exception) as exc_info:
            WalletSendUtils.test_send_to_single(wallet, False, None, f"{payment_id}{payment_id}{payment_id}")
        assert str(exc_info.value) == msg

    # Can send to an address with split transactions
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_send_split(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_single(wallet, True)

    # Can create then relay a transaction to send to a single address
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_create_then_relay(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_single(wallet, False, False)

    # Can create then relay split transactions to send to a single address
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_create_then_relay_split(self, wallet: MoneroWallet) -> None:
        WalletSendUtils.test_send_to_single(wallet, True, False)

    # Can get the default fee priority
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_default_fee_priority(self, wallet: MoneroWallet) -> None:
        default_priority: MoneroTxPriority = wallet.get_default_fee_priority()
        assert int(default_priority) > 0


@pytest.mark.integration
class TestMoneroWalletFullSend(FullWalletSupport, BaseTestMoneroWalletSend):
    """Full wallet send integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcSend(RpcWalletSupport, BaseTestMoneroWalletSend):
    """Rpc wallet send integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysSend(KeysWalletSupport, BaseTestMoneroWalletSend):
    """Keys-only wallet send unit tests."""

    @pytest.mark.not_supported
    @override
    def test_send(self, wallet: MoneroWallet) -> None:
        return super().test_send(wallet)

    @pytest.mark.not_implemented
    @override
    def test_send_with_payment_id(self, wallet: MoneroWallet) -> None:
        return super().test_send_with_payment_id(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_then_relay(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_then_relay_split(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_validate_inputs_sending_funds(self, wallet: MoneroWallet) -> None:
        return super().test_validate_inputs_sending_funds(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_to_self(self, wallet: MoneroWallet) -> None:
        return super().test_send_to_self(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_to_external(self, wallet: MoneroWallet) -> None:
        return super().test_send_to_external(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_default_fee_priority(self, wallet: MoneroWallet) -> None:
        return super().test_get_default_fee_priority(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_from_subaddresses(self, wallet: MoneroWallet) -> None:
        return super().test_send_from_subaddresses(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_from_subaddresses_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_from_subaddresses_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_to_multiple(self, wallet: MoneroWallet) -> None:
        return super().test_send_to_multiple(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_to_multiple_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_to_multiple_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_send_dust_to_multiple_split(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_send_dust_to_multiple_split(daemon, wallet)

    @pytest.mark.not_supported
    @override
    def test_subtract_fee_from(self, wallet: MoneroWallet) -> None:
        return super().test_subtract_fee_from(wallet)

    @pytest.mark.not_supported
    @override
    def test_subtract_fee_from_split(self, wallet: MoneroWallet) -> None:
        return super().test_subtract_fee_from_split(wallet)
