import logging

from time import sleep
from monero import (
    MoneroDaemon, MoneroWallet, MoneroTxQuery, MoneroSyncResult,
    MoneroTxWallet, MoneroMiningStatus, MoneroAccount
)

logger: logging.Logger = logging.getLogger("WalletTxTracker")


class WalletTxTracker:
    """Tracks wallets which are in sync with the tx pool and therefore whose txs in the pool
    do not need to be waited on for up-to-date pool information e.g. to create txs.

    This is only necessary because txs relayed outside wallets are not fully incorporated
    into the wallet state until confirmed.

    TODO monero-project: sync txs relayed outside wallet so this class is unecessary.
    """

    _daemon: MoneroDaemon
    """Daemon test instance."""
    _sync_period_ms: int
    """Sync period in milliseconds."""
    _mining_address: str
    """Mining address."""

    @property
    def sync_period(self) -> float:
        """Sync period in seconds.

        :returns float: sync period in seconds.
        """
        return self._sync_period_ms / 1000

    def __init__(self, daemon: MoneroDaemon, sync_period_ms: int, mining_address: str) -> None:
        """Initialize a new WalletTxTracker.

        :param MoneroDaemon daemon: Daemon test instance.
        :param int sync_period_ms: Sync period in ms.
        :param str mining_address: Address used for mining.
        """
        self._daemon = daemon
        self._sync_period_ms = sync_period_ms
        self._mining_address = mining_address

    @classmethod
    def get_unlocked_accounts(cls, wallet: MoneroWallet, num_subaddresses: int, min_amount: int) -> list[MoneroAccount]:
        accounts: list[MoneroAccount] = []
        for account in wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                if subaddress.unlocked_balance is not None and subaddress.unlocked_balance > min_amount:
                    accounts.append(account)
            if len(accounts) >= num_subaddresses:
                break
        return accounts

    def _sleep(self) -> None:
        """Sleep for one sync period."""
        sleep(self.sync_period)

    def _wait_for_txs_to_clear(self, clear_from_wallet: bool, wallets: list[MoneroWallet]) -> None:
        """Wait for wallet txs to clear pool.

        :param bool clear_from_wallet: Clear txs from wallet.
        :param list[MoneroWallet] wallets: Wallets to clear.
        """
        # loop until pending txs cleared
        is_first: bool = True
        mining_started: bool = False
        num_it: int = 0
        while True:
            num_it += 1
            msg: str = f"Clearing pending wallet transactions from {len(wallets)} wallets (it={num_it})..."
            if not clear_from_wallet:
                msg = f"Clearing pool pending wallet transactions (it={num_it})..."
            logger.debug(msg)

            # get pending wallet tx hashes
            tx_hashes_wallet: set[str] = set()
            for i, wallet in enumerate(wallets):
                result: MoneroSyncResult = wallet.sync()
                assert result.num_blocks_fetched is not None
                if result.num_blocks_fetched > 0:
                    logger.debug(f"Synced wallet {i + 1}, blocks fetched {result.num_blocks_fetched}")
                query: MoneroTxQuery = MoneroTxQuery()
                query.in_tx_pool = True
                pool_txs: list[MoneroTxWallet] = wallet.get_txs(query)
                for tx in pool_txs:
                    assert tx.hash is not None
                    if tx.is_relayed is not True:
                        continue
                    elif tx.is_failed:
                        # flush tx if failed
                        logger.debug(f"Found wallet failed tx {tx.hash}")
                        self._daemon.flush_tx_pool(tx.hash)
                        logger.debug(f"Flushed failed tx wallet {tx.hash}")
                    else:
                        tx_hashes_wallet.add(tx.hash)

            # get pending txs to wait for
            tx_hashes_pool: set[str] = set()
            if clear_from_wallet:
                tx_hashes_pool = tx_hashes_pool.union(tx_hashes_wallet)
            else:
                for tx in self._daemon.get_tx_pool():
                    assert tx.hash is not None
                    if tx.is_relayed is not True:
                        continue
                    elif tx.is_failed:
                        # flush tx if failed
                        logger.debug(f"Found failed pool tx {tx.hash}")
                        self._daemon.flush_tx_pool(tx.hash)
                        logger.debug(f"Flushed failed pool tx {tx.hash}")
                    elif tx.hash in tx_hashes_wallet:
                        tx_hashes_pool.add(tx.hash)

            num_txs_in_pool: int = len(tx_hashes_pool)
            # break if no txs to wait for
            if num_txs_in_pool == 0:
                logger.debug("No more pool txs to wait for")
                if mining_started:
                    # stop mining if started
                    self._daemon.stop_mining()
                break

            # log message and start mining if first iteration
            if is_first:
                is_first = False
                logger.info(f"Waiting for wallet txs to clear from the pool in order to fully sync and avoid double spend attempts: {tx_hashes_pool}")
                mining_status: MoneroMiningStatus = self._daemon.get_mining_status()
                if mining_status.is_active is not True:
                    try:
                        self._daemon.start_mining(self._mining_address, 1, False, False)
                        mining_started = True
                    except Exception as e:
                        logger.warning(f"An error occured while starting mining: {e}")
                        # no problem
                else:
                    logger.warning("Mining already active")

            # sleep for sync period
            logger.debug(f"Waiting for {num_txs_in_pool} tx(s) to confirm (it={num_it})...")
            self._sleep()

        # stop mining if started mining
        try:
            self._daemon.stop_mining()
        except Exception as e:
            logger.debug(str(e))

        # sync wallets with the pool
        for i, wallet in enumerate(wallets):
            while wallet.get_height() < self._daemon.get_height():
                result = wallet.sync()
                assert result.num_blocks_fetched is not None
                if result.num_blocks_fetched > 0:
                    logger.debug(f"Synced wallet {i + 1} with the pool, fetched {result.num_blocks_fetched} blocks")

        msg: str = f"Cleared pending wallet transactions from {len(wallets)} wallets"
        if not clear_from_wallet:
            msg = "Cleared pool pending wallet transactions"
        logger.debug(msg)

    def wait_for_txs_to_clear_pool(self, wallets: list[MoneroWallet] | MoneroWallet) -> None:
        """Wait for pending wallet transactions to clear the pool.

        :param list[MoneroWallet] wallets: Wallets to wait for pending transactions.
        """
        if isinstance(wallets, MoneroWallet):
            self._wait_for_txs_to_clear(False, [wallets])
        else:
            self._wait_for_txs_to_clear(False, wallets)

    def wait_for_txs_to_clear_wallets(self, wallets: list[MoneroWallet]) -> None:
        """Wait for pending wallet transactions to clear from the wallets.

        :param list[MoneroWallet] wallets: Wallets to wait for pending transactions.
        """
        self._wait_for_txs_to_clear(True, wallets)

    def wait_for_unlocked_balance(
        self, wallet: MoneroWallet,
        account_index: int, subaddress_index: int | None = None, min_amount: int | None = None
    ) -> int:
        """Wait for wallet unlocked balance.

        :param MoneroWallet wallet: Wallet to wait for unlocked balance.
        :param int account_index: Wallet account index.
        :param int | None subaddress_index: Wallet subaddress index.
        :param int | None min_amount: Minimum amount to wait for.
        :returns int: Unlocked balance.
        """
        if min_amount is None:
            min_amount = 0

        # check if wallet has balance
        err: Exception = Exception("Wallet does not have enough balance to wait for")
        if subaddress_index is not None and wallet.get_balance(account_index, subaddress_index) < min_amount:
            raise err
        elif subaddress_index is None and wallet.get_balance(account_index) < min_amount:
            raise err

        # check if wallet has unlocked balance
        unlocked_balance: int
        if subaddress_index is not None:
            unlocked_balance = wallet.get_unlocked_balance(account_index, subaddress_index)
        else:
            unlocked_balance = wallet.get_unlocked_balance(account_index)

        if unlocked_balance > min_amount:
            logger.debug(f"Wallet has enough unlocked balance {unlocked_balance}")
            return unlocked_balance

        # start mining
        mining_started: bool = False
        if not self._daemon.get_mining_status().is_active:
            try:
                self._daemon.start_mining(self._mining_address, 1, False, False)
                mining_started = True
            except Exception as e:
                logger.warning(f"An error occurred while starting mining: {str(e)}")
                # no problem

        # wait for unlocked balance // TODO: promote to MoneroWallet interface?
        if unlocked_balance < min_amount:
            logger.info(f"Waiting for minimum unlocked balance: {min_amount}")
        else:
            logger.info("Wallet has sufficient balance")

        while unlocked_balance < min_amount:
            logger.debug(f"Wallet unlocked balance: {unlocked_balance}, min amount: {min_amount}")

            if subaddress_index is not None:
                unlocked_balance = wallet.get_unlocked_balance(account_index, subaddress_index)
            else:
                unlocked_balance = wallet.get_unlocked_balance(account_index)

            self._sleep()

        # stop mining if started
        if mining_started:
            self._daemon.stop_mining()

        return unlocked_balance

    def wait_for_wallet_unlocked_balance(
        self, wallet: MoneroWallet,
        num_subaddresses: int, min_amount: int | None = None
    ) -> None:
        """Wait until some account has at least `num_subaddresses` subaddresses with unlocked balance.

        :param MoneroWallet wallet: Wallet to wait for unlocked balance.
        :param int num_subaddresses: Minimum number of subaddresses with unlocked balance required within a single account.
        :param int | None min_amount: Minimum unlocked balance per subaddress to count it (default 0).
        :returns MoneroAccount: the first account found to satisfy the condition.
        """
        if min_amount is None:
            min_amount = 0

        found: list[MoneroAccount] = self.get_unlocked_accounts(wallet, num_subaddresses, min_amount)
        if len(found) > 0:
            logger.debug(f"Wallet already has an account with {num_subaddresses} unlocked subaddresses")
            return

        # start mining
        mining_started: bool = False
        if not self._daemon.get_mining_status().is_active:
            try:
                self._daemon.start_mining(self._mining_address, 1, False, False)
                mining_started = True
            except Exception as e:
                logger.warning(f"An error occurred while starting mining: {str(e)}")
                # no problem

        logger.info(f"Waiting for an account with {num_subaddresses} unlocked subaddresses")
        while len(found) == 0:
            self._sleep()
            found = self.get_unlocked_accounts(wallet, num_subaddresses, min_amount)

        # stop mining if started
        if mining_started:
            self._daemon.stop_mining()

