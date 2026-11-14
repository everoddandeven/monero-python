from __future__ import annotations

import logging
from typing import Optional

import pytest
from monero import (
    MoneroAccount,
    MoneroAccountTag,
    MoneroAddressBookEntry,
    MoneroIntegratedAddress,
    MoneroSubaddress,
    MoneroWallet,
    MoneroWalletFull,
    MoneroWalletRpc,
)
from typing_extensions import override

from utils import (
    AssertUtils,
    GenUtils,
    StringUtils,
    TestUtils,
    TestUtils as Utils,
    WalletTestUtils,
    WalletUtils,
)
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletAccounts")


class BaseTestMoneroWalletAccounts(BaseTestMoneroWallet):
    """Common wallet accounts tests."""

    # Can get the locked and unlocked balances of the wallet, accounts and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_all_balances(self, wallet: MoneroWallet) -> None:
        # fetch accounts with all info as reference
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        # test that balances add up between accounts and wallet
        accounts_balance: int = 0
        accounts_unlocked_balance: int = 0
        for account in accounts:
            assert account.index is not None
            assert account.balance is not None
            assert account.unlocked_balance is not None
            accounts_balance += account.balance
            accounts_unlocked_balance += account.unlocked_balance

            # test that balances add up between subaddresses and accounts
            subaddresses_balance: int = 0
            subaddresses_unlocked_balance: int = 0
            for subaddress in account.subaddresses:
                assert subaddress.account_index is not None
                assert subaddress.index is not None
                assert subaddress.balance is not None
                assert subaddress.unlocked_balance is not None
                subaddresses_balance += subaddress.balance
                subaddresses_unlocked_balance += subaddress.unlocked_balance

                # test that balances are consistent with get_accounts() call
                assert wallet.get_balance(subaddress.account_index, subaddress.index) == subaddress.balance
                unlocked_balance: int = wallet.get_unlocked_balance(subaddress.account_index, subaddress.index)
                assert unlocked_balance == subaddress.unlocked_balance

            assert wallet.get_balance(account.index) == subaddresses_balance
            assert wallet.get_unlocked_balance(account.index) == subaddresses_unlocked_balance

        GenUtils.test_unsigned_big_integer(accounts_balance)
        GenUtils.test_unsigned_big_integer(accounts_unlocked_balance)
        assert wallet.get_balance() == accounts_balance
        assert wallet.get_unlocked_balance() == accounts_unlocked_balance

    # Can get accounts without subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_accounts_without_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)
            assert len(account.subaddresses) == 0

    # Can get accounts with subaddress
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_accounts_with_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)
            assert len(account.subaddresses) > 0

    # Can get an account at a specified index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_account(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)

            # test without subaddresses
            assert account.index is not None
            retrieved: MoneroAccount = wallet.get_account(account.index)
            assert len(retrieved.subaddresses) == 0

            # test with subaddresses
            retrieved = wallet.get_account(account.index, True)
            assert len(retrieved.subaddresses) > 0

    # Can create a new account without a label
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_account_without_label(self, wallet: MoneroWallet) -> None:
        accounts_before: list[MoneroAccount] = wallet.get_accounts()
        created_account: MoneroAccount = wallet.create_account()
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)
        assert len(accounts_before) == len(wallet.get_accounts()) - 1

    # Can create a new account with a label
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_account_with_label(self, wallet: MoneroWallet) -> None:
        # create account with label
        accounts_before: list[MoneroAccount] = wallet.get_accounts()
        label: str = StringUtils.get_random_string()
        created_account: MoneroAccount = wallet.create_account(label)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)
        assert created_account.index is not None
        assert len(accounts_before) == len(wallet.get_accounts()) - 1
        assert label == wallet.get_subaddress(created_account.index, 0).label

        # fetch and test account
        created_account = wallet.get_account(created_account.index)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)

        # create account with same label
        created_account = wallet.create_account(label)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)
        assert len(accounts_before) == len(wallet.get_accounts()) - 2
        assert created_account.index is not None
        assert label == wallet.get_subaddress(created_account.index, 0).label

        # fetch and test account
        created_account = wallet.get_account(created_account.index)
        WalletUtils.test_account(created_account, TestUtils.NETWORK_TYPE)

    # Can set account labels
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_account_label(self, wallet: MoneroWallet) -> None:
        # create account
        if len(wallet.get_accounts()) < 2:
            wallet.create_account()

        # set account label
        label: str = StringUtils.get_random_string()
        wallet.set_account_label(1, label)
        assert label == wallet.get_subaddress(1, 0).label

    # Can get subaddresses at a aspecified account index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                WalletUtils.test_subaddress(subaddress)
                assert account.index == subaddress.account_index

    # Can get subaddresses at a specified account index and subaddress indices
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddresses_by_indices(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:

            # get subaddresses
            assert account.index is not None
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0

            # remove a subaddress for query if possible
            if len(subaddresses) > 1:
                subaddresses = list(filter(lambda sub: sub != subaddresses[0], subaddresses))

            # get subaddress indices
            subaddress_indices: list[int] = []
            for subaddress in subaddresses:
                assert subaddress.index is not None
                subaddress_indices.append(subaddress.index)
            assert len(subaddress_indices) > 0

            # fetch subaddresses by indices
            fetched_subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account.index, subaddress_indices)

            # original subaddresses (minus one removed if applicable) is equal to fetched subaddresses
            AssertUtils.assert_list_equals(subaddresses, fetched_subaddresses)

    # Can get subaddress at a specified account index and subaddress index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_by_index(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account.index)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                assert subaddress.index is not None
                WalletUtils.test_subaddress(subaddress)
                AssertUtils.assert_equals(subaddress, wallet.get_subaddress(account.index, subaddress.index))
                # test plural call with single subaddr number
                AssertUtils.assert_equals(
                    subaddress, wallet.get_subaddresses(account.index, [subaddress.index])[0]
                )

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_subaddress(self, wallet: MoneroWallet) -> None:
        # create subaddresses across accounts
        accounts: list[MoneroAccount] = wallet.get_accounts()
        if len(accounts) < 2:
            wallet.create_account()
        accounts = wallet.get_accounts()
        assert len(accounts) > 1
        account_idx: int = 0
        while account_idx < 2:

            # create subaddress with no label
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            subaddress: MoneroSubaddress = wallet.create_subaddress(account_idx)
            assert subaddress.label is None
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            assert len(subaddresses_new) - 1 == len(subaddresses)
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = wallet.get_subaddresses(account_idx)
            uuid: str = StringUtils.get_random_string()
            subaddress = wallet.create_subaddress(account_idx, uuid)
            assert (uuid == subaddress.label)
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses) == len(subaddresses_new) - 1
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            account_idx += 1

    # Can set subaddress labels
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_subaddress_label(self, wallet: MoneroWallet) -> None:
        # create subaddresses
        while len(wallet.get_subaddresses(0)) < 3:
            wallet.create_subaddress(0)

        # set subaddress labels
        subaddress_idx: int = 0
        while subaddress_idx < len(wallet.get_subaddresses(0)):
            label: str = StringUtils.get_random_string()
            wallet.set_subaddress_label(0, subaddress_idx, label)
            assert label == wallet.get_subaddress(0, subaddress_idx).label
            subaddress_idx += 1

    # Can tag accounts and query accounts by tag
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_account_tags(self, wallet: MoneroWallet) -> None:
        # get accounts
        accounts: list[MoneroAccount] = wallet.get_accounts()
        assert len(accounts) > 3,  "Not enough accounts to test; run create account test"

        # tag some of the accounts
        tag: MoneroAccountTag = MoneroAccountTag(f"my_tag_{StringUtils.get_random_string()}", "my tag label", [0, 1])
        assert tag.tag is not None
        assert tag.label is not None
        wallet.tag_accounts(tag.tag, tag.account_indices)

        # query accounts by tag
        tagged_accounts: list[MoneroAccount] = wallet.get_accounts(False, tag.tag)
        assert len(tagged_accounts) == 2
        assert tagged_accounts[0].index == 0
        assert tagged_accounts[0].tag == tag.tag
        assert tagged_accounts[1].index == 1
        assert tagged_accounts[1].tag == tag.tag

        # set tag label
        wallet.set_account_tag_label(tag.tag, tag.label)

        # fetch tags and ensure new tag is contained
        tags: list[MoneroAccountTag] = wallet.get_account_tags()
        found: bool = False
        for a_tag in tags:
            if a_tag.tag == tag.tag:
                found = True
                break
        assert found, f"Could not find tag: {tag.serialize()}"
        logger.debug(f"Found account tag: {tag.serialize()}")

        # re-tag an account
        tag2: MoneroAccountTag = MoneroAccountTag(f"my_tag_{StringUtils.get_random_string()}", "my tag label 2", [1])
        assert tag2.tag is not None
        assert tag2.label is not None
        wallet.tag_accounts(tag2.tag, tag2.account_indices)
        tagged_accounts2: list[MoneroAccount] = wallet.get_accounts(False, tag2.tag)
        assert len(tagged_accounts2) == 1
        assert tagged_accounts2[0].index == 1
        assert tagged_accounts2[0].tag == tag2.tag

        # re-query original tag which only applies to one account now
        tagged_accounts = wallet.get_accounts(False, tag.tag)
        assert len(tagged_accounts) == 1
        assert tagged_accounts[0].index == 0
        assert tagged_accounts[0].tag == tag.tag

        # untag and query accounts
        wallet.untag_accounts([0, 1])
        assert len(wallet.get_account_tags()) == 0
        with pytest.raises(Exception):
            wallet.get_accounts(False, tag.tag)

        # a never-registered tag may raise or return nothing; either is acceptable
        try:
            assert len(wallet.get_accounts(False, "non_existing_tag")) == 0
        except Exception as e:
            logger.debug(f"get_accounts with non-existing tag raised: {e}")

    # Has an address book
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_address_book(self, wallet: MoneroWallet) -> None:
        # initial state
        entries: list[MoneroAddressBookEntry] = wallet.get_address_book_entries()
        num_entries_start: int = len(entries)
        for entry in entries:
            WalletUtils.test_address_book_entry(entry)

        # test adding standard addresses
        NUM_ENTRIES: int = 5
        address: str = WalletTestUtils.get_external_wallet_address()
        indices: list[int] = []
        for i in range(NUM_ENTRIES):
            logger.debug(f"Adding address book entry ({i + 1})")
            indices.append(wallet.add_address_book_entry(address, "hi there!"))

        entries = wallet.get_address_book_entries()
        assert num_entries_start + NUM_ENTRIES == len(entries)
        for idx in indices:
            found: bool = False
            for entry in entries:
                if idx == entry.index:
                    WalletUtils.test_address_book_entry(entry)
                    assert entry.address == address
                    assert entry.description == "hi there!"
                    found = True
                    break

            assert found, f"Index {idx} not found in address book indices"

        # edit each address book entry
        for idx in indices:
            wallet.edit_address_book_entry(idx, False, '', True, "hello there!!")

        entries = wallet.get_address_book_entries(indices)
        for entry in entries:
            assert entry.description == "hello there!!"

        # delete entries at starting index
        delete_idx: int = indices[0]
        for i in range(len(indices)):
            logger.debug(f"Deleting address book entry {i + 1}, delete_idx: {delete_idx}")
            wallet.delete_address_book_entry(delete_idx)
        entries = wallet.get_address_book_entries()
        assert len(entries) == num_entries_start

        # test adding integrated addresses
        indices = []
        # payment id less one character
        payment_id: str = "03284e41c342f03"
        integrated_addresses: dict[int, MoneroIntegratedAddress] = {}
        integrated_descriptions: dict[int, str] = {}
        for i in range(NUM_ENTRIES):
            # create unique integrated address
            integrated_address: MoneroIntegratedAddress = wallet.get_integrated_address('', f"{payment_id}{i}")
            uuid: str = StringUtils.get_random_string()
            idx: int = wallet.add_address_book_entry(integrated_address.integrated_address, uuid)
            indices.append(idx)
            integrated_addresses[idx] = integrated_address
            integrated_descriptions[idx] = uuid

        entries = wallet.get_address_book_entries()
        assert len(entries) == num_entries_start + NUM_ENTRIES
        for idx in indices:
            found: bool = False
            for entry in entries:
                if idx == entry.index:
                    WalletUtils.test_address_book_entry(entry)
                    assert integrated_descriptions[idx] == entry.description
                    assert integrated_addresses[idx].integrated_address == entry.address
                    assert entry.payment_id is None
                    found = True
                    break
            assert found, f"Index {idx} not found in address bool indices"

        # delete entries at starting index
        delete_idx = indices[0]
        for i in range(len(indices)):
            logger.debug(f"Deleting address book entry {i + 1}")
            wallet.delete_address_book_entry(delete_idx)

        entries = wallet.get_address_book_entries()
        assert num_entries_start == len(entries)


