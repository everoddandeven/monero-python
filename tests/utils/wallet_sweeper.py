from typing import Optional

from monero import (
    MoneroWallet, MoneroSubaddress,
    MoneroTxConfig, MoneroTxWallet,
    MoneroOutputQuery, MoneroOutputWallet,
    MoneroTxQuery
)

from .tx_context import TxContext
from .assert_utils import AssertUtils
from .tx_utils import TxUtils
from .test_utils import TestUtils


class WalletSweeper:
    """Wallet funds sweeper"""

    _wallet: MoneroWallet
    """Test wallet instance to sweep funds from"""
    _sweep_each_subaddress: Optional[bool]
    """Indicates if each subaddress must be sweeped out"""

    def __init__(self, wallet: MoneroWallet, sweep_each_subaddress: Optional[bool]) -> None:
        """
        Initialize a new wallet sweeper.

        :param MoneroWallet wallet: wallet to sweep funds from.
        :param bool sweep_each_subaddress: sweep each wallet subaddress.
        """
        self._wallet = wallet
        self._sweep_each_subaddress = sweep_each_subaddress

    def _check_for_balance(self) -> None:
        """
        Checks for subaddresses with enough unlocked balance for sweep test.
        """
        # verify 2 subaddresses with enough unlocked balance to cover the fee
        subaddresses_balance: list[MoneroSubaddress] = []
        subaddresses_unlocked: list[MoneroSubaddress] = []

        for account in self._wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert subaddress.balance is not None
                assert subaddress.unlocked_balance is not None
                if subaddress.balance > TxUtils.MAX_FEE:
                    subaddresses_balance.append(subaddress)
                if subaddress.unlocked_balance > TxUtils.MAX_FEE:
                    subaddresses_unlocked.append(subaddress)

        assert len(subaddresses_balance) >= 2, "Test requires multiple accounts with a balance greater than the fee; run send to multiple first"
        assert len(subaddresses_unlocked) >= 2, "Wallet is waiting on unlocked funds"

    def _check_outputs(self) -> None:
        """
        Check for outputs amount after sweep.
        """
        # all unspent, unlocked outputs must be less than fee
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.is_spent = False
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_locked = False
        query.set_tx_query(tx_query, True)
        spendable_outputs: list[MoneroOutputWallet] = self._wallet.get_outputs(query)
        for spendable_output in spendable_outputs:
            assert spendable_output.amount is not None
            assert spendable_output.amount < TxUtils.MAX_FEE, f"Unspent output should have been swept\n{spendable_output.serialize()}"

        # all subaddress unlocked balances must be less than fee
        for account in self._wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert subaddress.unlocked_balance is not None
                assert subaddress.unlocked_balance < TxUtils.MAX_FEE, "No subaddress should have more unlocked than the fee"

    def sweep(self) -> None:
        """
        Sweep outputs from wallet.
        """
        # cleanup and check balance
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self._wallet)
        self._check_for_balance()

        # sweep funds
        destination: str = self._wallet.get_primary_address()
        config: MoneroTxConfig = MoneroTxConfig()
        config.address = destination
        config.sweep_each_subaddress = self._sweep_each_subaddress
        config.relay = True
        copy: MoneroTxConfig = config.copy()
        txs: list[MoneroTxWallet] = self._wallet.sweep_unlocked(config)
        # config is unchanged
        AssertUtils.assert_equals(config, copy)
        for tx in txs:
            assert tx.tx_set is not None
            assert tx in tx.tx_set.txs
            assert tx.tx_set.multisig_tx_hex is None
            assert tx.tx_set.signed_tx_hex is None
            assert tx.tx_set.unsigned_tx_hex is None

        assert len(txs) > 0
        for tx in txs:
            assert tx.outgoing_transfer is not None
            config = MoneroTxConfig()
            config.address = destination
            config.account_index = tx.outgoing_transfer.account_index
            config.sweep_each_subaddress = self._sweep_each_subaddress
            config.relay = True

            ctx: TxContext = TxContext()
            ctx.wallet = self._wallet
            ctx.config = config
            ctx.is_send_response = True
            ctx.is_sweep_response = True
            TxUtils.test_tx_wallet(tx, ctx)

        self._check_outputs()
