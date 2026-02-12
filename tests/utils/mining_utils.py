import logging

from typing import Optional
from monero import (
    MoneroDaemonRpc, MoneroWallet, MoneroUtils,
    MoneroDestination, MoneroTxConfig, MoneroTxWallet,
    MoneroWalletFull, MoneroWalletRpc
)
from .test_utils import TestUtils as Utils

logger: logging.Logger = logging.getLogger("MiningUtils")


class MiningUtils:
    """
    Mining utilities.
    """
    _DAEMON: Optional[MoneroDaemonRpc] = None
    """Internal mining daemon."""

    @classmethod
    def get_daemon(cls) -> MoneroDaemonRpc:
        """
        Get internal mining daemon.
        """
        if cls._DAEMON is None:
            cls._DAEMON = MoneroDaemonRpc("127.0.0.1:18089")

        return cls._DAEMON

    @classmethod
    def is_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Check if mining is enabled.
        """
        # max tries 3
        daemon = cls.get_daemon() if d is None else d
        for i in range(3):
            try:
                status = daemon.get_mining_status()
                return status.is_active is True

            except Exception as e:
                if i == 2:
                    raise e

        return False

    @classmethod
    def start_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> None:
        """
        Start internal mining.
        """
        if cls.is_mining():
            raise Exception("Mining already started")

        daemon = cls.get_daemon() if d is None else d
        daemon.start_mining(Utils.MINING_ADDRESS, 1, False, False)

    @classmethod
    def stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> None:
        """
        Stop internal mining.
        """
        if not cls.is_mining():
            raise Exception("Mining already stopped")

        daemon = cls.get_daemon() if d is None else d
        daemon.stop_mining()

    @classmethod
    def try_stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Try stop internal mining.
        """
        try:
            cls.stop_mining(d)
            return True
        except Exception as e:
            logger.warning(f"MiningUtils.stop_mining(): {e}")
            return False

    @classmethod
    def try_start_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Try start internal mining.
        """
        try:
            cls.start_mining(d)
            return True
        except Exception as e:
            logger.warning(f"MiningUtils.start_mining(): {e}")
            return False

    @classmethod
    def is_wallet_funded(cls, wallet: MoneroWallet, xmr_amount_per_address: float, num_subaddresses: int = 10) -> bool:
        """Check if wallet has required funds"""
        amount_per_address = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required = amount_per_address * (num_subaddresses + 1) # include primary address

        if isinstance(wallet, MoneroWalletFull) or isinstance(wallet, MoneroWalletRpc):
            wallet.sync()
        else:
            return False

        if wallet.get_balance() < amount_required:
            return False

        accounts = wallet.get_accounts(True)
        subaddresses_found: int = 0
        for account in accounts:
            for subaddress in account.subaddresses:
                balance = subaddress.unlocked_balance
                assert balance is not None
                if balance >= amount_per_address:
                    subaddresses_found += 1

        return subaddresses_found >= num_subaddresses + 1

    @classmethod
    def fund_wallet(cls, wallet: MoneroWallet, xmr_amount_per_address: float, num_subaddresses: int = 10) -> Optional[MoneroTxWallet]:
        """Fund a wallet with mined coins"""
        primary_addr = wallet.get_primary_address()
        if cls.is_wallet_funded(wallet, xmr_amount_per_address, num_subaddresses):
            logger.debug(f"Already funded wallet {primary_addr}")
            return None

        amount_per_address = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required_str = f"{MoneroUtils.atomic_units_to_xmr(amount_required)} XMR"

        logger.debug(f"Funding wallet {primary_addr}...")

        tx_config = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.relay = True

        account_idx = 0
        account = wallet.get_account(account_idx)
        num_subaddr = len(account.subaddresses)

        while num_subaddr < num_subaddresses:
            wallet.create_subaddress(account_idx)
            num_subaddr += 1

        addresses = wallet.get_subaddresses(0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        for address in addresses:
            assert address.address is not None
            dest = MoneroDestination(address.address, amount_per_address)
            tx_config.destinations.append(dest)

        mining_wallet = Utils.get_mining_wallet()
        wallet_balance = mining_wallet.get_balance()
        err_msg = f"Mining wallet doesn't have enough balance: {MoneroUtils.atomic_units_to_xmr(wallet_balance)}"
        assert wallet_balance > amount_required, err_msg
        tx = mining_wallet.create_tx(tx_config)
        assert tx.is_failed is False, "Cannot fund wallet: tx failed"
        logger.debug(f"Funded test wallet {primary_addr} with {amount_required_str} in tx {tx.hash}")

        return tx