@pytest.mark.integration
class TestMoneroWalletFullAccounts(FullWalletSupport, BaseTestMoneroWalletAccounts):
    """Full wallet accounts integration tests."""

    # TODO implement
    @pytest.mark.not_implemented
    @override
    def test_account_tags(self, wallet: MoneroWallet) -> None:
        return super().test_account_tags(wallet)

    # Can create a subaddress with and without a label
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_create_subaddress(self, wallet: MoneroWalletFull) -> None: # type: ignore
        # create subaddresses across accounts
        accounts: list[MoneroAccount] = wallet.get_accounts()
        if len(accounts) < 2:
            wallet.create_account()

        accounts = wallet.get_accounts()
        assert len(accounts) > 1
        account_idx: int = 0
        while account_idx < 2:
            # create subaddress with no label
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            subaddress: MoneroSubaddress = wallet.create_subaddress(account_idx)
            assert subaddress.label is None
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx)
            assert len(subaddresses_new) - 1 == len(subaddresses)
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])

            # create subaddress with label
            subaddresses = wallet.get_subaddresses(account_idx)
            uuid: str = StringUtils.get_random_string()
            subaddress = wallet.create_subaddress(account_idx, uuid)
            assert uuid == subaddress.label
            WalletUtils.test_subaddress(subaddress)
            subaddresses_new = wallet.get_subaddresses(account_idx)
            assert len(subaddresses) == len(subaddresses_new) - 1
            AssertUtils.assert_equals(subaddress, subaddresses_new[len(subaddresses_new) - 1])
            account_idx += 1


