import logging

from time import monotonic, sleep
from monero import (
    MoneroDaemon, MoneroWallet, MoneroWalletRpc, MoneroTxQuery, MoneroSyncResult,
    MoneroTxWallet, MoneroMiningStatus, MoneroAccount, MoneroWalletLight
)

from .block_generation import is_generation_fast

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
    _can_generate_blocks: bool | None = None
    """Indicates if the daemon generates blocks on request (regtest only), `None` until it is tried."""

    WAIT_TIMEOUT_SECONDS: float = 300.0
    """Longest that a wallet is waited for, to reach the height of the daemon or to have unlocked funds. A wallet that does not get there
    (a light wallet when monero-lws does not catch up) fails the test, instead of waiting until the job is cancelled."""

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
        """Get the accounts that have at least `num_subaddresses` subaddresses with an unlocked balance greater than `min_amount`.

        The subaddresses are counted inside each account: the unlocked ones of different accounts do not add up.

        :param MoneroWallet wallet: wallet to get the accounts of.
        :param int num_subaddresses: minimum number of subaddresses with unlocked balance of an account.
        :param int min_amount: unlocked balance that a subaddress must exceed to count.
        :returns list[MoneroAccount]: the accounts that satisfy the condition.
        """
        accounts: list[MoneroAccount] = []
        for account in wallet.get_accounts(True):
            num_unlocked: int = sum(
                1 for subaddress in account.subaddresses
                if subaddress.unlocked_balance is not None and subaddress.unlocked_balance > min_amount
            )
            if num_unlocked >= num_subaddresses:
                accounts.append(account)
        return accounts

    def _sleep(self) -> None:
        """Sleep for one sync period."""
        sleep(self.sync_period)

    def _generate_block(self) -> bool:
        """Generate one block, to clear the pool, when the difficulty is low. The CPU miner is not used for it then: it makes blocks without
        stopping and the chain grows past 10000 outputs, where monero-project fails the txs it creates with "Transaction sanity check failed".

        :returns bool: `True` if a block was generated, `False` if the daemon can not generate blocks (not regtest) or mining is faster.
        """
        if self._can_generate_blocks is False:
            return False
        if not is_generation_fast(self._daemon):
            return False
        try:
            self._daemon.generate_blocks(self._mining_address, 1)
            self._can_generate_blocks = True
        except Exception as e:
            logger.debug(f"The daemon can not generate blocks: {e}")
            self._can_generate_blocks = False
        return self._can_generate_blocks

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

            # log message on the first iteration
            if is_first:
                logger.info(f"Waiting for wallet txs to clear from the pool in order to fully sync and avoid double spend attempts: {tx_hashes_pool}")

            # on regtest a block is generated on each iteration, and the wallets are synced in the next one
            if self._generate_block():
                is_first = False
                continue

            # start mining if first iteration
            if is_first:
                is_first = False
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
            if isinstance(wallet, MoneroWalletLight):
                # lws scans the blocks by itself and the light wallet only gets what it has scanned: wait for it before syncing
                from .test_utils import TestUtils  # test_utils creates a tracker, so it is imported here
                TestUtils.wait_for_lws_scan(wallet)
            deadline: float = monotonic() + self.WAIT_TIMEOUT_SECONDS
            while wallet.get_height() < self._daemon.get_height():
                if monotonic() > deadline:
                    raise TimeoutError(
                        f"Wallet {i + 1} is at height {wallet.get_height()}, the daemon at {self._daemon.get_height()}, "
                        f"after {self.WAIT_TIMEOUT_SECONDS:.0f}s of syncing"
                    )
                result = wallet.sync()
                assert result.num_blocks_fetched is not None
                if result.num_blocks_fetched > 0:
                    logger.debug(f"Synced wallet {i + 1} with the pool, fetched {result.num_blocks_fetched} blocks")

        # The server of a wallet rpc has the same keys as the full wallet, which sends txs and flushes them from the pool. The server keeps
        # as pending what it saw in the pool, and 500 seconds after, when it is not there, it marks it failed and sets its inputs as
        # unspent, even when another tx spent them. The next tx would use them and the daemon would reject it as a double spend. The
        # daemon says which outputs are spent (the ones in the pool too): asking it here, right before the txs that follow, leaves no time
        # for the server to change them again
        for wallet in wallets:
            if isinstance(wallet, MoneroWalletRpc):
                wallet.rescan_spent()

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
        """
        if min_amount is None:
            min_amount = 0

        found: list[MoneroAccount] = self.get_unlocked_accounts(wallet, num_subaddresses, min_amount)
        if len(found) > 0:
            logger.debug(f"Wallet already has an account with {num_subaddresses} unlocked subaddresses")
            return

        # start mining, unless the blocks are generated on each iteration (regtest at a low difficulty)
        mining_started: bool = False
        if not is_generation_fast(self._daemon) and not self._daemon.get_mining_status().is_active:
            try:
                self._daemon.start_mining(self._mining_address, 1, False, False)
                mining_started = True
            except Exception as e:
                logger.warning(f"An error occurred while starting mining: {str(e)}")
                # no problem

        logger.info(f"Waiting for an account with {num_subaddresses} unlocked subaddresses")
        deadline: float = monotonic() + self.WAIT_TIMEOUT_SECONDS
        try:
            while len(found) == 0:
                if monotonic() > deadline:
                    raise TimeoutError(f"No account has {num_subaddresses} unlocked subaddresses after {self.WAIT_TIMEOUT_SECONDS:.0f}s")
                if not self._generate_block():
                    self._sleep()
                wallet.sync()
                found = self.get_unlocked_accounts(wallet, num_subaddresses, min_amount)
        finally:
            # stop mining if started
            if mining_started:
                self._daemon.stop_mining()

