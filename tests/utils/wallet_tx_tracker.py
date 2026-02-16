import logging

from time import sleep
from monero import MoneroDaemon, MoneroWallet, MoneroTxQuery

logger: logging.Logger = logging.getLogger("WalletTxTracker")


class WalletTxTracker:
    """
    Tracks wallets which are in sync with the tx pool and therefore whose txs in the pool
    do not need to be waited on for up-to-date pool information e.g. to create txs.

    This is only necessary because txs relayed outside wallets are not fully incorporated
    into the wallet state until confirmed.

    TODO monero-project: sync txs relayed outside wallet so this class is unecessary.
    """

    _daemon: MoneroDaemon
    """Daemon test instance"""
    _sync_period_ms: int
    """Sync period in milliseconds"""
    _mining_address: str
    """Mining address"""

    def __init__(self, daemon: MoneroDaemon, sync_period_ms: int, mining_address: str) -> None:
        """
        Initialize a new WalletTxTracker.

        :param MoneroDaemon daemon: Daemon test instance.
        :param int sync_period_ms: Sync period in ms.
        :param str mining_address: Address used for mining.
        """
        self._daemon = daemon
        self._sync_period_ms = sync_period_ms
        self._mining_address = mining_address

    def _wait_for_txs_to_clear(self, clear_from_wallet: bool, wallets: list[MoneroWallet]) -> None:
        """
        Docstring for _wait_for_txs_to_clear

        :param bool clear_from_wallet: Clear txs from wallet
        :param list[MoneroWallet] wallets: Wallets to clear
        """
        # loop until pending txs cleared
        is_first: bool = True
        mining_started: bool = False
        while True:
            # get pending wallet tx hashes
            tx_hashes_wallet: set[str] = set()
            for wallet in wallets:
                wallet.sync()
                query = MoneroTxQuery()
                query.in_tx_pool = True
                for tx in wallet.get_txs(query):
                    assert tx.hash is not None
                    if tx.is_relayed is not True:
                        continue
                    elif tx.is_failed:
                        # flush tx if failed
                        self._daemon.flush_tx_pool(tx.hash)
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
                        self._daemon.flush_tx_pool(tx.hash)
                    elif tx.hash in tx_hashes_wallet:
                        tx_hashes_pool.add(tx.hash)

            # break if no txs to wait for
            if len(tx_hashes_pool) == 0:
                if mining_started:
                    # stop mining if started
                    self._daemon.stop_mining()
                break

            # log message and start mining if first iteration
            if is_first:
                is_first = False
                logger.info(f"Waiting for wallet txs to clear from the pool in order to fully sync and avoid double spend attempts: {tx_hashes_pool}")
                mining_status = self._daemon.get_mining_status()
                if mining_status.is_active is not True:
                    try:
                        self._daemon.start_mining(self._mining_address, 1, False, False)
                        mining_started = True
                    except Exception as e:
                        logger.debug(f"Error: {e}")
                        # no problem

            # sleep for sync period
            sleep(self._sync_period_ms / 1000)

    def wait_for_txs_to_clear_pool(self, wallets: list[MoneroWallet] | MoneroWallet) -> None:
        """
        Wait for pending wallet transactions to clear the pool.

        :param list[MoneroWallet] wallets: Wallets to wait for pending transactions.
        """
        if isinstance(wallets, MoneroWallet):
            self._wait_for_txs_to_clear(False, [wallets])
        else:
            self._wait_for_txs_to_clear(False, wallets)

    def wait_for_txs_to_clear_wallets(self, wallets: list[MoneroWallet]) -> None:
        """
        Wait for pending wallet transactions to clear from the wallets.

        :param list[MoneroWallet] wallets: Wallets to wait for pending transactions.
        """
        self._wait_for_txs_to_clear(True, wallets)

    def wait_for_unlocked_balance(
            self, wallet: MoneroWallet,
            account_index: int, subaddress_index: int | None = None, min_amount: int | None = None
    ) -> int:
        """
        Wait for wallet unlocked balance

        :param wallet: Wallet to wait for unlocked balance
        :param account_index: Wallet account index
        :param subaddress_index: Wallet subaddress index
        :param min_amount: Minimum amount to wait for
        :return: Unlocked balance
        """
        if min_amount is None:
            min_amount = 0

        # check if wallet has balance
        err = Exception("Wallet does not have enough balance to wait for") 
        if subaddress_index is not None and wallet.get_balance(account_index, subaddress_index) < min_amount:
            raise err
        elif subaddress_index is None and wallet.get_balance(account_index) < min_amount:
            raise err

        # check if wallet has unlocked balance
        if subaddress_index is not None:
            unlocked_balance = wallet.get_unlocked_balance(account_index, subaddress_index)
        else:
            unlocked_balance = wallet.get_unlocked_balance(account_index)

        if unlocked_balance > min_amount:
            return unlocked_balance

        # start mining
        mining_started: bool = False
        if not self._daemon.get_mining_status().is_active:
            try:
                self._daemon.start_mining(self._mining_address, 1, False, False)
                mining_started = True
            except Exception as e:
                logger.debug(f"Error: {str(e)}")
                # no problem

        # wait for unlocked balance // TODO: promote to MoneroWallet interface?
        logger.info("Waiting for unlocked balance")

        while unlocked_balance < min_amount:
            if subaddress_index is not None:
                unlocked_balance = wallet.get_unlocked_balance(account_index, subaddress_index)
            else:
                unlocked_balance = wallet.get_unlocked_balance(account_index)

            sleep(self._sync_period_ms / 1000)

        # stop mining if started
        if mining_started:
            self._daemon.stop_mining()

        return unlocked_balance
