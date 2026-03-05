import logging

from typing import Optional

from monero import (
    MoneroWallet, MoneroTxConfig, MoneroAccount,
    MoneroSubaddress, MoneroDestination, MoneroTxWallet
)

from .assert_utils import AssertUtils
from .test_utils import TestUtils
from .tx_utils import TxUtils
from .tx_context import TxContext

logger: logging.Logger = logging.getLogger("FromMultipleTxSender")


class FromMultipleTxSender:

    SEND_DIVISOR: int = 10
    SEND_MAX_DIFF: int = 60
    NUM_SUBADDRESSES: int = 2
    """Number of subaddresses to send from"""

    _wallet: MoneroWallet
    _config: MoneroTxConfig
    _accounts: list[MoneroAccount]
    _unlocked_subaddress: list[MoneroSubaddress]

    def __init__(self, wallet: MoneroWallet, can_split: Optional[bool] = None) -> None:
        self._wallet = wallet
        self._config = MoneroTxConfig()
        self._config.can_split = can_split
        self._unlocked_subaddress = []
        self._accounts = []

    def _get_src_account(self) -> MoneroAccount:
        """"""
        # get first account with (NUM_SUBADDRESSES + 1) subaddresses with unlocked balances
        self._accounts = self._wallet.get_accounts(True)
        assert len(self._accounts) >= 2, "This test requires at least 2 accounts; run send-to-multiple tests"
        # prefer first account instead of primary
        # TODO why this is needed?
        primary_account = self._accounts[0]
        first_account = self._accounts[1]
        self._accounts[0] = first_account
        self._accounts[1] = primary_account

        src_account: Optional[MoneroAccount] = None
        unlocked_subaddresses: list[MoneroSubaddress] = []
        has_balance: bool = False
        for account in self._accounts:
            unlocked_subaddresses.clear()
            num_subaddress_balances: int = 0
            for subaddress in account.subaddresses:
                assert subaddress.balance is not None
                assert subaddress.unlocked_balance is not None
                if subaddress.balance > TxUtils.MAX_FEE:
                    num_subaddress_balances += 1
                if subaddress.unlocked_balance > TxUtils.MAX_FEE:
                    unlocked_subaddresses.append(subaddress)

            if num_subaddress_balances >= self.NUM_SUBADDRESSES + 1:
                has_balance = True
            if len(unlocked_subaddresses) >= self.NUM_SUBADDRESSES + 1:
                src_account = account
                break

        assert has_balance, f"Wallet does not have account with {self.NUM_SUBADDRESSES + 1} subaddresses with balances; run send-to-multiple tests"
        assert len(unlocked_subaddresses) > self.NUM_SUBADDRESSES + 1, "Wallet is waiting on unlocked funds"
        self._unlocked_subaddress = unlocked_subaddresses
        assert src_account is not None
        # Restore accounts order
        self._accounts[0] = primary_account
        self._accounts[1] = first_account
        return src_account

    def send(self) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self._wallet)

        # get account
        src_account: MoneroAccount = self._get_src_account()
        assert src_account.index is not None

        logger.debug(f"Selected source account {src_account.index}")

        # determine the indices of the first two subaddresses with unlocked balances
        from_subaddress_indices: list[int] = []
        for i in range(self.NUM_SUBADDRESSES):
            from_subaddress_indices.append(i)

        # determine amount to send
        send_amount: int = 0
        for from_subaddress_idx in from_subaddress_indices:
            src_subaddress: MoneroSubaddress = src_account.subaddresses[from_subaddress_idx]
            assert src_subaddress.unlocked_balance is not None
            send_amount += src_subaddress.unlocked_balance

        send_amount = int(send_amount / self.SEND_DIVISOR)
        from_balance: int = 0
        from_unlocked_balance: int = 0
        for subaddress_idx in from_subaddress_indices:
            subaddress: MoneroSubaddress = self._wallet.get_subaddress(src_account.index, subaddress_idx)
            assert subaddress.balance is not None
            assert subaddress.unlocked_balance is not None
            from_balance += subaddress.balance
            from_unlocked_balance += subaddress.unlocked_balance

        # send from the first subaddresses with unlocked balances
        address: str = self._wallet.get_primary_address()
        self._config.destinations = [MoneroDestination(address, send_amount)]
        self._config.account_index = src_account.index
        self._config.subaddress_indices = from_subaddress_indices
        self._config.relay = True
        config_copy: MoneroTxConfig = self._config.copy()
        txs: list[MoneroTxWallet] = []

        if self._config.can_split is not False:
            txs.extend(self._wallet.create_txs(self._config))
        else:
            txs.append(self._wallet.create_tx(self._config))

        logger.debug(f"Created {len(txs)} txs")

        if self._config.can_split is False:
            # must have exactly one tx if no split
            assert len(txs) == 1

        # test that config is unchanged
        assert config_copy != self._config
        AssertUtils.assert_equals(config_copy, self._config)

        # test that balances of intended subaddresses decreased
        accounts_after: list[MoneroAccount] = self._wallet.get_accounts(True)
        assert len(self._accounts) == len(accounts_after)
        src_unlocked_balance_decreased: bool = False
        for i, account in enumerate(self._accounts):
            account_after: MoneroAccount = accounts_after[i]
            assert len(account.subaddresses) == len(account_after.subaddresses)
            for j, subaddress_before in enumerate(account.subaddresses):
                subaddress_after: MoneroSubaddress = account_after.subaddresses[j]
                if i == src_account.index and j in from_subaddress_indices:
                    assert subaddress_before.unlocked_balance is not None
                    assert subaddress_after.unlocked_balance is not None
                    if subaddress_after.unlocked_balance < subaddress_before.unlocked_balance:
                        src_unlocked_balance_decreased = True
                    else:
                        msg: str = f"Subaddress [{i},{j}] unlocked balance should not have changed"
                        assert subaddress_after.unlocked_balance == subaddress_before.unlocked_balance, msg

        assert src_unlocked_balance_decreased, "Subaddress unlocked balances should have decreased"

        # test context
        ctx: TxContext = TxContext()
        ctx.config = self._config
        ctx.wallet = self._wallet
        ctx.is_send_response = True

        # test each transaction
        assert len(txs) > 0
        outgoing_sum: int = 0
        for tx in txs:
            TxUtils.test_tx_wallet(tx, ctx)
            outgoing_sum += tx.get_outgoing_amount()
            if tx.outgoing_transfer is not None and len(tx.outgoing_transfer.destinations) > 0:
                destination_sum: int = 0
                for destination in tx.outgoing_transfer.destinations:
                    TxUtils.test_destination(destination)
                    assert destination.amount is not None
                    assert address == destination.address
                    destination_sum += destination.amount

                # assert that transfers sum up to tx amount
                assert destination_sum == tx.get_outgoing_amount()

        # assert that tx amounts sum up the amount sent within a small margin
        if abs(send_amount - outgoing_sum) > self.SEND_MAX_DIFF:
            # send amounts may be slightly different
            raise Exception(f"Tx amounts are too different: {send_amount} - {outgoing_sum} = {send_amount} - {outgoing_sum})")
