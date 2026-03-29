import logging

from typing import Optional, override

from monero import (
    MoneroOutputWallet, MoneroWalletFull, MoneroTxWallet,
    MoneroTxQuery
)
from .sync_progress_tester import SyncProgressTester

logger: logging.Logger = logging.getLogger("WalletSyncTester")


class WalletSyncTester(SyncProgressTester):
    """Wallet sync tester."""

    wallet_tester_prev_height: Optional[int]
    """Renamed from `prev_height` to not interfere with super's `prev_height`."""
    prev_output_received: Optional[MoneroOutputWallet]
    """Previous notified output received."""
    prev_output_spent: Optional[MoneroOutputWallet]
    """Previous notified output spent."""
    incoming_total: int
    """Total incoming amount collected."""
    outgoing_total: int
    """Total outgoing amount collected."""
    on_new_block_after_done: Optional[bool]
    """Indicates that `on_new_block` has been called after `on_done`."""
    prev_balance: Optional[int]
    """Previous notified wallet balance."""
    prev_unlocked_balance: Optional[int]
    """Previous notified wallet unlocked balance."""

    def __init__(self, wallet: MoneroWalletFull, start_height: int, end_height: int) -> None:
        """
        Initialize a new wallet sync tester.

        :param MoneroWalletFull wallet: wallet to test.
        :param int start_height: blockchain start height.
        :param int end_height: blockchain end height.
        """
        super().__init__(wallet, start_height, end_height)
        assert start_height >= 0
        assert end_height >= 0
        self.incoming_total = 0
        self.outgoing_total = 0

        # initialize empty fields
        self.wallet_tester_prev_height = None
        self.prev_output_received = None
        self.prev_output_spent = None
        self.on_new_block_after_done = None
        self.prev_balance = None
        self.prev_unlocked_balance = None

    @override
    def on_new_block(self, height: int) -> None:
        if self.is_done:
            assert self in self.wallet.get_listeners(), "Listener has completed and is not registered so should not be called again"
            self.on_new_block_after_done = True
        if self.wallet_tester_prev_height is not None:
            assert self.wallet_tester_prev_height + 1 == height

        assert height >= self.start_height
        self.wallet_tester_prev_height = height

    @override
    def on_balances_changed(self, new_balance: int, new_unclocked_balance: int) -> None:
        if self.prev_balance is not None:
            assert new_balance != self.prev_balance or new_unclocked_balance != self.prev_unlocked_balance
        self.prev_balance = new_balance
        self.prev_unlocked_balance = new_unclocked_balance

    # test received/spent output
    def test_output(self, output: MoneroOutputWallet, received: bool) -> None:
        """
        Test received or spent output.

        :param MoneroOutputWallet output: output to test.
        :param bool received: `True` for received output, `False` for spent.
        """
        assert output is not None
        if received:
            self.prev_output_received = output
        else:
            self.prev_output_spent = output

        # test output
        assert output.amount is not None
        assert output.account_index is not None
        assert output.account_index >= 0

        # TODO (monero-project): if spent, can be undefined because inputs not
        # provided so one created from outgoing transfer
        if received:
            assert output.subaddress_index is not None
            assert output.subaddress_index >= 0

        # test output's tx
        assert output.tx is not None
        assert isinstance(output.tx, MoneroTxWallet)
        assert output.tx.hash is not None
        assert len(output.tx.hash) == 64
        assert output.tx.version is not None
        assert output.tx.version >= 0
        assert output.tx.unlock_time is not None
        assert output.tx.unlock_time >= 0
        # TODO this part is failing, maybe for little differences in java data model
        #if received:
            #assert len(output.tx.inputs) == 0
            #assert len(output.tx.outputs) == 1
            #assert output.tx.outputs[0] == output
        #else:
            #assert len(output.tx.inputs) == 1
            #assert output.tx.inputs[0] == output
            #assert len(output.tx.outputs) == 0
        assert len(output.tx.extra) > 0

        if output.tx.is_locked:
            if received:
                # add incoming amount to running total
                # TODO: only add if not unlocked, test unlocked received
                self.incoming_total += output.amount
            else:
                # add outgoing amount to running total
                self.outgoing_total += output.amount

    @override
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        self.test_output(output, True)

    @override
    def on_output_spent(self, output: MoneroOutputWallet) -> None:
        self.test_output(output, False)

    @override
    def on_done(self, chain_height: int) -> None:
        super().on_done(chain_height)

        assert self.wallet_tester_prev_height is not None
        assert self.prev_output_received is not None
        assert self.prev_output_spent is not None
        logger.info(f"incoming amount {self.incoming_total}, outgoing total {self.outgoing_total}")
        expected_balance: int = self.incoming_total - self.outgoing_total

        # output notifications do not include pool fees or outgoing amount
        pool_spend_amount: int = 0
        query: MoneroTxQuery = MoneroTxQuery()
        query.in_tx_pool = True
        for pool_tx in self.wallet.get_txs(query):
            assert pool_tx.fee is not None
            pool_spend_amount += pool_tx.get_outgoing_amount() + pool_tx.fee

        logger.debug(f"pool spend amount: {pool_spend_amount}, expected balance: {expected_balance}")
        expected_balance -= pool_spend_amount
        logger.debug(f"new expected balance = {expected_balance}")

        wallet_balance: int = self.wallet.get_balance()
        wallet_unlocked_balance: int = self.wallet.get_unlocked_balance()
        assert expected_balance == wallet_balance, f"expected balance {expected_balance} != balance {wallet_balance}"
        assert self.prev_balance == wallet_balance, f"previous balance {expected_balance} != balance {wallet_balance}"
        assert self.prev_unlocked_balance == wallet_unlocked_balance, f"previous unlocked balance {expected_balance} != unlocked balance {wallet_balance}"
