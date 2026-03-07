import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroNetworkType, MoneroUtils, MoneroAccount,
    MoneroSubaddress, MoneroWalletKeys, MoneroWalletConfig,
    MoneroMessageSignatureResult, MoneroWallet,
    MoneroTxWallet, MoneroWalletFull, MoneroWalletRpc,
    MoneroTxConfig, MoneroDestination
)

from .gen_utils import GenUtils
from .assert_utils import AssertUtils
from .test_utils import TestUtils
from .single_tx_sender import SingleTxSender
from .to_multiple_tx_sender import ToMultipleTxSender
from .from_multiple_tx_sender import FromMultipleTxSender

logger: logging.Logger = logging.getLogger("WalletUtils")


class WalletUtils(ABC):
    """Wallet test utilities"""

    MAX_TX_PROOFS: Optional[int] = 25
    """maximum number of transactions to check for each proof, undefined to check all"""

    #region Test Utils

    @classmethod
    def test_invalid_address(cls, address: Optional[str], network_type: MoneroNetworkType) -> None:
        if address is None:
            return

        AssertUtils.assert_false(MoneroUtils.is_valid_address(address, network_type))

        try:
            MoneroUtils.validate_address(address, network_type)
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_private_view_key(cls, private_view_key: Optional[str]):
        if private_view_key is None:
            return

        AssertUtils.assert_false(MoneroUtils.is_valid_private_view_key(private_view_key))

        try:
            MoneroUtils.validate_private_view_key(private_view_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_public_view_key(cls, public_view_key: Optional[str]) -> None:
        if public_view_key is None:
            return

        AssertUtils.assert_false(MoneroUtils.is_valid_public_view_key(public_view_key))

        try:
            MoneroUtils.validate_public_view_key(public_view_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_private_spend_key(cls, private_spend_key: Optional[str]):
        if private_spend_key is None:
            return

        AssertUtils.assert_false(MoneroUtils.is_valid_private_spend_key(private_spend_key))

        try:
            MoneroUtils.validate_private_spend_key(private_spend_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_public_spend_key(cls, public_spend_key: Optional[str]):
        if public_spend_key is None:
            return

        AssertUtils.assert_false(MoneroUtils.is_valid_public_spend_key(public_spend_key))
        try:
            MoneroUtils.validate_public_spend_key(public_spend_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            AssertUtils.assert_false(len(str(e)) == 0)

    @classmethod
    def test_account(cls, account: Optional[MoneroAccount], network_type: MoneroNetworkType, full: bool = True):
        """Test a monero wallet account"""
        # test account
        assert account is not None
        assert account.index is not None
        assert account.index >= 0
        assert account.primary_address is not None

        MoneroUtils.validate_address(account.primary_address, network_type)
        if full:
            GenUtils.test_unsigned_big_integer(account.balance)
            GenUtils.test_unsigned_big_integer(account.unlocked_balance)

            # if given, test subaddresses and that their balances add up to account balances
            if len(account.subaddresses) > 0:
                balance = 0
                unlocked_balance = 0
                i = 0
                j = len(account.subaddresses)
                while i < j:
                    cls.test_subaddress(account.subaddresses[i])
                    assert account.index == account.subaddresses[i].account_index
                    assert i == account.subaddresses[i].index
                    address_balance = account.subaddresses[i].balance
                    assert address_balance is not None
                    balance += address_balance
                    address_balance = account.subaddresses[i].unlocked_balance
                    assert address_balance is not None
                    unlocked_balance += address_balance
                    i += 1

                msg1 = f"Subaddress balances {balance} != account {account.index} balance {account.balance}"
                msg2 =  f"Subaddress unlocked balances {unlocked_balance} != account {account.index} unlocked balance {account.unlocked_balance}"
                assert account.balance == balance, msg1
                assert account.unlocked_balance == unlocked_balance, msg2

        # tag must be undefined or non-empty
        tag = account.tag
        assert tag is None or len(tag) > 0

    @classmethod
    def test_subaddress(cls, subaddress: Optional[MoneroSubaddress], full: bool = True):
        assert subaddress is not None
        assert subaddress.account_index is not None
        assert subaddress.index is not None
        if full:
            assert subaddress.balance is not None
            assert subaddress.num_unspent_outputs is not None
            assert subaddress.num_blocks_to_unlock is not None
            GenUtils.test_unsigned_big_integer(subaddress.balance)
            GenUtils.test_unsigned_big_integer(subaddress.unlocked_balance)
            AssertUtils.assert_true(subaddress.num_unspent_outputs >= 0)
            AssertUtils.assert_not_none(subaddress.is_used)
            if subaddress.balance > 0:
                AssertUtils.assert_true(subaddress.is_used)
            AssertUtils.assert_true(subaddress.num_blocks_to_unlock >= 0)

        AssertUtils.assert_true(subaddress.account_index >= 0)
        AssertUtils.assert_true(subaddress.index >= 0)
        AssertUtils.assert_not_none(subaddress.address)
        # TODO fix monero-cpp/monero_wallet_full.cpp to return boost::none on empty label
        #AssertUtils.assert_true(subaddress.label is None or subaddress.label != "")

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

    # Convenience method for single tx send tests
    @classmethod
    def test_send_to_single(cls, wallet: MoneroWallet, can_split: bool, relay: Optional[bool] = None, payment_id: Optional[str] = None) -> None:
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
        assert error is not None
        err_msg: str = str(error)
        assert err_msg == "No wallet file", err_msg

    #endregion

    @classmethod
    def get_external_wallet_address(cls) -> str:
        """
        Return an external wallet address

        :returns str: external wallet address
        """
        network_type: MoneroNetworkType | None = TestUtils.get_daemon_rpc().get_info().network_type

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
        """Create random wallet used as spam destinations"""
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
        """Check if wallet has required funds"""
        amount_per_address = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_required_per_account = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required = amount_required_per_account * num_accounts
        required_subaddresses: int = num_accounts * (num_subaddresses + 1) # include primary address

        if isinstance(wallet, MoneroWalletFull) or isinstance(wallet, MoneroWalletRpc):
            wallet.sync()
        else:
            return False

        wallet_balance = wallet.get_balance()

        if wallet_balance < amount_required:
            return False

        accounts = wallet.get_accounts(True)
        subaddresses_found: int = 0
        num_wallet_accounts = len(accounts)

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
        Fund a wallet with mined coins

        :param MoneroWallet wallet: wallet to fund with mined coins
        :param float xmr_amount_per_address: XMR amount to fund each address
        :param int num_accounts: number of accounts to fund
        :param int num_subaddresses: number of subaddress to fund for each account
        :returns list[MoneroTxWallet] | None: Funding transactions created from mining wallet
        """
        primary_addr = wallet.get_primary_address()
        if cls.is_wallet_funded(wallet, xmr_amount_per_address, num_accounts, num_subaddresses):
            logger.debug(f"Already funded wallet {primary_addr}")
            return []

        amount_per_address = MoneroUtils.xmr_to_atomic_units(xmr_amount_per_address)
        amount_per_account = amount_per_address * (num_subaddresses + 1) # include primary address
        amount_required = amount_per_account * num_accounts
        amount_required_str = f"{MoneroUtils.atomic_units_to_xmr(amount_required)} XMR"

        logger.debug(f"Funding wallet {primary_addr} with {amount_required_str}...")

        tx_config = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.relay = True
        tx_config.can_split = True

        supports_get_accounts = isinstance(wallet, MoneroWalletRpc) or isinstance(wallet, MoneroWalletFull)
        while supports_get_accounts and len(wallet.get_accounts()) < num_accounts:
            wallet.create_account()

        for account_idx in range(num_accounts):
            account = wallet.get_account(account_idx)
            num_subaddr = len(account.subaddresses)

            while num_subaddr < num_subaddresses:
                wallet.create_subaddress(account_idx)
                num_subaddr += 1

            addresses = wallet.get_subaddresses(account_idx, list(range(num_subaddresses + 1)))
            for address in addresses:
                assert address.address is not None
                dest = MoneroDestination(address.address, amount_per_address)
                tx_config.destinations.append(dest)

        mining_wallet = TestUtils.get_mining_wallet()
        wallet_balance = mining_wallet.get_balance()
        err_msg = f"Mining wallet doesn't have enough balance: {MoneroUtils.atomic_units_to_xmr(wallet_balance)}"
        assert wallet_balance > amount_required, err_msg
        txs = mining_wallet.create_txs(tx_config)
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
