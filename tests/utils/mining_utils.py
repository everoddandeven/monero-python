import logging

from typing import Optional
from time import sleep
from monero import (
    MoneroDaemonRpc, MoneroWallet, MoneroUtils,
    MoneroDestination, MoneroTxConfig
)
from .test_utils import TestUtils as Utils
from .string_utils import StringUtils

logger: logging.Logger = logging.getLogger("MiningUtils")


class MiningUtils:
    """
    Mining utilities.
    """
    _DAEMON: Optional[MoneroDaemonRpc] = None
    """Internal mining daemon."""

    @classmethod
    def _get_daemon(cls) -> MoneroDaemonRpc:
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
        daemon = cls._get_daemon() if d is None else d
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

        daemon = cls._get_daemon() if d is None else d
        daemon.start_mining(Utils.MINING_ADDRESS, 1, False, False)

    @classmethod
    def stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> None:
        """
        Stop internal mining.
        """
        if not cls.is_mining():
            raise Exception("Mining already stopped")

        daemon = cls._get_daemon() if d is None else d
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
    def wait_for_height(cls, height: int) -> int:
        """
        Wait for blockchain height.
        """
        daemon = cls._get_daemon()
        current_height = daemon.get_height()
        if height <= current_height:
            return current_height

        stop_mining: bool = False
        if not cls.is_mining():
            cls.start_mining()
            stop_mining = True

        while current_height < height:
            p = StringUtils.get_percentage(current_height, height)
            logger.info(f"[{p}] Waiting for blockchain height ({current_height}/{height})")
            block = daemon.wait_for_next_block_header()
            assert block.height is not None
            current_height = block.height
            sleep(5)

        if stop_mining:
            cls.stop_mining()
            sleep(5)
            current_height = daemon.get_height()

        logger.info(f"[100%] Reached blockchain height: {current_height}")

        return current_height

    @classmethod
    def wait_until_blockchain_ready(cls) -> int:
        """
        Wait until blockchain is ready.
        """
        height = cls.wait_for_height(Utils.MIN_BLOCK_HEIGHT)
        cls.try_stop_mining()
        return height

    @classmethod
    def has_reached_height(cls, height: int) -> bool:
        """Check if blockchain has reached height"""
        return height == cls._get_daemon().get_height()

    @classmethod
    def blockchain_is_ready(cls) -> bool:
        """Indicates if blockchain has reached minimum height for running tests"""
        return cls.has_reached_height(Utils.MIN_BLOCK_HEIGHT)

    @classmethod
    def is_wallet_funded(cls, wallet: MoneroWallet, xmr_amount_per_address: float, num_subaddresses: int = 10) -> bool:
        """Check if wallet has required funds"""
        amount_per_address = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required = amount_per_address * (num_subaddresses + 1) # include primary address
        wallet.sync()

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
    def fund_wallet(cls, wallet: MoneroWallet, xmr_amount_per_address: float, num_subaddresses: int = 10) -> None:
        """Fund a wallet with mined coins"""
        primary_addr = wallet.get_primary_address()
        if cls.is_wallet_funded(wallet, xmr_amount_per_address, num_subaddresses):
            logger.info(f"Already funded wallet {primary_addr}")
            return

        amount_per_address = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required_str = f"{MoneroUtils.atomic_units_to_xmr(amount_required)} XMR"

        logger.info(f"Funding wallet {primary_addr}...")

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
        logger.info(f"Funded test wallet {primary_addr} with {amount_required_str} in tx {tx.hash}")
        height = cls._get_daemon().get_height()
        cls.wait_for_height(height + 11)
        wallet.sync()
