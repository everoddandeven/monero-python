from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAccount,
    MoneroDestination,
    MoneroIntegratedAddress,
    MoneroMessageSignatureResult,
    MoneroMessageSignatureType,
    MoneroSubaddress,
    MoneroTxConfig,
    MoneroUtils,
    MoneroWallet,
    MoneroWalletConfig,
    MoneroWalletKeys,
)
from typing_extensions import override

from utils import AssertUtils, TestUtils, TestUtils as Utils, WalletErrorUtils, WalletTestUtils, WalletUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletKeysAndAddresses")


class BaseTestMoneroWalletKeysAndAddresses(BaseTestMoneroWallet):
    """Common wallet keys and addresses tests."""

    # Can get the seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_seed(self, wallet: MoneroWallet) -> None:
        seed: str = wallet.get_seed()
        MoneroUtils.validate_mnemonic(seed)
        assert TestUtils.SEED == seed

    # Can get the language of the seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_seed_language(self, wallet: MoneroWallet) -> None:
        language: str = wallet.get_seed_language()
        assert MoneroWallet.DEFAULT_LANGUAGE == language

    # Can get a list of supported languages for the seed
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_seed_languages(self) -> None:
        languages: list[str] = self._get_seed_languages()
        assert len(languages) > 0
        for language in languages:
            assert len(language) > 0

    # Can get the private view key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_private_view_key(self, wallet: MoneroWallet) -> None:
        private_view_key: str = wallet.get_private_view_key()
        MoneroUtils.validate_private_view_key(private_view_key)

    # Can get the private spend key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_private_spend_key(self, wallet: MoneroWallet) -> None:
        private_spend_key: str = wallet.get_private_spend_key()
        MoneroUtils.validate_private_spend_key(private_spend_key)

    # Can get the public view key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_public_view_key(self, wallet: MoneroWallet) -> None:
        public_view_key: str = wallet.get_public_view_key()
        MoneroUtils.validate_private_spend_key(public_view_key)

    # Can get the public spend key
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_public_spend_key(self, wallet: MoneroWallet) -> None:
        public_spend_key: str = wallet.get_public_spend_key()
        MoneroUtils.validate_private_spend_key(public_spend_key)

    # Can get the primary address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_primary_address(self, wallet: MoneroWallet) -> None:
        primary_address: str = wallet.get_primary_address()
        MoneroUtils.validate_address(primary_address, TestUtils.NETWORK_TYPE)
        assert wallet.get_address(0, 0) == primary_address

    # Can get the address of a subaddress at a specified account and subaddress index
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_address(self, wallet: MoneroWallet) -> None:
        assert wallet.get_primary_address() == wallet.get_address(0, 0)
        for account in wallet.get_accounts(True):
            for subaddress in account.subaddresses:
                assert account.index is not None
                assert subaddress.index is not None
                assert subaddress.address == wallet.get_address(account.index, subaddress.index)

    # Can get addresses out of range of used accounts and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        account_idx: int = len(accounts) - 1
        subaddress_idx: int = len(accounts[account_idx].subaddresses)
        address: str = wallet.get_address(account_idx, subaddress_idx)
        assert address is not None
        assert len(address) > 0

    # Can get the account and subaddress indices of an address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_address_indices(self, wallet: MoneroWallet) -> None:
        # get last subaddress to test
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        account_idx: int = len(accounts) - 1
        subaddress_idx: int = len(accounts[account_idx].subaddresses) - 1
        address: str = wallet.get_address(account_idx, subaddress_idx)
        assert address is not None
        assert len(address) > 0

        # get address index
        subaddress: MoneroSubaddress = wallet.get_address_index(address)
        assert account_idx == subaddress.account_index
        assert subaddress_idx == subaddress.index

        # test valid but unfound address
        non_wallet_address: str = WalletTestUtils.get_external_wallet_address()
        with pytest.raises(Exception) as exc_info:
            wallet.get_address_index(non_wallet_address)
        assert str(exc_info.value) == "Address doesn't belong to the wallet"

        # test invalid address
        with pytest.raises(Exception) as exc_info:
            wallet.get_address_index("this is definitely not an address")
        WalletErrorUtils.test_invalid_address_error(exc_info.value)

    # Can decode an integrated address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_decode_integrated_address(self, wallet: MoneroWallet) -> None:
        integrated_address: MoneroIntegratedAddress = wallet.get_integrated_address('', "03284e41c342f036")
        decoded_address: MoneroIntegratedAddress = wallet.decode_integrated_address(integrated_address.integrated_address)
        AssertUtils.assert_equals(integrated_address, decoded_address)

        # decode invalid address
        with pytest.raises(Exception) as exc_info:
            wallet.decode_integrated_address("bad address")
        WalletErrorUtils.test_invalid_address_error(exc_info.value)

        # decode invalid payment id
        with pytest.raises(Exception) as exc_info:
            wallet.get_integrated_address(wallet.get_primary_address(), "invalid payment id")
        assert str(exc_info.value) == "Invalid payment ID: invalid payment id"

    # Can sign and verify messages
    # TODO test with view-only wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sign_and_verify_messages(self, wallet: MoneroWallet) -> None:
        msg: str =  "This is a super important message which needs to be signed and verified."
        subaddress1: MoneroSubaddress = MoneroSubaddress()
        subaddress1.account_index = 0
        subaddress1.index = 0
        subaddress2: MoneroSubaddress = MoneroSubaddress()
        subaddress2.account_index = 0
        subaddress2.index = 1
        subaddress3: MoneroSubaddress = MoneroSubaddress()
        subaddress3.account_index = 1
        subaddress3.index = 0
        subaddresses: list[MoneroSubaddress] = [subaddress1, subaddress2, subaddress3]

        # test signing message with subaddresses
        for subaddress in subaddresses:
            assert subaddress.account_index is not None
            assert subaddress.index is not None
            account_idx: int = subaddress.account_index
            idx: int = subaddress.index

            # sign and verify message with spend key
            signature: str = wallet.sign_message(msg, MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY, account_idx, idx)
            result: MoneroMessageSignatureResult = wallet.verify_message(msg, wallet.get_address(account_idx, idx), signature)
            WalletUtils.test_message_signature_result(result, True)
            assert result.signature_type == MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY

            # verify message with incorrect address
            result = wallet.verify_message(msg, wallet.get_address(0, 2), signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with invalid address
            result = wallet.verify_message(msg, "invalid address", signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with external address
            result = wallet.verify_message(msg, WalletTestUtils.get_external_wallet_address(), signature)
            WalletUtils.test_message_signature_result(result, False)

            # sign and verify message with view key
            signature = wallet.sign_message(msg, MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY, account_idx, idx)
            result = wallet.verify_message(msg, wallet.get_address(account_idx, idx), signature)
            WalletUtils.test_message_signature_result(result, True)
            assert result.signature_type == MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY

            # verify message with incorrect address
            result = wallet.verify_message(msg, wallet.get_address(0, 2), signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with invalid address
            result = wallet.verify_message(msg, "invalid address", signature)
            WalletUtils.test_message_signature_result(result, False)

            # verify message with external address
            result = wallet.verify_message(msg, WalletTestUtils.get_external_wallet_address(), signature)
            WalletUtils.test_message_signature_result(result, False)

    # Can convert between a tx config and payment URI
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_payment_uri(self, wallet: MoneroWallet) -> None:
        # test with address and amount
        config1: MoneroTxConfig = MoneroTxConfig()
        dest: MoneroDestination = MoneroDestination()
        dest.address = wallet.get_address(0, 0)
        dest.amount = 0
        config1.destinations.append(dest)
        uri: str = wallet.get_payment_uri(config1)
        config2: MoneroTxConfig = wallet.parse_payment_uri(uri)
        AssertUtils.assert_equals(config1, config2)

        # test with subaddress and all fields
        subaddress: MoneroSubaddress = wallet.get_subaddress(0, 1)
        assert subaddress.address is not None
        config1.destinations[0].address = subaddress.address
        config1.destinations[0].amount = 425000000000
        config1.recipient_name = "John Doe"
        config1.note = "OMZG XMR FTW"
        uri = wallet.get_payment_uri(config1)
        config2 = wallet.parse_payment_uri(uri)
        AssertUtils.assert_equals(config1, config2)

        # test with undefined address
        address: str | None = config1.destinations[0].address
        config1.destinations[0].address = None
        with pytest.raises(Exception, match="Cannot make URI from supplied parameters"):
            wallet.get_payment_uri(config1)

        config1.destinations[0].address = address

        # test with standalone payment id
        config1.payment_id = "03284e41c342f03603284e41c342f03603284e41c342f03603284e41c342f036"
        with pytest.raises(Exception, match="Cannot make URI from supplied parameters"):
            wallet.get_payment_uri(config1)


@pytest.mark.integration
class TestMoneroWalletFullKeysAndAddresses(FullWalletSupport, BaseTestMoneroWalletKeysAndAddresses):
    """Full wallet keys and addresses integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcKeysAndAddresses(RpcWalletSupport, BaseTestMoneroWalletKeysAndAddresses):
    """Rpc wallet keys and addresses integration tests."""

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        account_idx: int = len(accounts) - 1
        subaddress_idx: int = len(accounts[account_idx].subaddresses)
        address: str = wallet.get_address(account_idx, subaddress_idx)
        assert address is None or len(address) == 0

    @pytest.mark.not_supported
    @override
    def test_get_seed_language(self, wallet: MoneroWallet) -> None:
        return super().test_get_seed_language(wallet)

    @pytest.mark.xfail(reason="TODO monero-project")
    @override
    def test_get_public_view_key(self, wallet: MoneroWallet) -> None:
        return super().test_get_public_view_key(wallet)

    @pytest.mark.xfail(reason="TODO monero-project")
    @override
    def test_get_public_spend_key(self, wallet: MoneroWallet) -> None:
        return super().test_get_public_spend_key(wallet)


@pytest.mark.unit
class TestMoneroWalletKeysKeysAndAddresses(KeysWalletSupport, BaseTestMoneroWalletKeysAndAddresses):
    """Keys-only wallet keys and addresses unit tests."""

    @pytest.mark.not_supported
    @override
    def test_get_address_indices(self, wallet: MoneroWallet) -> None:
        return super().test_get_address_indices(wallet)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address(self, wallet: MoneroWallet) -> None:
        assert wallet.get_primary_address() == (wallet.get_address(0, 0))
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet, True)

        for account in accounts:
            assert account is not None
            assert account.index is not None
            assert account.primary_address is not None
            MoneroUtils.validate_address(account.primary_address, Utils.NETWORK_TYPE)

            for subaddress in account.subaddresses:
                assert subaddress is not None
                assert subaddress.index is not None
                assert subaddress.address == wallet.get_address(account.index, subaddress.index)

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = self._get_test_accounts(wallet, True)
        account_idx: int = len(accounts) - 1
        subaddress_idx: int = len(accounts[account_idx].subaddresses)
        address: str = wallet.get_address(account_idx, subaddress_idx)
        assert address is not None
        assert len(address) > 0

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_integrated_address_with_empty_standard_address(self) -> None:
        """An empty standard_address uses the wallet's own primary address (account 0, subaddress 0)."""
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            integrated: MoneroIntegratedAddress = w.get_integrated_address("", "a" * 16)
            assert integrated.standard_address == w.get_primary_address()
            assert integrated.payment_id == "a" * 16
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_integrated_address_with_standard_address(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            address: str = w.get_primary_address()
            integrated: MoneroIntegratedAddress = w.get_integrated_address(address, "b" * 16)
            assert integrated.standard_address == address
            assert integrated.payment_id == "b" * 16
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_integrated_address_invalid_address_raises(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            with pytest.raises(RuntimeError, match="Invalid address"):
                w.get_integrated_address("notanaddress", "a" * 16)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_integrated_address_subaddress_raises(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            subaddress: str = w.get_address(1, 1)
            with pytest.raises(RuntimeError, match="Subaddress shouldn't be used"):
                w.get_integrated_address(subaddress, "a" * 16)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_integrated_address_already_integrated_raises(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            integrated: str = w.get_integrated_address("", "a" * 16).integrated_address
            with pytest.raises(RuntimeError, match="Already integrated address"):
                w.get_integrated_address(integrated, "a" * 16)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_integrated_address_missing_payment_id_raises(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            with pytest.raises(RuntimeError, match="Payment ID shouldn't be left unspecified"):
                w.get_integrated_address(w.get_primary_address(), "")
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sign_message_invalid_signature_type_base_address_raises(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            invalid_type: MoneroMessageSignatureType = MoneroMessageSignatureType(99) # type: ignore
            with pytest.raises(RuntimeError, match="Invalid signature type requested"):
                w.sign_message("hello", invalid_type, 0, 0)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_sign_message_invalid_signature_type_subaddress_raises(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            invalid_type: MoneroMessageSignatureType = MoneroMessageSignatureType(99) # type: ignore
            with pytest.raises(RuntimeError, match="Invalid signature type requested"):
                w.sign_message("hello", invalid_type, 1, 1)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_verify_message_no_signature_header(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            result: MoneroMessageSignatureResult = w.verify_message("hello", w.get_primary_address(), "not-a-signature")
            WalletUtils.test_message_signature_result(result, False)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_verify_message_invalid_base58(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            result: MoneroMessageSignatureResult = w.verify_message("hello", w.get_primary_address(), "SigV2!!!not-base58!!!")
            WalletUtils.test_message_signature_result(result, False)
        finally:
            w.close()

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_verify_message_wrong_decoded_size(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.network_type = Utils.NETWORK_TYPE
        w: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        try:
            address: str = w.get_primary_address()
            signature: str = w.sign_message("hello", MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY, 0, 0)
            # truncate the base58 payload so it decodes to fewer bytes than crypto::signature expects
            truncated: str = signature[:5] + signature[5:-10]
            result: MoneroMessageSignatureResult = w.verify_message("hello", address, truncated)
            WalletUtils.test_message_signature_result(result, False)
        finally:
            w.close()
