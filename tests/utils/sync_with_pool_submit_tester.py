import logging

from monero import (
    MoneroWallet, MoneroTxConfig, MoneroTxWallet,
    MoneroSubmitTxResult, MoneroDaemon
)

from .assert_utils import AssertUtils
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("SyncWithPoolSubmitTester")


class SyncWithPoolSubmitTester:
    """Test wallet capability to sync transactions in the pool."""

    daemon: MoneroDaemon
    """Daemon instance."""
    wallet: MoneroWallet
    """Test wallet instance."""
    config: MoneroTxConfig
    """Transaction test configuration."""
    balance_before: int
    """Wallet balance before test."""
    unlocked_balance_before: int
    """Wallet unlocked balance before test."""
    txs_before: list[MoneroTxWallet]
    """Wallet transactions before running test."""
    run_failing_code: bool
    """Run failing monero core code."""

    def __init__(self, daemon: MoneroDaemon, wallet: MoneroWallet, config: MoneroTxConfig, run_failing_core_code: bool = False) -> None:
        """
        Initialize a new sync with poll submit tester.

        :param MoneroDaemon daemon: daemon test instance.
        :param MoneroWallet wallet: wallet test instance.
        :param MoneroTxConfig config: transaction config.
        """
        self.daemon = daemon
        self.wallet = wallet
        self.config = config
        self.balance_before = 0
        self.unlocked_balance_before = 0
        self.txs_before = []
        self.run_failing_code = run_failing_core_code

    def run_failing_core_code(self, config_no_relay: MoneroTxConfig) -> None:
        """
        TODO monero-project this code fails wich indicates issues.
        TODO monero-project sync txs from pool.

        :param MoneroTxConfig config_no_relay: Non-relay tx config.
        """
        if not self.run_failing_code:
            return

        # wallet balances should change
        assert self.balance_before != self.wallet.get_balance(), "Wallet balance should revert to original after flushing tx from pool without relaying"
        # TODO: test exact amounts, maybe in ux test
        assert self.unlocked_balance_before != self.wallet.get_unlocked_balance(), "Wallet unlocked balance should revert to original after flushing tx from pool without relaying"

        # create tx using same config which is no longer double spend
        tx2: MoneroTxWallet = self.wallet.create_tx(config_no_relay)
        assert tx2.hash is not None
        assert tx2.full_hex is not None
        result2: MoneroSubmitTxResult = self.daemon.submit_tx_hex(tx2.full_hex)

        # test result and flush on finally
        try:
            if result2.is_double_spend:
                raise Exception(f"Wallet created double spend transaction after syncing with the pool: {result2}")

            assert result2.is_good
            self.wallet.sync()
            # wallet is aware of tx2
            fetched = self.wallet.get_tx(tx2.hash)
            assert fetched is not None and fetched.is_failed is False, "Submitted tx should not be null or failed"
        finally:
            self.daemon.flush_tx_pool(tx2.hash)

    def setup(self) -> None:
        """Setup test."""
        # wait for txs to confirm and for sufficient unlocked balance
        # TODO monero-project: update from pool does not prevent creating double spend tx
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_wallets([self.wallet])
        assert len(self.config.subaddress_indices) == 0
        assert self.config.account_index is not None
        TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(self.wallet, self.config.account_index, None, self.config.amount)

        # rescan spent outputs for reliable before/after state
        self.wallet.rescan_spent()

        # record wallet balances before submitting tx to pool
        self.balance_before = self.wallet.get_balance()
        self.unlocked_balance_before = self.wallet.get_unlocked_balance()
        self.txs_before = self.wallet.get_txs()
        logger.debug(f"balance {self.balance_before}, unlocked balance {self.unlocked_balance_before}")

    def flush_tx(self, tx_hash: str) -> None:
        """
        Flush created test tx.

        :param str tx_hash: hash of the transaction to flush.
        """
        if self.config.relay is True:
            return

        # flush the tx from the pool
        self.daemon.flush_tx_pool(tx_hash)
        logger.debug(f"flushed tx from pool: {tx_hash}")

        # clear tx from wallet
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_wallets([self.wallet])

        # wallet should see failed state
        fetched = self.wallet.get_tx(tx_hash)
        if fetched is not None:
            assert fetched.is_failed, "Flushed tx should be failed"
            assert not fetched.in_tx_pool, "Flushed tx should not be in pool"
            assert not fetched.is_relayed, "Flushed tx should not be relayed"

        # wallet txs are restored
        txs_after: list[MoneroTxWallet] = self.wallet.get_txs()
        for tx_before in self.txs_before:
            if tx_before.hash != tx_hash:
                continue
            found: bool = False
            for tx_after in txs_after:
                if tx_before.hash != tx_after.hash:
                    continue
                # transfer fields which can update with confirmations
                # TODO: merge instead?
                tx_before.num_confirmations = tx_after.num_confirmations
                tx_before.is_locked = tx_after.is_locked

                AssertUtils.assert_equals(tx_before, tx_after)
                found = True

            assert found, f"Tx {tx_before.hash} not found after flushing tx from pool without relaying"

        # wallet balance should be restored
        wallet_balance: int = self.wallet.get_balance()
        logger.debug(f"New balance {wallet_balance}")
        assert self.balance_before == wallet_balance, "Wallet balance should be same as original since tx was flushed and not relayed"

    def test(self) -> None:
        """Run test."""
        self.setup()
        # create tx but do not relay
        config_no_relay: MoneroTxConfig = self.config.copy()
        config_no_relay.relay = False
        config_no_relay_copy: MoneroTxConfig = config_no_relay.copy()
        tx: MoneroTxWallet = self.wallet.create_tx(config_no_relay)
        assert tx.hash is not None

        # create tx using same config which is double spend
        tx_double_spend = self.wallet.create_tx(config_no_relay)
        assert tx_double_spend.hash is not None
        assert tx_double_spend.full_hex is not None

        # test that config is unchanged
        assert config_no_relay_copy != config_no_relay
        AssertUtils.assert_equals(config_no_relay_copy, config_no_relay)

        # submit tx directly to the pool but do not relay
        assert tx.full_hex is not None
        result: MoneroSubmitTxResult = self.daemon.submit_tx_hex(tx.full_hex, True)
        assert result.is_good, f"Transaction could not be submitted to the pool: {result}"

        # sync wallet wich checks pool
        self.wallet.sync()

        # test result and flush on finally
        try:
            # test tx state
            fetched: MoneroTxWallet | None = self.wallet.get_tx(tx.hash)
            assert fetched is not None
            assert fetched.is_failed is False, "Submitted tx should not be failed"
            # TODO: relay flag is not correctly set, insufficient info comes from monero-wallet-rpc
            #assert fetched.is_relayed is False, "Submitted tx should be same relayed as configuration"
            assert fetched.in_tx_pool is True, "Submitted tx should be in the pool"

            # submit double spend tx
            result_double_spend: MoneroSubmitTxResult = self.daemon.submit_tx_hex(tx_double_spend.full_hex, True)
            if result_double_spend.is_good is True:
                self.daemon.flush_tx_pool(tx_double_spend.hash)
                raise Exception("Tx submit result should have been double spend")

            # relay if configured
            if self.config.relay is True:
                self.daemon.relay_tx_by_hash(tx.hash)

            # sync wallet which updates from pool
            self.wallet.sync()

            self.run_failing_core_code(config_no_relay)
        finally:
            self.flush_tx(tx.hash)
