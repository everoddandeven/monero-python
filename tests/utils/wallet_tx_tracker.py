from time import sleep

from monero import MoneroDaemon, MoneroWallet
from .const import MINING_ADDRESS


class WalletTxTracker:

    _cleared_wallets: set[MoneroWallet]

    def __init__(self) -> None:
        self._cleared_wallets = set()

    def reset(self) -> None:
        self._cleared_wallets.clear()

    def wait_for_wallet_txs_to_clear_pool(
            self, daemon: MoneroDaemon, sync_period_ms: int, wallets: list[MoneroWallet]
    ) -> None:
        # get wallet tx hashes
        tx_hashes_wallet: set[str] = set()

        for wallet in wallets:
            if wallet not in self._cleared_wallets:
                wallet.sync()
                for tx in wallet.get_txs():
                    assert tx.hash is not None
                    tx_hashes_wallet.add(tx.hash)

        # loop until all wallet txs clear from pool
        is_first: bool = True
        mining_started: bool = False
        # daemon = TestUtils.getDaemonRpc()
        while True:
            # get hashes of relayed, non-failed txs in the pool
            tx_hashes_pool: set[str] = set()
            for tx in daemon.get_tx_pool():
                assert tx.hash is not None
                if not tx.is_relayed:
                    continue
                elif tx.is_failed:
                    daemon.flush_tx_pool(tx.hash) # flush tx if failed
                else:
                    tx_hashes_pool.add(tx.hash)

            # get hashes to wait for as intersection of wallet and pool txs
            tx_hashes_pool = tx_hashes_pool.intersection(tx_hashes_wallet)

            # break if no txs to wait for
            if len(tx_hashes_pool) == 0:
                break

            # if first time waiting, log message and start mining
            if is_first:
                is_first = False
                print("Waiting for wallet txs to clear from the pool in order to fully sync and avoid double spend attempts (known issue)")
                mining_status = daemon.get_mining_status()
                if not mining_status.is_active:
                    try:
                        daemon.start_mining(MINING_ADDRESS, 1, False, False)
                        mining_started = True
                    except Exception as e: # no problem
                        print(f"[!]: {str(e)}")

            # sleep for a moment
            sleep(sync_period_ms)

        # stop mining if started mining
        if mining_started:
            daemon.stop_mining()

        # sync wallets with the pool
        for wallet in wallets:
            wallet.sync()
            self._cleared_wallets.add(wallet)

    @classmethod
    def wait_for_unlocked_balance(
            cls, daemon: MoneroDaemon, sync_period_ms: int, wallet: MoneroWallet,
            account_index: int, subaddress_index: int | None, min_amount: int | None = None
    ) -> int:
        if min_amount is None:
            min_amount = 0

        # check if wallet has balance
        if subaddress_index is not None and wallet.get_balance(account_index, subaddress_index) < min_amount:
            raise Exception("Wallet does not have enough balance to wait for")
        elif subaddress_index is None and wallet.get_balance(account_index) < min_amount:
            raise Exception("Wallet does not have enough balance to wait for")

        # check if wallet has unlocked balance
        if subaddress_index is not None:
            unlocked_balance = wallet.get_unlocked_balance(account_index, subaddress_index)
        else:
            unlocked_balance = wallet.get_unlocked_balance(account_index)

        if unlocked_balance > min_amount:
            return unlocked_balance

        # start mining
        # daemon = TestUtils.getDaemonRpc()
        mining_started: bool = False
        if not daemon.get_mining_status().is_active:
            try:
                daemon.start_mining(MINING_ADDRESS, 1, False, False)
                mining_started = True
            except Exception as e:
                print(f"[!]: {str(e)}")

        # wait for unlocked balance // TODO: promote to MoneroWallet interface?
        print("Waiting for unlocked balance")
        while unlocked_balance < min_amount:
            if subaddress_index is not None:
                unlocked_balance = wallet.get_unlocked_balance(account_index, subaddress_index)
            else:
                unlocked_balance = wallet.get_unlocked_balance(account_index)

            try:
                sleep(sync_period_ms)
            except Exception as e:
                print(f"[!]: {str(e)}")

        # stop mining if started
        if mining_started:
            daemon.stop_mining()

        return unlocked_balance
