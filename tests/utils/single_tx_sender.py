import logging

from typing import Optional
from monero import (
    MoneroWallet, MoneroTxConfig, MoneroAccount,
    MoneroSubaddress, MoneroDaemonRpc, MoneroDestination,
    MoneroTxWallet, MoneroTxQuery
)

from .tx_context import TxContext
from .assert_utils import AssertUtils
from .wallet_tx_tracker import WalletTxTracker as TxTracker
from .test_utils import TestUtils
from .tx_utils import TxUtils

logger: logging.Logger = logging.getLogger("SingleTxSender")


class SingleTxSender:
    """Sends funds from the first unlocked account to primary account address."""

    SEND_DIVISOR: int = 10

    _config: MoneroTxConfig
    _wallet: MoneroWallet
    _daemon: MoneroDaemonRpc

    _from_account: Optional[MoneroAccount] = None
    _from_subaddress: Optional[MoneroSubaddress] = None

    @property
    def tracker(self) -> TxTracker:
        return TestUtils.WALLET_TX_TRACKER

    @property
    def balance_before(self) -> int:
        balance = self._from_subaddress.balance if self._from_subaddress is not None else 0
        return balance if balance is not None else 0

    @property
    def unlocked_balance_before(self) -> int:
        balance = self._from_subaddress.unlocked_balance if self._from_subaddress is not None else 0
        return balance if balance is not None else 0

    @property
    def send_amount(self) -> int:
        b = self.unlocked_balance_before
        return int((b - TxUtils.MAX_FEE) / self.SEND_DIVISOR)

    @property
    def address(self) -> str:
        return self._wallet.get_primary_address()

    def __init__(self, wallet: MoneroWallet, config: Optional[MoneroTxConfig]) -> None:
        self._wallet = wallet
        self._daemon = TestUtils.get_daemon_rpc()
        self._config = config if config is not None else MoneroTxConfig()

    #region Private Methods

    def _build_tx_config(self) -> MoneroTxConfig:
        assert self._from_account is not None
        assert self._from_account.index is not None
        assert self._from_subaddress is not None
        assert self._from_subaddress.index is not None
        self._config.destinations.append(MoneroDestination(self.address, self.send_amount))
        self._config.account_index = self._from_account.index
        self._config.subaddress_indices.append(self._from_subaddress.index)
        return self._config

    def _get_locked_txs(self) -> list[MoneroTxWallet]:
        """Returns locked txs"""
        # query locked txs
        query = MoneroTxQuery()
        query.is_locked = True
        locked_txs = TxUtils.get_and_test_txs(self._wallet, query, None, True, TestUtils.REGTEST)

        for locked_tx in locked_txs:
            assert locked_tx.is_locked, "Expected locked tx"

        return locked_txs

    def _check_balance(self) -> None:
        """
        Assert wallet has sufficient balance.
        """
        # wait for wallet to clear unconfirmed txs
        self.tracker.wait_for_txs_to_clear_pool([self._wallet])
        sufficient_balance: bool = False
        accounts = self._wallet.get_accounts(True)
        # iterate over all wallet addresses
        for account in accounts:
            for i, subaddress in enumerate(account.subaddresses):
                if i == 0:
                    continue
                assert subaddress.balance is not None
                assert subaddress.unlocked_balance is not None
                if subaddress.balance > TxUtils.MAX_FEE:
                    sufficient_balance = True
                if subaddress.unlocked_balance > TxUtils.MAX_FEE:
                    self._from_account = account
                    self._from_subaddress = subaddress
                    break
            if self._from_account is not None:
                break
        # check for sufficient balance
        assert sufficient_balance, "No non-primary subaddress found with sufficient balance"
        assert self._from_subaddress is not None, "Wallet is waiting on unlocked funds"
        logger.debug(f"Selected subaddress ({self._from_subaddress.account_index},{self._from_subaddress.index}), balance: {self._from_subaddress.balance}")

    def _check_balance_decreased(self) -> None:
        """Checks that wallet balance decreased"""
        # TODO test that other balances did not decrease
        assert self._from_account is not None
        assert self._from_subaddress is not None
        assert self._from_account.index is not None
        assert self._from_subaddress.index is not None
        subaddress = self._wallet.get_subaddress(self._from_account.index, self._from_subaddress.index)
        assert subaddress.balance is not None
        assert subaddress.balance < self.balance_before, f"Expected {subaddress.balance} < {self.balance_before}"
        assert subaddress.unlocked_balance is not None
        assert subaddress.unlocked_balance < self.unlocked_balance_before, f"Expected {subaddress.unlocked_balance} < {self.unlocked_balance_before}"
        logger.debug(f"Balance decreased from {self.balance_before} to {subaddress.balance}")

    def _send_to_invalid(self, config: MoneroTxConfig) -> None:
        """Send to invalid address"""
        # save original address
        try:
            # set invalid destination address
            config.set_address("my invalid address")
            # create tx
            if config.can_split is not False:
                self._wallet.create_txs(config)
            else:
                self._wallet.create_tx(config)
            # raise error
            raise Exception("Should have thrown error creating tx with invalid address")
        except Exception as e:
            assert str(e) == "Invalid destination address", str(e)
        finally:
            # restore original address
            config.set_address(self.address)

    def _send_to_self(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        """Test sending to self"""
        txs = self._wallet.create_txs(config)

        if config.can_split is False:
            # must have exactly one tx if no split
            assert len(txs) == 1

        return txs

    def _handle_non_relayed_tx(self, txs: list[MoneroTxWallet], config: MoneroTxConfig) -> list[MoneroTxWallet]:
        if config.relay is True:
            return txs

        # build test context
        ctx = TxContext()
        ctx.wallet = self._wallet
        ctx.config = config
        ctx.is_send_response = True

        # test transactions
        TxUtils.test_txs_wallet(txs, ctx)

        # txs are not in the pool
        for tx_created in txs:
            for tx_pool in self._daemon.get_tx_pool():
                assert tx_pool.hash is not None
                assert tx_created is not None
                assert tx_pool.hash != tx_created.hash, "Created tx should not be in the pool"

        # relay txs
        tx_hashes: list[str] = []
        if config.can_split is not True:
            # test relay_tx() with single transaction
            tx_hashes = [self._wallet.relay_tx(txs[0])]
        else:
            tx_metadatas: list[str] = []
            for tx in txs:
                assert tx.metadata is not None
                tx_metadatas.append(tx.metadata)
            # test relayTxs() with potentially multiple transactions
            tx_hashes = self._wallet.relay_txs(tx_metadatas)

        for tx_hash in tx_hashes:
            assert len(tx_hash) == 64

        # fetch txs for testing
        query = MoneroTxQuery()
        query.hashes = tx_hashes
        return self._wallet.get_txs(query)

    #endregion

    def send(self) -> None:
        # check wallet balance
        self._check_balance()

        assert self._from_subaddress is not None
        assert self._from_account is not None

        # init tx config
        config = self._build_tx_config()
        config_copy = config.copy()

        # test sending to invalid address
        self._send_to_invalid(config)

        # test send to self
        txs = self._send_to_self(config)

        logger.debug(f"Created {len(txs)}")

        # test that config is unchaged
        assert config_copy != config
        AssertUtils.assert_equals(config_copy, config)

        # test common tx set among txs
        TxUtils.test_common_tx_sets(txs, False, False, False)

        # handle non-relayed transaction
        txs = self._handle_non_relayed_tx(txs, config)

        logger.debug(f"Handled {len(txs)} txs")

        # test that balance and unlocked balance decreased
        self._check_balance_decreased()

        locked_txs = self._get_locked_txs()

        # build test context
        ctx = TxContext()
        ctx.wallet = self._wallet
        ctx.config = config
        ctx.is_send_response = config.relay is True

        # test transactions
        assert len(txs) > 0
        for tx in txs:
            TxUtils.test_tx_wallet(tx, ctx)
            assert tx.outgoing_transfer is not None
            assert self._from_account.index == tx.outgoing_transfer.account_index
            assert len(tx.outgoing_transfer.subaddress_indices) == 1
            assert self._from_subaddress.index == tx.outgoing_transfer.subaddress_indices[0]
            assert self.send_amount == tx.get_outgoing_amount()
            if config.payment_id is not None:
                assert config.payment_id == tx.payment_id

            # test outgoing destinations
            dest_count = len(tx.outgoing_transfer.destinations)
            if dest_count > 0:
                assert dest_count == 1
                for dest in tx.outgoing_transfer.destinations:
                    TxUtils.test_destination(dest)
                    assert dest.address == self.address
                    assert self.send_amount == dest.amount

            # tx is among locked txs
            found: bool = False
            for locked in locked_txs:
                if locked.hash == tx.hash:
                    found = True
                    break

            assert found, "Created txs should be among locked txs"