@pytest.mark.integration
class TestMoneroWalletRpcAccounts(RpcWalletSupport, BaseTestMoneroWalletAccounts):
    """Rpc wallet accounts integration tests."""

    # Can get a subaddress via monero_wallet_rpc's
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_rpc(self, wallet: MoneroWalletRpc) -> None:
        account_idx: int = 0
        subaddress_idx: int = 0

        subaddress: MoneroSubaddress = wallet.get_subaddress(account_idx, subaddress_idx)
        WalletUtils.test_subaddress(subaddress)
        assert subaddress.account_index == account_idx
        assert subaddress.index == subaddress_idx

        plural: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx, [subaddress_idx])
        assert len(plural) == 1
        AssertUtils.assert_equals(subaddress, plural[0])

        assert subaddress.address == wallet.get_address(account_idx, subaddress_idx)


@pytest.mark.unit
class TestMoneroWalletKeysAccounts(KeysWalletSupport, BaseTestMoneroWalletAccounts):
    """Keys-only wallet accounts unit tests."""

    def _get_subaddress(self, wallet: MoneroWallet, account_idx: int, subaddress_idx: int) -> Optional[MoneroSubaddress]:
        subaddress_indices: list[int] = [subaddress_idx]
        subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account_idx, subaddress_indices)

        if len(subaddresses) == 0:
            return None

        return subaddresses[0]

    @pytest.mark.not_supported
    @override
    def test_get_all_balances(self, wallet: MoneroWallet) -> None:
        return super().test_get_all_balances(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_account_without_label(self, wallet: MoneroWallet) -> None:
        return super().test_create_account_without_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_account_with_label(self, wallet: MoneroWallet) -> None:
        return super().test_create_account_with_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_account_label(self, wallet: MoneroWallet) -> None:
        return super().test_set_account_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_subaddresses_by_indices(self, wallet: MoneroWallet) -> None:
        return super().test_get_subaddresses_by_indices(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_subaddress(self, wallet: MoneroWallet) -> None:
        return super().test_create_subaddress(wallet)

    @override
    def test_set_subaddress_label(self, wallet: MoneroWallet) -> None:
        # a keys-only wallet cannot enumerate its subaddresses, which this test needs
        with pytest.raises(RuntimeError, match="does not have enumerable set of subaddresses"):
            super().test_set_subaddress_label(wallet)

    @pytest.mark.not_supported
    @override
    def test_address_book(self, wallet: MoneroWallet) -> None:
        return super().test_address_book(wallet)

    @pytest.mark.not_supported
    @override
    def test_account_tags(self, wallet: MoneroWallet) -> None:
        return super().test_account_tags(wallet)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_account(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, Utils.NETWORK_TYPE, False)

            # test without subaddresses
            assert account.index is not None
            retrieved: MoneroAccount = wallet.get_account(account.index)
            assert len(retrieved.subaddresses) == 0

            # test with subaddresses
            retrieved = wallet.get_account(account.index)
            retrieved.subaddresses = wallet.get_subaddresses(account.index, self._subaddress_indices)

    def test_get_account_with_subaddresses_not_supported(self, wallet: MoneroWallet) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            wallet.get_account(0, True)
        assert str(exc_info.value) == "monero_wallet_keys::get_account(account_idx, include_subaddresses) include_subaddresses must be false"

    @override
    def test_get_accounts_without_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, Utils.NETWORK_TYPE, False)
            assert len(account.subaddresses) == 0

    @override
    def test_get_accounts_with_subaddresses(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet, True)
        assert len(accounts) > 0
        for account in accounts:
            WalletUtils.test_account(account, Utils.NETWORK_TYPE, False)
            assert len(account.subaddresses) > 0

    @override
    def test_get_subaddresses(self, wallet: MoneroWallet) -> None:
        wallet = wallet
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account.index, self._subaddress_indices)
            assert len(subaddresses) > 0
            for subaddress in subaddresses:
                WalletUtils.test_subaddress(subaddress, False)
                assert account.index == subaddress.account_index

    @override
    def test_get_subaddress_by_index(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet)
        assert len(accounts) > 0
        for account in accounts:
            assert account.index is not None
            subaddresses: list[MoneroSubaddress] = wallet.get_subaddresses(account.index, self._subaddress_indices)
            assert len(subaddresses) > 0

            for subaddress in subaddresses:
                assert subaddress.index is not None
                WalletUtils.test_subaddress(subaddress, False)
                AssertUtils.assert_equals(subaddress, self._get_subaddress(wallet, account.index, subaddress.index))
                # test plural call with single subaddr number
                AssertUtils.assert_equals(
                    subaddress, wallet.get_subaddresses(account.index, [subaddress.index])[0]
                )
