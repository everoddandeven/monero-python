from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroCheck,
    MoneroCheckReserve,
    MoneroCheckTx,
    MoneroKeyImage,
    MoneroKeyImageExportResult,
    MoneroKeyImageImportResult,
    MoneroMessageSignatureResult,
    MoneroMessageSignatureType,
    MoneroMultisigInfo,
    MoneroMultisigInitResult,
    MoneroMultisigSignResult,
    MoneroSyncResult,
)

from utils import AssertUtils, BaseTestClass, TestUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelResults")


@pytest.mark.unit
class TestMoneroWalletModelResults(BaseTestClass):
    """Wallet result model unit tests."""

    def test_key_image_import_result_deserialize(self) -> None:
        result: MoneroKeyImageImportResult = MoneroKeyImageImportResult()
        result.height = 3000000
        result.spent_amount = 500000
        result.unspent_amount = 1500000
        AssertUtils.assert_serialization_integrity(result)

    def test_message_signature_result_deserialize(self) -> None:
        result: MoneroMessageSignatureResult = MoneroMessageSignatureResult()
        result.is_good = True
        result.is_old = False
        result.version = 2
        result.signature_type = MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY
        AssertUtils.assert_serialization_integrity(result)

    def test_message_signature_result_invalid_signature_type_deserialize(self) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            MoneroMessageSignatureResult.deserialize('{"signatureType": "bogus"}')
        assert str(exc_info.value) == "Invalid message signature type: bogus"

    def test_check_tx_deserialize(self) -> None:
        check: MoneroCheckTx = MoneroCheckTx()
        check.is_good = True
        check.in_tx_pool = False
        check.num_confirmations = 10
        check.received_amount = 500000
        AssertUtils.assert_serialization_integrity(check)

    def test_check_reserve_deserialize(self) -> None:
        check: MoneroCheckReserve = MoneroCheckReserve()
        check.is_good = True
        check.total_amount = 1000000
        check.unconfirmed_spent_amount = 0
        AssertUtils.assert_serialization_integrity(check)

    def test_multisig_info_deserialize(self) -> None:
        info: MoneroMultisigInfo = MoneroMultisigInfo()
        info.is_multisig = True
        info.is_ready = True
        info.threshold = 2
        info.num_participants = 3
        AssertUtils.assert_serialization_integrity(info)

    def test_multisig_init_result_deserialize(self) -> None:
        result: MoneroMultisigInitResult = MoneroMultisigInitResult()
        result.address = TestUtils.ADDRESS
        result.multisig_hex = "deadbeef"
        AssertUtils.assert_serialization_integrity(result)

    def test_multisig_sign_result_deserialize(self) -> None:
        result: MoneroMultisigSignResult = MoneroMultisigSignResult()
        result.signed_multisig_tx_hex = "deadbeef"
        result.tx_hashes = ["a" * 64, "b" * 64]
        AssertUtils.assert_serialization_integrity(result)

    def test_sync_result_deserialize(self) -> None:
        result: MoneroSyncResult = MoneroSyncResult()
        result.num_blocks_fetched = 42
        result.received_money = True
        AssertUtils.assert_serialization_integrity(result)

    def test_check_deserialize(self) -> None:
        check: MoneroCheck = MoneroCheck()
        check.is_good = True
        AssertUtils.assert_serialization_integrity(check)

    def test_key_image_export_result_deserialize(self) -> None:
        result: MoneroKeyImageExportResult = MoneroKeyImageExportResult()
        result.offset = 3
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        result.key_images = [key_image]
        AssertUtils.assert_serialization_integrity(result)
