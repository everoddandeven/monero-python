import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroNetworkType, MoneroUtils, MoneroAccount, MoneroSubaddress,
    MoneroWallet, MoneroTxConfig, MoneroDestination,
    MoneroTxWallet, MoneroWalletFull, MoneroWalletRpc, MoneroWalletLight
)

from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("WalletTestUtils")


class WalletTestUtils(ABC):

    @classmethod
    def get_external_wallet_address(cls) -> str:
        """Gets an external wallet address.

        :returns str: external wallet address.
        """

        if TestUtils.NETWORK_TYPE == MoneroNetworkType.STAGENET:
            # stagenet subaddress
            return "78Zq71rS1qK4CnGt8utvMdWhVNMJexGVEDM2XsSkBaGV9bDSnRFFhWrQTbmCACqzevE8vth9qhWfQ9SUENXXbLnmMVnBwgW"

        if TestUtils.NETWORK_TYPE == MoneroNetworkType.TESTNET:
            # testnet subaddress
            return "BhsbVvqW4Wajf4a76QW3hA2B3easR5QdNE5L8NwkY7RWXCrfSuaUwj1DDUsk3XiRGHBqqsK3NPvsATwcmNNPUQQ4SRR2b3V"

        # mainnet subaddress
        return "87a1Yf47UqyQFCrMqqtxfvhJN9se3PgbmU7KUFWqhSu5aih6YsZYoxfjgyxAM1DztNNSdoYTZYn9xa3vHeJjoZqdAybnLzN"

    @classmethod
    def select_subaddress_with_min_balance(cls, wallet: MoneroWallet, min_balance: int, skip_primary: bool = True) -> Optional[MoneroSubaddress]:
        """Select a wallet subaddress with minimum unlocked balance.

        :param MoneroWallet wallet: wallet to select subaddress from.
        :param int min_balance: miniumum subaddress unlocked balance.
        :param bool skip_primary: skip primary account address (default `True`).
        :returns MoneroSubaddress | None: selected subaddress with unlocked `min_balance`, if any.
        """
        # get wallet accounts
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        for account in accounts:
            assert account.index is not None
            i: int = account.index
            for subaddress in account.subaddresses:
                assert subaddress.index is not None
                j: int = subaddress.index
                if i == 0 and j == 0 and skip_primary:
                    continue

                assert subaddress.unlocked_balance is not None
                if subaddress.unlocked_balance > min_balance - 1:
                    return subaddress

        return None

    @classmethod
    def is_wallet_funded(cls, wallet: MoneroWallet, xmr_amount_per_address: float, num_accounts: int, num_subaddresses: int) -> bool:
        """Check if wallet has required funds.

        :param MoneroWallet wallet: wallet to check balance.
        :param float xmr_amount_per_address: human readable xmr amount to check per address.
        :param int num_accounts: number of wallet accounts to check balance.
        :param int num_subaddresses: number of wallet subaddresses to check balance for each `num_accounts`.
        :returns bool: `True` if `wallet` has enough balance, `False` otherwise.
        """
        amount_per_address: int = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required_per_account: int = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required: int = amount_required_per_account * num_accounts
        required_subaddresses: int = num_accounts * (num_subaddresses + 1) # include primary address

        if not isinstance(wallet, (MoneroWalletFull, MoneroWalletRpc, MoneroWalletLight)):
            return False

        # sync wallet
        wallet.sync()
        wallet_balance: int = wallet.get_balance()

        if wallet_balance < amount_required:
            return False

        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        subaddresses_found: int = 0
        num_wallet_accounts: int = len(accounts)

        if num_wallet_accounts < num_accounts:
            return False

        for account in accounts:
            for subaddress in account.subaddresses:
                balance = subaddress.unlocked_balance
                assert balance is not None
                if balance >= amount_per_address:
                    subaddresses_found += 1

        return subaddresses_found >= required_subaddresses

    @classmethod
    def build_tx_config(
        cls,
        wallet: MoneroWallet,
        num_accounts: int,
        num_subaddresses: int,
        amount_per_address: int,
        supports_get_accounts: bool
    ) -> MoneroTxConfig:
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.relay = True
        tx_config.can_split = True

        while supports_get_accounts and len(wallet.get_accounts()) < num_accounts:
            wallet.create_account()

        for account_idx in range(num_accounts):
            account: MoneroAccount = wallet.get_account(account_idx)
            num_subaddr: int = len(account.subaddresses)

            while num_subaddr < num_subaddresses:
                wallet.create_subaddress(account_idx)
                num_subaddr += 1

            addresses: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx, list(range(num_subaddresses + 1)))
            for address in addresses:
                if address.unlocked_balance is not None and address.unlocked_balance >= amount_per_address:
                    # skip if subaddress already funded
                    continue

                assert address.address is not None
                dest = MoneroDestination(address.address, amount_per_address)
                tx_config.destinations.append(dest)

        return tx_config

    @classmethod
    def fund_wallet(
        cls,
        wallet: MoneroWallet,
        xmr_amount_per_address: float = 10,
        num_accounts: int = 3,
        num_subaddresses: int = 5,
        close_mining_wallet: bool = False) -> list[MoneroTxWallet]:
        """Fund a wallet with mined coins.

        :param MoneroWallet wallet: wallet to fund with mined coins.
        :param float xmr_amount_per_address: XMR amount to fund each address.
        :param int num_accounts: number of accounts to fund.
        :param int num_subaddresses: number of subaddress to fund for each account.
        :returns list[MoneroTxWallet]: Funding transactions created from mining wallet.
        """
        primary_addr: str = wallet.get_primary_address()
        if cls.is_wallet_funded(wallet, xmr_amount_per_address, num_accounts, num_subaddresses):
            logger.debug(f"Already funded wallet {primary_addr}")
            return []

        amount_per_address: int = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_per_account: int = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required: int = amount_per_account * num_accounts
        amount_required_str: str = f"{MoneroUtils.atomic_units_to_xmr(amount_required)} XMR"

        logger.debug(f"Funding wallet {primary_addr} with {amount_required_str}...")
        supports_get_accounts: bool = isinstance(wallet, MoneroWalletRpc) or isinstance(wallet, MoneroWalletFull) or isinstance(wallet, MoneroWalletLight)
        supports_save: bool = isinstance(wallet, MoneroWalletRpc) or isinstance(wallet, MoneroWalletFull)

        tx_config: MoneroTxConfig = cls.build_tx_config(wallet, num_accounts, num_subaddresses, amount_per_address, supports_get_accounts)

        mining_wallet: MoneroWalletFull = TestUtils.get_mining_wallet()
        wallet_balance: int = mining_wallet.get_balance()
        err_msg: str = f"Mining wallet doesn't have enough balance: {MoneroUtils.atomic_units_to_xmr(wallet_balance)}"
        assert wallet_balance > amount_required, err_msg

        txs: list[MoneroTxWallet] = mining_wallet.create_txs(tx_config)
        txs_amount: int = 0
        for tx in txs:
            assert tx.is_failed is False, "Cannot fund wallet: tx failed"
            tx_amount: int = tx.get_outgoing_amount()
            assert tx_amount > 0, "Tx outgoing amount should be > 0"
            txs_amount += tx_amount

        sent_amount_xmr_str: str = f"{MoneroUtils.atomic_units_to_xmr(txs_amount)} XMR"

        if supports_save:
            wallet.save()

        logger.debug(f"Funded test wallet {primary_addr} with {sent_amount_xmr_str} in {len(txs)} txs")

        # close mining wallet if requested
        if close_mining_wallet:
            mining_wallet.close()

        return txs

    @classmethod
    def fund_wallets(
        cls,
        wallets: list[MoneroWallet],
        xmr_amount_per_address: float = 10,
        num_accounts: int = 3,
        num_subaddresses: int = 5) -> list[MoneroTxWallet]:
        """Fund multiple wallets with mined coins.

        :param list[MoneroWallet] wallets: list of wallets to fund with mined coins.
        :param float xmr_amount_per_address: XMR amount to fund each address.
        :param int num_accounts: number of accounts to fund.
        :param int num_subaddresses: number of subaddress to fund for each account.
        :returns list[MoneroTxWallet]: Funding transactions created from mining wallet.
        """

        txs: list[MoneroTxWallet] = []
        num_wallets: int = len(wallets)

        for i, wallet in enumerate(wallets):
            last: bool = i == num_wallets - 1
            wallet_txs: list[MoneroTxWallet] = cls.fund_wallet(wallet, xmr_amount_per_address, num_accounts, num_subaddresses, last)
            assert len(wallet_txs) > 0, f"Could not fund test wallet ({i}): {wallet.get_primary_address()}"
            txs.extend(wallet_txs)

        return txs
