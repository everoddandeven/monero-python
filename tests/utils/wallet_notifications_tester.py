from __future__ import annotations

import logging
from time import monotonic
from typing import Callable, Optional

from monero import (
    MoneroDaemonRpc, MoneroDestination, MoneroOutputQuery, MoneroOutputWallet,
    MoneroTxConfig, MoneroTxQuery, MoneroTxWallet, MoneroWallet, MoneroWalletRpc
)

from .context import TxContext
from .gen_utils import GenUtils
from .mining_utils import MiningUtils
from .test_utils import TestUtils
from .tx_wallet_utils import TxWalletUtils
from .wallet_notification_collector import WalletNotificationCollector

logger: logging.Logger = logging.getLogger("WalletNotificationsTester")


class WalletNotificationsTester:
    """Sends funds from a wallet and tests the notifications of the sender and of the receiver, until the funds unlock.

    The issues are collected as the test runs: the ones that start with `ERROR:` fail the test, the `WARNING:` ones are only logged.
    """

    NUM_BLOCKS_LOCKED: int = 10
    """Number of blocks for which received funds are locked."""
    MAX_POLL_TIME_MS: int = 5000
    """Maximum time granted for a wallet to poll."""

    sender: MoneroWallet
    """Wallet that sends the funds."""
    receiver: MoneroWallet
    """Wallet that receives the funds (the sender itself when sending to the same wallet)."""
    daemon: MoneroDaemonRpc
    """Daemon of the test network."""
    same_account: bool
    """Send to the account the funds come from (account 0)."""
    sweep_output: bool
    """Sweep an output instead of sending to multiple accounts."""
    create_then_relay: bool
    """Create the tx without relaying it, then relay it."""
    unlock_delay: int
    """Blocks to wait, after the last height before sending, before testing the unlock notifications."""
    issues: list[str]
    """Issues found while testing."""

    _sender_collector: WalletNotificationCollector
    _receiver_collector: WalletNotificationCollector
    _pending_checks: list[tuple[float, Callable[[], None]]]
    _started_mining: bool
    """`True` if the tester started mining, so it stops it at the end."""
    """Checks to run when their time comes: the wallets get some sync periods to notify what happened."""

    def __init__(
        self, sender: MoneroWallet, receiver: MoneroWallet, daemon: MoneroDaemonRpc,
        same_account: bool, sweep_output: bool, create_then_relay: bool, unlock_delay: int
    ) -> None:
        """Initialize a new wallet notifications tester.

        :param MoneroWallet sender: wallet that sends the funds.
        :param MoneroWallet receiver: wallet that receives the funds, `sender` to send to the same wallet.
        :param MoneroDaemonRpc daemon: daemon of the test network.
        :param bool same_account: send to the account the funds come from.
        :param bool sweep_output: sweep an output instead of sending to multiple accounts.
        :param bool create_then_relay: create the tx without relaying it, then relay it.
        :param int unlock_delay: blocks to wait before testing the unlock notifications.
        """
        self.sender = sender
        self.receiver = receiver
        self.daemon = daemon
        self.same_account = same_account
        self.sweep_output = sweep_output
        self.create_then_relay = create_then_relay
        self.unlock_delay = unlock_delay
        self.issues = []
        self._sender_collector = WalletNotificationCollector()
        self._receiver_collector = WalletNotificationCollector()
        self._pending_checks = []
        self._started_mining = False

    @property
    def same_wallet(self) -> bool:
        """`True` if the funds are sent to the same wallet."""
        return self.sender is self.receiver

    def test(self, test_name: str) -> None:
        """Run the test and fail if an issue is an error.

        :param str test_name: name of the test, for the report of the issues.
        """
        issues: list[str] = self.run()
        if len(issues) == 0:
            return
        msg: str = (
            f"{test_name}(same_wallet={self.same_wallet}, same_account={self.same_account}, sweep_output={self.sweep_output}, "
            f"create_then_relay={self.create_then_relay}) generated {len(issues)} issues:\n{self.issues_to_str(issues)}"
        )
        logger.warning(msg)
        assert "ERROR:" not in msg, msg

    def run(self) -> list[str]:
        """Send the funds and test the notifications until they unlock.

        :returns list[str]: issues found.
        """
        try:
            self._run()
        finally:
            # run the checks that are left, also when the test fails, then stop everything
            try:
                self._run_pending_checks(True)
            finally:
                # like monero-java's StartMining.stopMining(), it does not ask the daemon when the tester did not start mining: a test
                # that fails before, or that is not supported (the keys-only wallet), may have no daemon (the unit tests of the CI)
                if self._started_mining:
                    self._stop_mining()
                self._stop_listening(self.sender, self._sender_collector)
                self._stop_listening(self.receiver, self._receiver_collector)

        # errors raised inside the listeners
        for error in self._sender_collector.errors:
            self.issues.append(f"ERROR: sender listener raised: {error}")
        for error in self._receiver_collector.errors:
            self.issues.append(f"ERROR: receiver listener raised: {error}")

        return self.issues

    def _run(self) -> None:
        sender: MoneroWallet = self.sender
        receiver: MoneroWallet = self.receiver
        sender_collector: WalletNotificationCollector = self._sender_collector
        receiver_collector: WalletNotificationCollector = self._receiver_collector
        issues: list[str] = self.issues

        # create receiver accounts if necessary
        num_accounts: int = len(receiver.get_accounts())
        for _ in range(4 - num_accounts):
            receiver.create_account()

        # wait for unlocked funds in source account
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(sender)
        TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(sender, 0, None, TxWalletUtils.MAX_FEE * 10)

        # include the last mined blocks before measuring balance changes
        self._stop_mining()
        sender.sync()
        if not self.same_wallet:
            receiver.sync()

        # get balances to compare after sending
        sender_balance_before: int = sender.get_balance()
        sender_unlocked_balance_before: int = sender.get_unlocked_balance()
        receiver_balance_before: int = receiver.get_balance()
        receiver_unlocked_balance_before: int = receiver.get_unlocked_balance()
        last_height: int = self.daemon.get_height()

        # start collecting notifications from sender and receiver
        sender.add_listener(sender_collector)
        GenUtils.wait_for(TestUtils.SYNC_PERIOD_IN_MS // 2)
        receiver.add_listener(receiver_collector)

        # send funds
        ctx: TxContext = TxContext()
        ctx.wallet = sender
        ctx.is_send_response = True
        destination_accounts: list[int]
        if self.same_account:
            destination_accounts = [0] if self.sweep_output else [0, 1, 2]
        else:
            destination_accounts = [1] if self.sweep_output else [1, 2, 3]
        expected_outputs: list[MoneroOutputWallet] = []
        sender_tx: MoneroTxWallet
        config: MoneroTxConfig = MoneroTxConfig()
        config.relay = not self.create_then_relay
        if self.sweep_output:
            ctx.is_sweep_response = True
            ctx.is_sweep_output_response = True
            output_query: MoneroOutputQuery = MoneroOutputQuery()
            output_query.is_spent = False
            output_query.account_index = 0
            output_query.min_amount = TxWalletUtils.MAX_FEE * 5
            unlocked_query: MoneroTxQuery = MoneroTxQuery()
            unlocked_query.is_locked = False
            output_query.set_tx_query(unlocked_query, True)
            outputs: list[MoneroOutputWallet] = sender.get_outputs(output_query)
            if len(outputs) == 0:
                issues.append("ERROR: No outputs available to sweep from account 0")
                return
            assert outputs[0].key_image is not None
            config.address = receiver.get_address(destination_accounts[0], 0)
            config.key_image = outputs[0].key_image.hex
            sender_tx = sender.sweep_output(config)
            assert sender_tx.outgoing_transfer is not None
            swept_amount: int | None = sender_tx.outgoing_transfer.destinations[0].amount
            assert swept_amount is not None
            expected_outputs.append(self._output(swept_amount, destination_accounts[0], 0))
        else:
            config.account_index = 0
            destinations: list[MoneroDestination] = []
            for destination_account in destination_accounts:
                # TODO: send and check random amounts?
                destinations.append(MoneroDestination(receiver.get_address(destination_account, 0), TxWalletUtils.MAX_FEE))
                expected_outputs.append(self._output(TxWalletUtils.MAX_FEE, destination_account, 0))
            config.destinations = destinations
            sender_tx = sender.create_tx(config)
        ctx.config = config
        if self.create_then_relay:
            sender.relay_tx(sender_tx)

        # start timer to measure end of sync period
        start_time: float = monotonic()

        # test send tx
        TxWalletUtils.test_tx_wallet(sender_tx, ctx)
        tx_hash: str | None = sender_tx.hash
        assert tx_hash is not None

        # test sender after sending
        tx_outputs_query: MoneroOutputQuery = self._outputs_query(tx_hash)  # query for outputs from sender tx
        if self.same_wallet:
            incoming_amount: int = sender_tx.get_incoming_amount()
            if incoming_amount == 0:
                issues.append("WARNING: sender tx incoming amount is 0 when sent to same wallet")
            else:
                assert sender_tx.fee is not None
                if incoming_amount != sender_tx.get_outgoing_amount() - sender_tx.fee:
                    issues.append("WARNING: sender tx incoming amount != outgoing amount - fee when sent to same wallet")
        elif sender_tx.get_incoming_amount() != 0:
            issues.append("ERROR: tx incoming amount should be 0")
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = tx_hash
        tx_query.include_outputs = True
        sender_tx = sender.get_txs(tx_query)[0]
        assert sender_tx.fee is not None
        sender_balance: int = sender.get_balance()
        expected_sender_balance: int = (
            sender_balance_before - sender_tx.fee - sender_tx.get_outgoing_amount() + sender_tx.get_incoming_amount()
        )
        if sender_balance != expected_sender_balance:
            issues.append(
                f"ERROR: sender balance after send != balance before - tx fee - outgoing amount + incoming amount ({sender_balance} != "
                f"{sender_balance_before} - {sender_tx.fee} - {sender_tx.get_outgoing_amount()} + {sender_tx.get_incoming_amount()})"
            )
        sender_unlocked_balance_after: int = sender.get_unlocked_balance()
        if sender_unlocked_balance_after >= sender_unlocked_balance_before:
            issues.append(
                f"ERROR: sender unlocked balance should have decreased after sending (before: {sender_unlocked_balance_before}, "
                f"after: {sender_unlocked_balance_after})"
            )
        self._test_last_balance_notification(sender, sender_collector, "sender", "after sending", "did not notify balance change after sending")
        # TODO monero-cpp: the rpc wallet does not notify the outputs of the txs in the pool (see the xfail marks in test_listeners.py)
        if len(sender_collector.get_outputs_spent(tx_outputs_query)) == 0:
            issues.append("ERROR: sender did not announce unconfirmed spent output")

        # test receiver after a sync period
        GenUtils.wait_for(self._remaining_sync_period_ms(start_time))
        start_time = monotonic()  # reset timer
        receiver_tx: MoneroTxWallet | None = receiver.get_tx(tx_hash)
        assert receiver_tx is not None
        if sender_tx.get_outgoing_amount() != receiver_tx.get_incoming_amount() and self.same_account:
            issues.append(
                "WARNING: sender tx outgoing amount != receiver tx incoming amount when sent to same account "
                f"({sender_tx.get_outgoing_amount()} != {receiver_tx.get_incoming_amount()})"
            )
        receiver_fee: int = 0
        if self.same_wallet:
            assert receiver_tx.fee is not None
            receiver_fee = receiver_tx.fee
        receiver_balance: int = receiver.get_balance()
        expected_receiver_balance: int = (
            receiver_balance_before + receiver_tx.get_incoming_amount() - receiver_tx.get_outgoing_amount() - receiver_fee
        )
        if receiver_balance != expected_receiver_balance:
            level: str = "WARNING" if self.same_account else "ERROR"
            suffix: str = " when sent to same account" if self.same_account else ""
            issues.append(
                f"{level}: after sending, receiver balance != balance before + incoming amount - outgoing amount - tx fee{suffix} "
                f"({receiver_balance} != {receiver_balance_before} + {receiver_tx.get_incoming_amount()} - "
                f"{receiver_tx.get_outgoing_amount()} - {receiver_fee})"
            )
        if not self.same_wallet and receiver.get_unlocked_balance() != receiver_unlocked_balance_before:
            issues.append("ERROR: receiver unlocked balance should not have changed after sending")
        self._test_last_balance_notification(
            receiver, receiver_collector, "receiver", "after funds received", "did not notify balance change when funds received"
        )
        if len(receiver_collector.get_outputs_received(tx_outputs_query)) == 0:
            issues.append("ERROR: receiver did not announce unconfirmed received output")
        else:
            for output in self.get_missing_outputs(expected_outputs, receiver_collector.get_outputs_received(tx_outputs_query), True):
                issues.append(f"ERROR: receiver did not announce received output for {self._output_str(output)}")

        # mine until the funds unlock
        if not MiningUtils.is_mining():
            MiningUtils.start_mining()
        self._started_mining = True

        # loop every sync period until unlock tested
        expected_unlock_height: int = last_height + self.unlock_delay
        confirm_height: Optional[int] = None
        while True:
            self._run_pending_checks(False)

            # test height notifications
            height: int = self.daemon.get_height()
            if height > last_height:
                self._schedule(self._block_notifications_check(last_height, height))
                last_height = height

            # check if tx confirmed
            if confirm_height is None:

                # get updated tx
                tx: MoneroTxWallet | None = receiver.get_tx(tx_hash)
                assert tx is not None

                # break if tx fails
                if tx.is_failed:
                    issues.append("ERROR: tx failed in tx pool")
                    break

                # test confirm notifications
                if tx.is_confirmed:
                    confirm_height = tx.get_height()
                    assert confirm_height is not None
                    expected_unlock_height = max(confirm_height + self.NUM_BLOCKS_LOCKED, expected_unlock_height)  # exact unlock time known
                    self._schedule(self._confirmed_notifications_check(tx, tx_hash, expected_outputs))

            # otherwise test unlock notifications
            elif height >= expected_unlock_height:
                # freeze the chain so unrelated unlocks cannot change balances before the final checks
                self._stop_mining()
                self._schedule(self._unlocked_notifications_check(tx_hash, expected_outputs))
                break

            # wait for end of sync period
            GenUtils.wait_for(self._remaining_sync_period_ms(start_time))
            start_time = monotonic()  # reset timer

        # wait for the pending checks
        self._run_pending_checks(True)

        # test notified outputs
        for output in sender_collector.get_outputs_spent(tx_outputs_query):
            self.test_notified_output(output, True, issues)
        for output in sender_collector.get_outputs_received(tx_outputs_query):
            self.test_notified_output(output, False, issues)
        for output in receiver_collector.get_outputs_spent(tx_outputs_query):
            self.test_notified_output(output, True, issues)
        for output in receiver_collector.get_outputs_received(tx_outputs_query):
            self.test_notified_output(output, False, issues)

    #region Checks

    def _block_notifications_check(self, start_height: int, end_height: int) -> Callable[[], None]:
        """The check that the wallets announced the blocks from `start_height` to `end_height` (excluded)."""
        def check() -> None:
            for i in range(start_height, end_height):
                if i not in self._sender_collector.block_notifications:
                    self.issues.append(f"ERROR: sender did not announce block {i}")
                if i not in self._receiver_collector.block_notifications:
                    self.issues.append(f"ERROR: receiver did not announce block {i}")
        return check

    def _confirmed_notifications_check(
        self, tx: MoneroTxWallet, tx_hash: str, expected_outputs: list[MoneroOutputWallet]
    ) -> Callable[[], None]:
        """The check of the notifications of the outputs of the tx when it is confirmed."""
        def check() -> None:
            confirmed_query: MoneroOutputQuery = self._outputs_query(tx_hash, is_confirmed=True, is_locked=True)
            sender_collector: WalletNotificationCollector = self._sender_collector
            receiver_collector: WalletNotificationCollector = self._receiver_collector
            if len(sender_collector.get_outputs_spent(confirmed_query)) == 0:
                self.issues.append("ERROR: sender did not announce confirmed spent output")  # TODO: test amount
            received: list[MoneroOutputWallet] = receiver_collector.get_outputs_received(confirmed_query)
            if len(received) == 0:
                self.issues.append("ERROR: receiver did not announce confirmed received output")
            else:
                for output in self.get_missing_outputs(expected_outputs, received, True):
                    self.issues.append(f"ERROR: receiver did not announce confirmed received output for {self._output_str(output)}")

            # if same wallet, net amount spent = tx fee = outputs spent - outputs received
            if self.same_wallet:
                net_amount: int = 0
                for output_spent in sender_collector.get_outputs_spent(confirmed_query):
                    assert output_spent.amount is not None
                    net_amount += output_spent.amount
                for output_received in sender_collector.get_outputs_received(confirmed_query):
                    assert output_received.amount is not None
                    net_amount -= output_received.amount
                if tx.fee != net_amount:
                    if self.same_account:
                        self.issues.append(f"WARNING: net output amount != tx fee when funds sent to same account: {net_amount} vs {tx.fee}")
                    elif isinstance(self.sender, MoneroWalletRpc):
                        # TODO (monero-project): open issue to provide tx inputs
                        self.issues.append(
                            "WARNING: net output amount != tx fee when funds sent to same wallet because monero-wallet-rpc does not "
                            f"provide tx inputs: {net_amount} vs {tx.fee}"
                        )
                    else:
                        self.issues.append(f"ERROR: net output amount must equal tx fee when funds sent to same wallet: {net_amount} vs {tx.fee}")
        return check

    def _unlocked_notifications_check(self, tx_hash: str, expected_outputs: list[MoneroOutputWallet]) -> Callable[[], None]:
        """The check of the notifications of the outputs and of the balances when the funds unlock."""
        def check() -> None:
            unlocked_query: MoneroOutputQuery = self._outputs_query(tx_hash, is_locked=False)
            if len(self._sender_collector.get_outputs_spent(unlocked_query)) == 0:
                self.issues.append("ERROR: sender did not announce unlocked spent output")  # TODO: test amount?
            received: list[MoneroOutputWallet] = self._receiver_collector.get_outputs_received(unlocked_query)
            for output in self.get_missing_outputs(expected_outputs, received, True):
                self.issues.append(f"ERROR: receiver did not announce unlocked received output for {self._output_str(output)}")
            if not self.same_wallet and self.receiver.get_balance() != self.receiver.get_unlocked_balance():
                self.issues.append("ERROR: receiver balance != unlocked balance after funds unlocked")
            self._test_last_balance_notification(
                self.sender, self._sender_collector, "sender", "after funds unlocked", "did not announce any balance notifications"
            )
            self._test_last_balance_notification(
                self.receiver, self._receiver_collector, "receiver", "after funds unlocked", "did not announce any balance notifications"
            )
        return check

    def _test_last_balance_notification(
        self, wallet: MoneroWallet, collector: WalletNotificationCollector, role: str, when: str, missing_msg: str
    ) -> None:
        """Test that the last notified balances are the ones of the wallet."""
        if len(collector.balance_notifications) == 0:
            self.issues.append(f"ERROR: {role} {missing_msg}")
            return
        last_balance, last_unlocked_balance = collector.balance_notifications[-1]
        balance: int = wallet.get_balance()
        unlocked_balance: int = wallet.get_unlocked_balance()
        if balance != last_balance:
            self.issues.append(f"ERROR: {role} balance != last notified balance {when} ({balance} != {last_balance})")
        if unlocked_balance != last_unlocked_balance:
            self.issues.append(
                f"ERROR: {role} unlocked balance != last notified unlocked balance {when} ({unlocked_balance} != {last_unlocked_balance})"
            )

    @classmethod
    def test_notified_output(cls, output: MoneroOutputWallet, is_tx_input: bool, issues: list[str]) -> None:
        """Test an output notified by a wallet.

        :param MoneroOutputWallet output: notified output.
        :param bool is_tx_input: `True` if the output was notified as spent.
        :param list[str] issues: collects the issues found.
        """
        # test tx link
        assert output.tx is not None
        if is_tx_input:
            assert output in output.tx.inputs
        else:
            assert output in output.tx.outputs

        # test output values
        GenUtils.test_unsigned_big_integer(output.amount)
        state: str = cls.get_output_state(output)
        if output.account_index is not None:
            assert output.account_index >= 0
        elif is_tx_input:
            # TODO (monero-project): account index not provided when output swept by key image.  could retrieve it but slows tx creation significantly
            issues.append(f"WARNING: notification of {state} spent output missing account index")
        else:
            issues.append(f"ERROR: notification of {state} received output missing account index")
        if output.subaddress_index is not None:
            assert output.subaddress_index >= 0
        elif is_tx_input:
            # TODO (monero-project): because inputs are not provided, creating fake input from outgoing transfer, which can be sourced from
            # multiple subaddress indices, whereas an output can only come from one subaddress index; need to provide tx inputs to resolve this
            issues.append(f"WARNING: notification of {state} spent output missing subaddress index")
        else:
            issues.append(f"ERROR: notification of {state} received output missing subaddress index")

    #endregion

    #region Utils

    @staticmethod
    def get_output_state(output: MoneroOutputWallet) -> str:
        """Get the state of a notified output.

        :param MoneroOutputWallet output: notified output.
        :returns str: `unlocked`, `confirmed` or `unconfirmed`.
        """
        assert output.tx is not None
        if output.tx.is_locked is False:
            return "unlocked"
        if output.tx.is_confirmed is True:
            return "confirmed"
        if output.tx.is_confirmed is False:
            return "unconfirmed"
        raise Exception(f"Unknown output state: {output.serialize()}")

    @staticmethod
    def get_missing_outputs(
        expected_outputs: list[MoneroOutputWallet], actual_outputs: list[MoneroOutputWallet], match_subaddress: bool
    ) -> list[MoneroOutputWallet]:
        """Get the expected outputs that are not in the actual ones, matching each actual output once.

        :param list[MoneroOutputWallet] expected_outputs: expected outputs.
        :param list[MoneroOutputWallet] actual_outputs: actual outputs.
        :param bool match_subaddress: match also the account and subaddress indices.
        :returns list[MoneroOutputWallet]: expected outputs not found.
        """
        missing: list[MoneroOutputWallet] = []
        used: list[int] = []
        for expected_output in expected_outputs:
            found: bool = False
            for i, actual_output in enumerate(actual_outputs):
                if i in used:
                    continue
                if actual_output.amount == expected_output.amount and (
                    not match_subaddress or (
                        actual_output.account_index == expected_output.account_index
                        and actual_output.subaddress_index == expected_output.subaddress_index
                    )
                ):
                    used.append(i)
                    found = True
                    break
            if not found:
                missing.append(expected_output)
        return missing

    @staticmethod
    def issues_to_str(issues: list[str]) -> str:
        """Numbered list of issues, one per line.

        :param list[str] issues: issues.
        :returns str: the issues, one per line.
        """
        return "\n".join(f"{i + 1}: {issue}" for i, issue in enumerate(issues))

    @staticmethod
    def _output(amount: int, account_index: int, subaddress_index: int) -> MoneroOutputWallet:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = amount
        output.account_index = account_index
        output.subaddress_index = subaddress_index
        return output

    @staticmethod
    def _output_str(output: MoneroOutputWallet) -> str:
        return f"amount {output.amount} to subaddress [{output.account_index}, {output.subaddress_index}]"

    @staticmethod
    def _outputs_query(tx_hash: str, is_confirmed: Optional[bool] = None, is_locked: Optional[bool] = None) -> MoneroOutputQuery:
        """Query for the outputs of the tx with `tx_hash`."""
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = tx_hash
        tx_query.is_confirmed = is_confirmed
        tx_query.is_locked = is_locked
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.set_tx_query(tx_query, True)
        return query

    @staticmethod
    def _remaining_sync_period_ms(start_time: float) -> int:
        """Milliseconds left of the sync period started at `start_time`."""
        return max(0, int(TestUtils.SYNC_PERIOD_IN_MS - (monotonic() - start_time) * 1000))

    def _schedule(self, check: Callable[[], None]) -> None:
        """Run `check` after 2 sync periods and the poll time, the time the wallets have to notify what happened."""
        delay_s: float = (TestUtils.SYNC_PERIOD_IN_MS * 2 + self.MAX_POLL_TIME_MS) / 1000
        self._pending_checks.append((monotonic() + delay_s, check))

    def _run_pending_checks(self, wait: bool) -> None:
        """Run the checks whose time has come, or all of them, waiting for each one, if `wait`."""
        while len(self._pending_checks) > 0:
            due_time, check = self._pending_checks[0]
            remaining_ms: int = int((due_time - monotonic()) * 1000)
            if remaining_ms > 0:
                if not wait:
                    return
                GenUtils.wait_for(remaining_ms)
            self._pending_checks.pop(0)
            check()

    @staticmethod
    def _stop_mining() -> None:
        """Stop mining, if the daemon is mining."""
        if MiningUtils.is_mining():
            MiningUtils.stop_mining()

    @staticmethod
    def _stop_listening(wallet: MoneroWallet, collector: WalletNotificationCollector) -> None:
        """Remove the collector from the wallet, if it was added, and stop it."""
        try:
            wallet.remove_listener(collector)
        except Exception as e:
            logger.debug(f"Listener not removed: {e}")
        collector.listening = False

    #endregion
