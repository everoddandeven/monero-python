import logging

from typing import Optional
from monero import (
    MoneroWallet, MoneroAccount, MoneroSubaddress, MoneroTxConfig,
    MoneroTxPriority, MoneroDestination, MoneroTxWallet
)

from utils import TxUtils, AssertUtils, TestUtils, TxContext

logger: logging.Logger = logging.getLogger("ToMultipleTxSender")


class ToMultipleTxSender:
    """Sends funds from the first unlocked account to multiple accounts and subaddresses."""

    SEND_DIVISOR: int = 10
    """Transaction amount send divisor."""
    SEND_MAX_DIFF: int = 60

    _wallet: MoneroWallet
    """Wallet test instance"""
    _num_accounts: int
    """Number of account to receive funds"""
    _num_subaddresses_per_account: int
    """Number of subaddresses per account to receive funds"""
    _can_split: bool
    """Split into multiple transactions"""
    _send_amount_per_subaddress: Optional[int]
    """Amount to send to each subaddress"""
    _subtract_fee_from_destinations: bool
    """Subtract the from destination addresses"""

    @property
    def total_subaddresses(self) -> int:
        """Total num of subaddresses to send txs to"""
        return self._num_accounts * self._num_subaddresses_per_account

    @property
    def min_account_amount(self) -> int:
        """Minimum account unlocked balance needed"""
        fee: int = TxUtils.MAX_FEE # 75000000000
        # compute the minimum account unlocked balance needed in order to fulfill the config
        if self._send_amount_per_subaddress is not None:
            # min account amount must cover the total amount being sent plus the tx fee = num_addresses * (amount_per_subaddress + fee)
            return self.total_subaddresses * (self._send_amount_per_subaddress + fee)

        # account balance must be more than fee * num_addresses * divisor + fee so each destination amount is at least a fee's worth (so dust is not sent)
        return ((fee * self.total_subaddresses) * self.SEND_DIVISOR) + fee

    def __init__(
            self,
            wallet: MoneroWallet,
            num_accounts: int,
            num_subaddresses_per_account: int,
            can_split: bool,
            send_amount_per_subaddress: Optional[int],
            subtract_fee_from_destinations: bool
            ) -> None:
        """
        Initialize a new multiple tx sender.

        :param MoneroWallet wallet: wallet to send txs from
        :param int num_accounts: is the number of accounts to receive funds
        :param int num_subaddresses_per_account: is the number of subaddresses per account to receive funds
        :param bool can_split: specifies if the operation can be split into multiple transactions
        :param int | None send_amount_per_subaddress: is the amount to send to each subaddress (optional, computed if not given)
        :param bool subtract_fee_from_destinations: specifies to subtract the fee from destination addresses
        """
        self._wallet = wallet
        self._num_accounts = num_accounts
        self._num_subaddresses_per_account = num_subaddresses_per_account
        self._can_split = can_split
        self._send_amount_per_subaddress = send_amount_per_subaddress
        self._subtract_fee_from_destinations = subtract_fee_from_destinations

    #region Private Methods

    def _get_source_account(self) -> MoneroAccount:
        """
        Get wallet account to send funds from.

        :returns MoneroAccount: account to send funds from.
        """
        min_account_amount: int = self.min_account_amount
        src_account: Optional[MoneroAccount] = None
        has_balance: bool = False
        # get first account with sufficient unlocked funds
        for account in self._wallet.get_accounts():
            assert account.balance is not None
            assert account.unlocked_balance is not None
            if account.balance > min_account_amount:
                has_balance = True
            if account.unlocked_balance > min_account_amount:
                src_account = account
                break

        assert has_balance, f"Wallet does not have enough balance; load '{TestUtils.WALLET_NAME}' with XMR in order to test sending"
        assert src_account is not None, "Wallet is waiting on unlocked funds"
        return src_account

    def _create_accounts(self) -> int:
        """Creates minimum number of accounts"""
        num_accounts: int = len(self._wallet.get_accounts())
        logger.info(f"Wallet has already {num_accounts} accounts")
        num_accounts_to_create: int = self._num_accounts - num_accounts if num_accounts <= self._num_accounts else 0
        for i in range(num_accounts_to_create):
            self._wallet.create_account()
            logger.debug(f"Created account {i + 1}")
        return num_accounts_to_create

    def _create_subaddresses(self) -> list[str]:
        """Creates minimum number of subaddress per account"""
        destination_addresses: list[str] = []

        for i in range(self._num_accounts):
            subaddresses: list[MoneroSubaddress] = self._wallet.get_subaddresses(i)
            for j in range(self._num_subaddresses_per_account - len(subaddresses)):
                self._wallet.create_subaddress(i)
                logger.debug(f"Created subaddress {i},{j}")

            subaddresses = self._wallet.get_subaddresses(i)
            assert len(subaddresses) >= self._num_subaddresses_per_account
            for j in range(self._num_subaddresses_per_account):
                subaddress: MoneroSubaddress = subaddresses[j]
                assert subaddress.address is not None
                destination_addresses.append(subaddress.address)

        return destination_addresses

    def _build_tx_config(self, src_account: MoneroAccount, send_amount_per_subaddress: int, destination_addresses: list[str]) -> MoneroTxConfig:
        """Build tx configuration"""
        config: MoneroTxConfig = MoneroTxConfig()
        config.account_index = src_account.index
        config.relay = True
        config.can_split = self._can_split
        config.priority = MoneroTxPriority.NORMAL

        subtract_fee_from: list[int] = []
        for i, address in enumerate(destination_addresses):
            destination: MoneroDestination = MoneroDestination()
            destination.address = address
            destination.amount = send_amount_per_subaddress
            config.destinations.append(destination)
            subtract_fee_from.append(i)

        if self._subtract_fee_from_destinations:
            config.subtract_fee_from = subtract_fee_from

        return config

    #endregion

    def send(self) -> None:
        """Send multiple txs from wallet"""

        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self._wallet)

        # send funds from first account with sufficient unlocked funds
        src_account: MoneroAccount = self._get_source_account()
        assert src_account.index is not None
        assert src_account.balance is not None
        assert src_account.unlocked_balance is not None
        balance: int = src_account.balance
        unlocked_balance: int = src_account.unlocked_balance

        # get amount to send total and per subaddress
        total_subaddresses: int = self.total_subaddresses
        send_amount: Optional[int] = None
        send_amount_per_subaddress: Optional[int] = self._send_amount_per_subaddress

        if send_amount_per_subaddress is None:
            send_amount = TxUtils.MAX_FEE * 5 * total_subaddresses
            send_amount_per_subaddress = int(send_amount / total_subaddresses)
        else:
            send_amount = send_amount_per_subaddress * total_subaddresses

        # create minimum number of accounts
        created_accounts: int = self._create_accounts()
        logger.debug(f"Created {created_accounts} accounts")

        # create minimum number of subaddresses per account and collect destination addresses
        destination_addresses: list[str] = self._create_subaddresses()
        config: MoneroTxConfig = self._build_tx_config(src_account, send_amount_per_subaddress, destination_addresses)
        config_copy: MoneroTxConfig = config.copy()

        # send tx(s) with config
        txs: list[MoneroTxWallet] = []
        try:
            txs = self._wallet.create_txs(config)
        except Exception as e:
            # test error applying subtractFromFee with split txs
            if self._subtract_fee_from_destinations and len(txs) == 0:
                if str(e) == "subtractfeefrom transfers cannot be split over multiple transactions yet":
                    logger.debug(str(e))
                    return
            raise

        if not self._can_split:
            assert len(txs) == 1

        # test that config is unchanged
        assert config_copy != config
        AssertUtils.assert_equals(config_copy, config)

        # test that wallet balance decreased
        account: MoneroAccount = self._wallet.get_account(src_account.index)
        assert account.balance is not None
        assert account.unlocked_balance is not None
        assert account.balance < balance
        assert account.unlocked_balance < unlocked_balance

        # build test context
        config.can_split = self._can_split
        ctx: TxContext = TxContext()
        ctx.wallet = self._wallet
        ctx.config = config
        ctx.is_send_response = True

        # test each transaction
        assert len(txs) > 0
        fee_sum: int = 0
        outgoing_sum: int = 0
        TxUtils.test_txs_wallet(txs, ctx)
        for tx in txs:
            assert tx.fee is not None
            fee_sum += tx.fee
            outgoing_sum += tx.get_outgoing_amount()

            if tx.outgoing_transfer is not None and len(tx.outgoing_transfer.destinations) > 0:
                destination_sum: int = 0
                for destination in tx.outgoing_transfer.destinations:
                    TxUtils.test_destination(destination)
                    assert destination.amount is not None
                    assert destination.address in destination_addresses
                    destination_sum += destination.amount

                # assert that transfers sum up to tx amount
                assert destination_sum == tx.get_outgoing_amount()

        # assert that outgoing amounts sum up to the amount sent within a small margin
        amount: int = (send_amount - fee_sum) if self._subtract_fee_from_destinations else send_amount
        amount = abs(amount - outgoing_sum)

        if amount > self.SEND_MAX_DIFF:
            raise Exception("Actual send amount is too different from requested send amount")
