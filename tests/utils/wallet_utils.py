import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroNetworkType, MoneroUtils, MoneroAccount,
    MoneroSubaddress, MoneroAddressBookEntry,
    MoneroMessageSignatureResult, MoneroWallet,
    MoneroTxConfig, MoneroMultisigInfo
)

from .gen_utils import GenUtils
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("WalletUtils")


class WalletUtils(ABC):
    """Wallet test utilities."""

    MAX_TX_PROOFS: Optional[int] = 25
    """maximum number of transactions to check for each proof, undefined to check all."""

    #region Test Utils

    @classmethod
    def test_invalid_address(cls, address: Optional[str], network_type: MoneroNetworkType) -> None:
        """Test and assert invalid wallet address.

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
        """Test and assert invalid wallet private view key.

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
        """Test and assert invalid wallet public view key.

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
        """Test and assert invalid wallet private spend key.

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
        """Test and assert invalid wallet public spend key.

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
        """Test a monero wallet account.

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
        """Test a monero wallet subaddress.

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
        """Test a monero message signature result.

        :param MoneroMessageSignatureResult | None result: signature result to test.
        :param bool is_good: expected good signature.
        """
        assert result is not None
        if is_good:
            assert result.is_good is True
            assert result.is_old is False
            assert result.version == 2
        else:
            assert result.is_good is False
            assert result.is_old is False
            #assert result.signature_type is None
            assert result.version == 0

    @classmethod
    def test_address_book_entry(cls, entry: Optional[MoneroAddressBookEntry]) -> None:
        """Test a monero address book entry.

        :param MoneroAddressBookEntry | None entry: entry to test.
        """
        assert entry is not None
        assert entry.index is not None
        assert entry.index >= 0
        assert entry.address is not None
        MoneroUtils.validate_address(entry.address, TestUtils.NETWORK_TYPE)
        assert entry.description is not None

    @classmethod
    def test_wallet_keys(cls, address: str, view_key: str, spend_key: str, w: MoneroWallet) -> None:
        """Test wallet keys.

        :param str address: expected primary address.
        :param str view_key: expected private view key.
        :param str spend_key: expected private spend key.
        :param MoneroWallet w: wallet to test keys.
        """

        assert address == w.get_primary_address()
        assert view_key == w.get_private_view_key()
        assert spend_key == w.get_private_spend_key()
        MoneroUtils.validate_mnemonic(w.get_seed())
        assert MoneroWallet.DEFAULT_LANGUAGE == w.get_seed_language()

    @classmethod
    def test_multisig_info(cls, info: MoneroMultisigInfo, threshold: int, num_participants: int) -> None:
        """Test multisignature wallet info.

        :param MoneroMultisigInfo info: wallet multisignature info to test.
        :param int threshold: expected multisig threshold.
        :param int num_participants: expected number of participants.
        """
        logger.debug(f"Testing multisig info: {info.serialize()}")
        assert info.is_multisig is True
        assert info.is_ready is True
        assert threshold == info.threshold
        assert num_participants == info.num_participants

    @classmethod
    def build_payment_uri_config(cls, address: str) -> MoneroTxConfig:
        tx_config = MoneroTxConfig()
        tx_config.address = address
        tx_config.amount = 250000000000
        tx_config.recipient_name = "John Doe"
        tx_config.note = "My transfer to wallet"

        return tx_config

    #endregion
