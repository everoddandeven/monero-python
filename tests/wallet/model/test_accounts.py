from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAccount,
    MoneroAccountTag,
    MoneroAddressBookEntry,
    MoneroAddressType,
    MoneroDecodedAddress,
    MoneroIntegratedAddress,
    MoneroNetworkType,
    MoneroSubaddress,
)

from utils import AssertUtils, BaseTestClass, TestUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelAccounts")


@pytest.mark.unit
class TestMoneroWalletModelAccounts(BaseTestClass):
    """Wallet account model unit tests."""

    def test_subaddress_deserialize(self) -> None:
        subaddress: MoneroSubaddress = MoneroSubaddress()
        subaddress.account_index = 0
        subaddress.index = 1
        subaddress.address = TestUtils.ADDRESS
        subaddress.label = "primary"
        subaddress.balance = 1000000
        subaddress.unlocked_balance = 900000
        subaddress.is_used = True
        subaddress.num_unspent_outputs = 3
        subaddress.num_blocks_to_unlock = 0
        AssertUtils.assert_serialization_integrity(subaddress)

    def test_account_deserialize(self) -> None:
        account: MoneroAccount = MoneroAccount()
        account.index = 0
        account.balance = 1000000
        account.unlocked_balance = 900000
        account.primary_address = TestUtils.ADDRESS
        account.tag = "savings"
        # subaddresses is serialized as a sub-array but from_property_tree() never
        # reads it back (see test below)
        AssertUtils.assert_serialization_integrity(account)

    def test_account_subaddresses_deserialize(self) -> None:
        account: MoneroAccount = MoneroAccount()
        account.subaddresses = [MoneroSubaddress()]
        json_str: str = account.serialize()
        logger.debug(f"Serialized account: {json_str}")
        assert "subaddresses" in json_str
        restored: MoneroAccount = MoneroAccount.deserialize(json_str)
        logger.debug(f"Deserialized account re-serialized: {restored.serialize()}")
        assert len(restored.subaddresses) == len(account.subaddresses)

    def test_integrated_address_deserialize(self) -> None:
        address: MoneroIntegratedAddress = MoneroIntegratedAddress()
        address.standard_address = TestUtils.ADDRESS
        address.payment_id = "d" * 16
        address.integrated_address = TestUtils.ADDRESS
        AssertUtils.assert_serialization_integrity(address)

    def test_address_book_entry_deserialize(self) -> None:
        entry: MoneroAddressBookEntry = MoneroAddressBookEntry()
        entry.index = 0
        entry.address = TestUtils.ADDRESS
        entry.description = "friend"
        entry.payment_id = "e" * 16
        AssertUtils.assert_serialization_integrity(entry)

    def test_address_book_entry_constructor_with_payment_id_deserialize(self) -> None:
        entry: MoneroAddressBookEntry = MoneroAddressBookEntry(0, TestUtils.ADDRESS, "friend", "e" * 16)
        assert entry.index == 0
        assert entry.address == TestUtils.ADDRESS
        assert entry.description == "friend"
        assert entry.payment_id == "e" * 16
        AssertUtils.assert_serialization_integrity(entry)

    def test_account_tag_deserialize(self) -> None:
        tag: MoneroAccountTag = MoneroAccountTag()
        tag.tag = "savings"
        tag.label = "Savings accounts"
        tag.account_indices = [0, 1, 2]
        AssertUtils.assert_serialization_integrity(tag)

    def test_account_tag_constructor_deserialize(self) -> None:
        tag: MoneroAccountTag = MoneroAccountTag("savings", "Savings accounts")
        assert tag.tag == "savings"
        assert tag.label == "Savings accounts"
        assert len(tag.account_indices) == 0
        AssertUtils.assert_serialization_integrity(tag)

    def test_decoded_address_deserialize(self) -> None:
        address: MoneroDecodedAddress = MoneroDecodedAddress(
            TestUtils.ADDRESS, MoneroAddressType.PRIMARY_ADDRESS, MoneroNetworkType.MAINNET
        )
        AssertUtils.assert_serialization_integrity(address)

    @pytest.mark.parametrize("json_fragment", [
        '{"networkType":-1}',
        '{"networkType":3}',
        '{"addressType":-1}',
        '{"addressType":3}',
    ])
    def test_decoded_address_invalid_enum_range(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="Invalid (network|address) type"):
            MoneroDecodedAddress.deserialize(json_fragment)
