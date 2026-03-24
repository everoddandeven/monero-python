import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroNetworkType, MoneroUtils, MoneroAccount,
    MoneroSubaddress, MoneroWalletKeys, MoneroWalletConfig,
    MoneroMessageSignatureResult, MoneroWallet,
    MoneroTxWallet, MoneroWalletFull, MoneroWalletRpc,
    MoneroTxConfig, MoneroDestination, MoneroAddressBookEntry
)

from .gen_utils import GenUtils
from .test_utils import TestUtils
from .single_tx_sender import SingleTxSender
from .to_multiple_tx_sender import ToMultipleTxSender
from .from_multiple_tx_sender import FromMultipleTxSender
from .wallet_sweeper import WalletSweeper

logger: logging.Logger = logging.getLogger("WalletUtils")


class WalletUtils(ABC):
    """Wallet test utilities"""

    WALLET_IS_CLOSED_ERROR: str = "Wallet is closed"
    """Wallet is closed error message"""

    MAX_TX_PROOFS: Optional[int] = 25
    """maximum number of transactions to check for each proof, undefined to check all"""

    #region Test Utils

    @classmethod
    def test_invalid_address(cls, address: Optional[str], network_type: MoneroNetworkType) -> None:
        """
        Test and assert invalid wallet address.

        :param str | None address: invalid address to test.
        :param MoneroNetworkType network_type: address network type.
        """
        if address is None:
            return

        assert MoneroUtils.is_valid_address(address, network_type) is False

        try:
            MoneroUtils.validate_address(address, network_type)
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert "Should have thrown exception" != e_msg, e_msg

    @classmethod
    def test_invalid_private_view_key(cls, private_view_key: Optional[str]) -> None:
        """
        Test and assert invalid wallet private view key.

        :param str | None private_view_key: invalid private view key to test.
        """
        if private_view_key is None:
            return

        assert MoneroUtils.is_valid_private_view_key(private_view_key) is False

        try:
            MoneroUtils.validate_private_view_key(private_view_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert "Should have thrown exception" != e_msg, e_msg

    @classmethod
    def test_invalid_public_view_key(cls, public_view_key: Optional[str]) -> None:
        """
        Test and assert invalid wallet public view key.

        :param str | None public_view_key: invalid public view key to test.
        """
        if public_view_key is None:
            return

        assert MoneroUtils.is_valid_public_view_key(public_view_key) is False

        try:
            MoneroUtils.validate_public_view_key(public_view_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert "Should have thrown exception" != e_msg, e_msg

    @classmethod
    def test_invalid_private_spend_key(cls, private_spend_key: Optional[str]) -> None:
        """
        Test and assert invalid wallet private spend key.

        :param str | None private_spend_key: invalid private spend key to test.
        """
        if private_spend_key is None:
            return

        assert MoneroUtils.is_valid_private_spend_key(private_spend_key) is False

        try:
            MoneroUtils.validate_private_spend_key(private_spend_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert "Should have thrown exception" != e_msg, e_msg

    @classmethod
    def test_invalid_public_spend_key(cls, public_spend_key: Optional[str]) -> None:
        """
        Test and assert invalid wallet public spend key.

        :param str | None public_spend_key: invalid public spend key to test.
        """
        if public_spend_key is None:
            return

        assert MoneroUtils.is_valid_public_spend_key(public_spend_key) is False
        try:
            MoneroUtils.validate_public_spend_key(public_spend_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            e_msg: str = str(e)
            assert "Should have thrown exception" != e_msg, e_msg

    @classmethod
    def test_account(cls, account: Optional[MoneroAccount], network_type: MoneroNetworkType, full: bool = True) -> None:
        """
        Test a monero wallet account

        :param MoneroAccount | None account: wallet account to test.
        :param MoneroNetworkType: wallet network type.
        :param bool full: validates also `balance`, `unlocked_balance` and `subaddresses` (default `True`).
        """
        # test account
        assert account is not None
        assert account.index is not None
        assert account.index >= 0
        assert account.primary_address is not None

        MoneroUtils.validate_address(account.primary_address, network_type)
        if full:
            GenUtils.test_unsigned_big_integer(account.balance)
            GenUtils.test_unsigned_big_integer(account.unlocked_balance)
            num_subadresses: int = len(account.subaddresses)

            # if given, test subaddresses and that their balances add up to account balances
            if num_subadresses > 0:
                balance: int = 0
                unlocked_balance: int = 0

                for i in range(num_subadresses):
                    cls.test_subaddress(account.subaddresses[i])
                    assert account.index == account.subaddresses[i].account_index
                    assert i == account.subaddresses[i].index
                    address_balance = account.subaddresses[i].balance
                    assert address_balance is not None
                    balance += address_balance
                    address_balance = account.subaddresses[i].unlocked_balance
                    assert address_balance is not None
                    unlocked_balance += address_balance

                msg1: str = f"Subaddress balances {balance} != account {account.index} balance {account.balance}"
                msg2: str =  f"Subaddress unlocked balances {unlocked_balance} != account {account.index} unlocked balance {account.unlocked_balance}"
                assert account.balance == balance, msg1
                assert account.unlocked_balance == unlocked_balance, msg2

        # tag must be undefined or non-empty
        assert account.tag is None or len(account.tag) > 0

    @classmethod
    def test_subaddress(cls, subaddress: Optional[MoneroSubaddress], full: bool = True) -> None:
        """
        Test a monero wallet subaddress.

        :param MoneroSubaddress | None subaddress: wallet subaddress to test.
        :param bool full: test also `balance`, `unlocked_balance`, `num_unspent_outputs` and `num_blocks_to_unlock` (default `True`).
        """
        assert subaddress is not None
        assert subaddress.account_index is not None
        assert subaddress.index is not None
        if full:
            assert subaddress.balance is not None
            assert subaddress.num_unspent_outputs is not None
            assert subaddress.num_blocks_to_unlock is not None
            GenUtils.test_unsigned_big_integer(subaddress.balance)
            GenUtils.test_unsigned_big_integer(subaddress.unlocked_balance)
            assert subaddress.num_unspent_outputs >= 0
            assert subaddress.is_used is not None
            if subaddress.balance > 0:
                assert subaddress.is_used
            assert subaddress.num_blocks_to_unlock >= 0

        assert subaddress.account_index >= 0
        assert subaddress.index >= 0
        assert subaddress.address is not None
        assert len(subaddress.address) > 0
        assert subaddress.label is None or subaddress.label != ""

    @classmethod
    def test_message_signature_result(cls, result: Optional[MoneroMessageSignatureResult], is_good: bool) -> None:
        assert result is not None
        if is_good:
            assert result.is_good is True
            assert result.is_old is False
            assert result.version == 2
        else:
            # TODO set boost::optional in monero-cpp?
            assert result.is_good is False
            assert result.is_old is False
            #assert result.signature_type is None
            assert result.version == 0

    @classmethod
    def test_address_book_entry(cls, entry: Optional[MoneroAddressBookEntry]) -> None:
        """
        Test a monero address book entry.

        :param MoneroAddressBookEntry | None entry: entry to test.
        """
        assert entry is not None
        assert entry.index is not None
        assert entry.index >= 0
        assert entry.address is not None
        MoneroUtils.validate_address(entry.address, TestUtils.NETWORK_TYPE)
        assert entry.description is not None

    # Convenience method for single tx send tests
    @classmethod
    def test_send_to_single(cls, wallet: MoneroWallet, can_split: bool, relay: Optional[bool] = None, payment_id: Optional[str] = None) -> None:
        """
        Test creating transaction and sending to single destination.

        :param MoneroWallet wallet: wallet to send funds from.
        :param bool can_split: Can split transactions.
        :param bool | None relay: Relay created transaction(s).
        :param str | None payment_id: Transaction payment id.
        """
        config = MoneroTxConfig()
        config.can_split = can_split
        config.relay = relay
        config.payment_id = payment_id
        sender = SingleTxSender(wallet, config)
        sender.send()

    # Convenience method for sending funds from multiple sources
    @classmethod
    def test_send_from_multiple(cls, wallet: MoneroWallet, can_split: bool | None) -> None:
        sender: FromMultipleTxSender = FromMultipleTxSender(wallet, can_split)
        sender.send()

    # Convenience method for multiple tx send tests
    @classmethod
    def test_send_to_multiple(
                            cls,
                            wallet: MoneroWallet,
                            num_accounts: int,
                            num_subaddresses_per_account: int,
                            can_split: bool,
                            send_amount_per_subaddress: Optional[int] = None,
                            subtract_fee_from_destinations: bool = False
                            ) -> None:
        sender: ToMultipleTxSender = ToMultipleTxSender(
            wallet, num_accounts, num_subaddresses_per_account,
            can_split, send_amount_per_subaddress, subtract_fee_from_destinations)
        sender.send()

    @classmethod
    def test_no_wallet_file_error(cls, error: Optional[Exception]) -> None:
        """
        Test for `No wallet file` monero error.

        :param Exception | None error: error to test.
        """
        assert error is not None
        err_msg: str = str(error)
        assert err_msg == "No wallet file", err_msg

    @classmethod
    def test_wallet_is_closed_error(cls, error: Optional[Exception]) -> None:
        """
        Test for `Wallet is closed` monero error.

        :param Exception | None error: error to test.
        """
        assert error is not None
        err_msg: str = str(error)
        assert err_msg == cls.WALLET_IS_CLOSED_ERROR, err_msg

    #endregion

    @classmethod
    def get_external_wallet_address(cls) -> str:
        """
        Gets an external wallet address.

        :returns str: external wallet address.
        """
        network_type: MoneroNetworkType | None = TestUtils.NETWORK_TYPE

        if network_type == MoneroNetworkType.STAGENET:
            # subaddress
            return "78Zq71rS1qK4CnGt8utvMdWhVNMJexGVEDM2XsSkBaGV9bDSnRFFhWrQTbmCACqzevE8vth9qhWfQ9SUENXXbLnmMVnBwgW"
        if network_type == MoneroNetworkType.TESTNET:
            # subaddress
            return "BhsbVvqW4Wajf4a76QW3hA2B3easR5QdNE5L8NwkY7RWXCrfSuaUwj1DDUsk3XiRGHBqqsK3NPvsATwcmNNPUQQ4SRR2b3V"
        if network_type == MoneroNetworkType.MAINNET:
            # subaddress
            return "87a1Yf47UqyQFCrMqqtxfvhJN9se3PgbmU7KUFWqhSu5aih6YsZYoxfjgyxAM1DztNNSdoYTZYn9xa3vHeJjoZqdAybnLzN"
        else:
            raise Exception("Invalid network type: " + str(network_type))

    @classmethod
    def select_subaddress_with_min_balance(cls, wallet: MoneroWallet, min_balance: int, skip_primary: bool = True) -> Optional[MoneroSubaddress]:
        """
        Select a wallet subaddress with minimum unlocked balance.

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
    def create_random_wallets(cls, network_type: MoneroNetworkType, n: int = 10) -> list[MoneroWalletKeys]:
        """
        Create random wallet used as spam destinations.

        :param MoneroNetworkType network_type: Network type.
        :param int n: number of wallets to create.
        :returns list[MoneroWalletKeys]: random wallets created.
        """
        assert n >= 0, "n must be >= 0"
        wallets: list[MoneroWalletKeys] = []
        # setup basic wallet config
        config = MoneroWalletConfig()
        config.network_type = network_type
        # create n random wallets
        for i in range(n):
            logger.debug(f"Creating random wallet ({i})...")
            wallet = MoneroWalletKeys.create_wallet_random(config)
            logger.debug(f"Created random wallet ({i}): {wallet.get_primary_address()}")
            wallets.append(wallet)

        return wallets

    @classmethod
    def is_wallet_funded(cls, wallet: MoneroWallet, xmr_amount_per_address: float, num_accounts: int, num_subaddresses: int) -> bool:
        """
        Check if wallet has required funds.

        :param MoneroWallet wallet: wallet to check balance.
        :param float xmr_amount_per_address: human readable xmr amount to check per address.
        :param int num_accounts: number of wallet accounts to check balance.
        :param int num_subaddresses: number of wallet subaddresses to check balance for each `num_accounts`.
        :return bool: `True` if `wallet` has enough balance, `False` otherwise.
        """
        amount_per_address: int = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required_per_account: int = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required: int = amount_required_per_account * num_accounts
        required_subaddresses: int = num_accounts * (num_subaddresses + 1) # include primary address

        if isinstance(wallet, MoneroWalletFull) or isinstance(wallet, MoneroWalletRpc):
            wallet.sync()
        else:
            return False

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
    def fund_wallet(cls, wallet: MoneroWallet, xmr_amount_per_address: float = 10, num_accounts: int = 3, num_subaddresses: int = 5) -> list[MoneroTxWallet]:
        """
        Fund a wallet with mined coins.

        :param MoneroWallet wallet: wallet to fund with mined coins.
        :param float xmr_amount_per_address: XMR amount to fund each address.
        :param int num_accounts: number of accounts to fund.
        :param int num_subaddresses: number of subaddress to fund for each account.
        :returns list[MoneroTxWallet] | None: Funding transactions created from mining wallet.
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

        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.relay = True
        tx_config.can_split = True

        supports_get_accounts: bool = isinstance(wallet, MoneroWalletRpc) or isinstance(wallet, MoneroWalletFull)
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
                assert address.address is not None
                dest = MoneroDestination(address.address, amount_per_address)
                tx_config.destinations.append(dest)

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

        if supports_get_accounts:
            wallet.save()

        logger.debug(f"Funded test wallet {primary_addr} with {sent_amount_xmr_str} in {len(txs)} txs")

        return txs

    @classmethod
    def test_sweep_wallet(cls, wallet: MoneroWallet, sweep_each_subaddress: Optional[bool]) -> None:
        """
        Test creating sweep wallet transaction.

        :param bool | None sweep_each_subaddress: sweep each wallet subaddresses.
        """
        sweeper: WalletSweeper = WalletSweeper(wallet, sweep_each_subaddress)
        sweeper.sweep()
