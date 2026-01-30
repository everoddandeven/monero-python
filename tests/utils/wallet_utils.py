import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroNetworkType, MoneroUtils, MoneroAccount,
    MoneroSubaddress
)

from .gen_utils import GenUtils
from .assert_utils import AssertUtils

logger: logging.Logger = logging.getLogger("WalletUtils")


class WalletUtils(ABC):

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
