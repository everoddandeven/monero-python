from monero import (
    MoneroWallet, MoneroSubaddress,
    MoneroTxConfig, MoneroTxWallet,
    MoneroOutputQuery, MoneroOutputWallet,
    MoneroTxQuery
)

from .context import TxContext
from .assert_utils import AssertUtils
from .tx_wallet_utils import TxWalletUtils
from .test_utils import TestUtils


class WalletSweeper:
    """Wallet funds sweeper."""

    _wallet: MoneroWallet
    """Test wallet instance to sweep funds from."""
    _sweep_each_subaddress: bool | None
    """Indicates if each subaddress must be sweeped out."""

    def __init__(self, wallet: MoneroWallet, sweep_each_subaddress: bool | None) -> None:
        """Initialize a new wallet sweeper.

        :param MoneroWallet wallet: wallet to sweep funds from.
        :param bool sweep_each_subaddress: sweep each wallet subaddress.
        """
        self._wallet = wallet
        self._sweep_each_subaddress = sweep_each_subaddress

    def _check_for_balance(self) -> None:
        """Checks for subaddresses with enough unlocked balance for sweep test."""
        # verify 2 subaddresses with enough unlocked balance to cover the fee
        subaddresses_balance: list[MoneroSubaddress] = []
        subaddresses_unlocked: list[MoneroSubaddress] = []

        for account in self._wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert subaddress.balance is not None
                assert subaddress.unlocked_balance is not None
                if subaddress.balance > TxWalletUtils.MAX_FEE:
                    subaddresses_balance.append(subaddress)
                if subaddress.unlocked_balance > TxWalletUtils.MAX_FEE:
                    subaddresses_unlocked.append(subaddress)

        assert len(subaddresses_balance) >= 2, "Test requires multiple accounts with a balance greater than the fee; run send to multiple first"
        assert len(subaddresses_unlocked) >= 2, "Wallet is waiting on unlocked funds"

    def _get_unlocked_outputs(self) -> list[MoneroOutputWallet]:
        """Get the unspent outputs that are unlocked.

        :returns list[MoneroOutputWallet]: unspent and unlocked outputs of the wallet.
        """
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.is_spent = False
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_locked = False
        query.set_tx_query(tx_query, True)
        outputs: list[MoneroOutputWallet] = self._wallet.get_outputs(query)
        for output in outputs:
            assert output.stealth_public_key is not None
            assert output.amount is not None
            assert output.account_index is not None
            assert output.subaddress_index is not None
        return outputs

    def _check_outputs(self, unlocked_before: set[str]) -> None:
        """Check for outputs amount after sweep.

        The sweep takes the outputs that are unlocked when it starts. The ones that are locked then (the change of the txs just before, and
        the outputs that the sweep creates: it sends to the primary address of the wallet) are not swept, and the chain does not wait for
        the checks: the blocks keep coming while the wallet syncs (the light wallet gets them from lws, which scans after the daemon), so
        they can be unlocked when they are checked. They are not funds that the sweep left behind, so they are not counted.

        :param set[str] unlocked_before: stealth public keys of the outputs that were unlocked when the sweep started.
        """
        # The balances are read before the outputs: when a block unlocks outputs in between, the outputs that are subtracted from the
        # balances are more, not less, and the check does not fail for them
        balances: dict[tuple[int, int], int] = {}
        for account in self._wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert subaddress.unlocked_balance is not None
                assert account.index is not None
                assert subaddress.index is not None
                balances[(account.index, subaddress.index)] = subaddress.unlocked_balance

        # all the outputs that were unlocked and unspent must be less than fee
        unlocked_later: dict[tuple[int, int], int] = {}
        for spendable_output in self._get_unlocked_outputs():
            assert spendable_output.amount is not None
            assert spendable_output.account_index is not None
            assert spendable_output.subaddress_index is not None
            if spendable_output.stealth_public_key not in unlocked_before:
                key: tuple[int, int] = (spendable_output.account_index, spendable_output.subaddress_index)
                unlocked_later[key] = unlocked_later.get(key, 0) + spendable_output.amount
                continue
            tx_hash: str | None = spendable_output.tx.hash if spendable_output.tx is not None else None # type: ignore
            assert spendable_output.amount < TxWalletUtils.MAX_FEE, (
                f"Unspent output should have been swept, it was unlocked before the sweep (tx {tx_hash})\n{spendable_output.serialize()}"
            )

        # all subaddress unlocked balances must be less than fee
        for (account_index, subaddress_index), unlocked_balance in balances.items():
            later: int = unlocked_later.get((account_index, subaddress_index), 0)
            assert unlocked_balance - later < TxWalletUtils.MAX_FEE, (
                f"No subaddress should have more unlocked than the fee: subaddress ({account_index}, {subaddress_index}) has "
                f"{unlocked_balance} unlocked, {later} of outputs that were locked when the sweep started"
            )

    def sweep(self) -> None:
        """Sweep outputs from wallet."""
        # cleanup and check balance
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self._wallet)
        self._check_for_balance()
        unlocked_before: set[str] = {str(output.stealth_public_key) for output in self._get_unlocked_outputs()}

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
            TxWalletUtils.test_tx_wallet(tx, ctx)

        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self._wallet)

        self._check_outputs(unlocked_before)
