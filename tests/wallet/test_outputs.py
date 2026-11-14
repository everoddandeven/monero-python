from __future__ import annotations

import logging
from typing import Optional

import pytest
from monero import (
    MoneroAccount,
    MoneroDestination,
    MoneroKeyImage,
    MoneroKeyImageExportResult,
    MoneroKeyImageImportResult,
    MoneroOutputQuery,
    MoneroOutputWallet,
    MoneroSubaddress,
    MoneroTx,
    MoneroTxConfig,
    MoneroTxQuery,
    MoneroTxWallet,
    MoneroWallet,
)
from typing_extensions import override

from utils import GenUtils, OutputUtils, TestUtils, TxWalletUtils, WalletTestUtils, WalletTxsUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletOutputs")


class BaseTestMoneroWalletOutputs(BaseTestMoneroWallet):
    """Common wallet outputs tests."""

    # Can get outputs in the wallet, accounts, and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_outputs(self, wallet: MoneroWallet) -> None:
        # get all outputs
        OutputUtils.get_and_test_outputs(wallet, None, True)

        # get outputs for each account
        non_default_incoming: bool = False
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        for account in accounts:
            # determine if account is used
            is_used: bool = False
            for subaddress in account.subaddresses:
                if subaddress.is_used is True:
                    is_used = True
                    break

            # get outputs by account index
            output_query: MoneroOutputQuery = MoneroOutputQuery()
            output_query.account_index = account.index
            account_outputs: list[MoneroOutputWallet] = OutputUtils.get_and_test_outputs(wallet, output_query, is_used)
            for ouput in account_outputs:
                assert ouput.account_index == account.index

            # get outputs by subaddress index
            subaddress_outputs: list[MoneroOutputWallet] = []
            for subaddress in account.subaddresses:
                subaddr_query: MoneroOutputQuery = MoneroOutputQuery()
                subaddr_query.account_index = account.index
                subaddr_query.subaddress_index = subaddress.index
                outputs: list[MoneroOutputWallet] = OutputUtils.get_and_test_outputs(wallet, subaddr_query, subaddress.is_used)
                for output in outputs:
                    assert subaddress.account_index == output.account_index
                    assert subaddress.index == output.subaddress_index
                    if output.account_index != 0 and output.subaddress_index != 0:
                        non_default_incoming = True
                    subaddress_outputs.append(output)

            assert len(subaddress_outputs) == len(account_outputs)

            # get outputs by subaddress indices
            subaddress_indices: set[int] = set()
            for output in subaddress_outputs:
                assert output.subaddress_index is not None
                subaddress_indices.add(output.subaddress_index)

            output_query = MoneroOutputQuery()
            output_query.account_index = account.index
            for sub_idx in subaddress_indices:
                output_query.subaddress_indices.append(sub_idx)

            outputs = OutputUtils.get_and_test_outputs(wallet, output_query, is_used)
            assert len(outputs) == len(subaddress_outputs)

            for output in outputs:
                assert account.index == output.account_index
                assert output.subaddress_index is not None
                assert output.subaddress_index in subaddress_indices

        # ensure output found with non-zero account and subaddress indices
        assert non_default_incoming, "No outputs found in non-default account and subaddress; run send-to-multiple tests"

    # Can get outputs with additional configuration
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_outputs_with_query(self, wallet: MoneroWallet) -> None:
        # get unspent outputs to account 0
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.account_index = 0
        output_query.is_spent = False
        outputs: list[MoneroOutputWallet] = OutputUtils.get_and_test_outputs(wallet, output_query, None)

        for output in outputs:
            assert output.account_index == 0
            assert output.is_spent is False

        # get spent outputs to account 1
        output_query = MoneroOutputQuery()
        output_query.account_index = 1
        output_query.is_spent = True
        outputs = OutputUtils.get_and_test_outputs(wallet, output_query, True)

        for output in outputs:
            assert output.account_index == 1
            assert output.is_spent is True

        # get random transactions
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_confirmed = True
        txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, tx_query, 3, 5)

        # get outputs with a tx hash
        tx_hashes: list[str] = []
        for tx in txs:
            assert tx.hash is not None
            tx_hashes.append(tx.hash)
            output_query = MoneroOutputQuery()
            output_query.set_tx_query(MoneroTxQuery(), True)
            assert output_query.tx_query is not None
            output_query.tx_query.hash = tx.hash
            outputs = OutputUtils.get_and_test_outputs(wallet, output_query, True)

            for output in outputs:
                assert output.tx is not None
                assert output.tx.hash is not None
                assert output.tx.hash in tx_hashes

        # get outputs with tx hashes
        tx_query = MoneroTxQuery()
        tx_query.hashes = tx_hashes
        output_query = MoneroOutputQuery()
        output_query.set_tx_query(tx_query, True)
        outputs = OutputUtils.get_and_test_outputs(wallet, output_query, True)

        for output in outputs:
            assert output.tx is not None
            assert output.tx.hash is not None
            assert output.tx.hash in tx_hashes

        # get confirmed outputs to specifi subaddress with pre-built query
        account_idx: int = 0
        subaddress_idx: int = 1
        output_query = MoneroOutputQuery()
        output_query.account_index = account_idx
        output_query.subaddress_index = subaddress_idx
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        output_query.set_tx_query(tx_query, True)
        output_query.min_amount = TxWalletUtils.MAX_FEE
        outputs = OutputUtils.get_and_test_outputs(wallet, output_query, True)

        for output in outputs:
            assert output.account_index == account_idx
            assert output.subaddress_index == subaddress_idx
            assert output.tx is not None
            assert output.tx.is_confirmed is True
            assert output.amount is not None
            assert output.amount >= TxWalletUtils.MAX_FEE

        # get output by key image
        output: MoneroOutputWallet = outputs[0]
        assert output.key_image is not None
        assert output.key_image.hex is not None
        output_query = MoneroOutputQuery()
        output_query.key_image = MoneroKeyImage()
        output_query.key_image.hex = output.key_image.hex
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 1
        output_result: MoneroOutputWallet = outputs[0]
        assert output_result.key_image is not None
        assert output.key_image.hex == output_result.key_image.hex

        # get outputs whose transaction is confirmed and has incoming and outgoing transfers
        output_query = MoneroOutputQuery()
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.is_incoming = True
        tx_query.is_outgoing = True
        tx_query.include_outputs = True
        output_query.set_tx_query(tx_query, True)
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) > 0

        for output in outputs:
            assert output.tx is not None
            assert isinstance(output.tx, MoneroTxWallet)
            assert output.tx.is_incoming is True
            assert output.tx.is_outgoing is True
            assert output.tx.is_confirmed is True
            outputs_wallet: list[MoneroOutputWallet] = output.tx.get_outputs_wallet()
            assert len(outputs_wallet) > 0
            assert output in outputs_wallet

    # Validates inputs when getting wallet outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled or LITE_MODE enabled")
    def test_validate_inputs_get_outputs(self, wallet: MoneroWallet) -> None:
        # test with invalid hash
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.set_tx_query(MoneroTxQuery(), True)
        assert output_query.tx_query is not None
        output_query.tx_query.hash = "invalid_id"

        outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
        assert len(outputs) == 0

        # test invalid hash in list
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.include_outputs = True
        random_txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, tx_query, 3, 5)

        for random_tx in random_txs:
            assert len(random_tx.outputs) > 0

        output_query = MoneroOutputQuery()
        output_query.set_tx_query(MoneroTxQuery(), False)
        assert output_query.tx_query is not None
        random_hash: str | None = random_txs[0].hash
        assert random_hash is not None and len(random_hash) > 0
        output_query.tx_query.hashes = [random_hash, "invalid_id"]

        outputs = wallet.get_outputs(output_query)
        assert len(outputs) > 0
        assert len(outputs) == len(random_txs[0].outputs)

        tx: MoneroTx = outputs[0].tx
        assert isinstance(tx, MoneroTxWallet)

        for output in outputs:
            assert output.tx == tx

    # Can export outputs in hex format
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_export_outputs(self, wallet: MoneroWallet) -> None:
        outputs_hex: str = wallet.export_outputs()
        logger.debug(f"Exported outputs hex: {outputs_hex}")
        # TODO: this will fail if wallet has no outputs; run these tests on new wallet
        assert outputs_hex is not None and len(outputs_hex) > 0

        # wallet exports outputs since last export by default
        outputs_hex = wallet.export_outputs()
        outputs_hex_all: str = wallet.export_outputs(True)
        assert len(outputs_hex_all) > len(outputs_hex)

    # Can import outputs in hex format
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled")
    def test_import_outputs(self, wallet: MoneroWallet) -> None:
        # export outputs hex
        outputs_hex: str = wallet.export_outputs()
        logger.debug(f"Exported outputs hex {outputs_hex}")
        # import outputs hex
        if len(outputs_hex) > 0:
            num_imported: int = wallet.import_outputs(outputs_hex)
            assert num_imported >= 0

    # Can freeze and thaw outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_freeze_outputs(self, wallet: MoneroWallet) -> None:
        # get an available output
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.is_spent = False
        output_query.is_frozen = False
        output_query.set_tx_query(MoneroTxQuery(), True)
        assert output_query.tx_query is not None
        output_query.tx_query.is_locked = False
        outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
        assert len(outputs) > 0
        for output in outputs:
            assert output.is_frozen is False

        output: MoneroOutputWallet = outputs[0]
        assert output.tx is not None
        assert isinstance(output.tx, MoneroTxWallet)
        assert output.tx.is_locked is False
        assert output.is_spent is False
        assert output.is_frozen is False
        assert output.key_image is not None
        assert output.key_image.hex is not None
        assert wallet.is_output_frozen(output.key_image.hex) is False

        # freeze output by key image
        output_query = MoneroOutputQuery()
        output_query.is_frozen = True
        num_frozen_before: int = len(wallet.get_outputs(output_query))
        wallet.freeze_output(output.key_image.hex)
        is_frozen: bool = wallet.is_output_frozen(output.key_image.hex)
        assert is_frozen

        # test querying
        frozen_outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
        num_frozen: int = len(frozen_outputs)
        assert num_frozen == num_frozen_before + 1
        output_query = MoneroOutputQuery()
        output_query.key_image = MoneroKeyImage()
        output_query.key_image.hex = output.key_image.hex
        output_query.is_frozen = True
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 1
        output_frozen: MoneroOutputWallet = outputs[0]
        assert output_frozen.is_frozen is True
        assert output_frozen.key_image is not None
        assert output.key_image.hex == output_frozen.key_image.hex

        # try to sweep frozen output
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.address = wallet.get_primary_address()
        tx_config.key_image = output.key_image.hex
        with pytest.raises(Exception) as exc_info:
            wallet.sweep_output(tx_config)
        assert str(exc_info.value) == "No outputs found"

        # try to freeze empty key image
        with pytest.raises(Exception) as exc_info:
            wallet.freeze_output("")
        assert str(exc_info.value) == "Must specify key image to freeze"

        # try to freeze bad key image
        with pytest.raises(Exception) as exc_info:
            wallet.freeze_output("123")
        assert str(exc_info.value) == "failed to parse key image"

        # thaw output by key image
        wallet.thaw_output(output.key_image.hex)
        is_frozen = wallet.is_output_frozen(output.key_image.hex)
        assert is_frozen is False

        # test querying
        output_query = MoneroOutputQuery()
        output_query.is_frozen = True
        assert num_frozen_before == len(wallet.get_outputs(output_query))

        output_query = MoneroOutputQuery()
        output_query.key_image = MoneroKeyImage()
        output_query.key_image.hex = output.key_image.hex
        output_query.is_frozen = True
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 0

        output_query.is_frozen = False
        outputs = wallet.get_outputs(output_query)
        assert len(outputs) == 1

        output_thawed: MoneroOutputWallet = outputs[0]
        assert output_thawed.is_frozen is False
        assert output_thawed.key_image is not None
        assert output_thawed.key_image.hex == output.key_image.hex

    # Provides key images of spent outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_input_key_images(self, wallet: MoneroWallet) -> None:
        # get subaddress to test input key images
        subaddress: Optional[MoneroSubaddress] = WalletTestUtils.select_subaddress_with_min_balance(wallet, TxWalletUtils.MAX_FEE)
        assert subaddress is not None, "No subaddress with outputs found for test input key images; fund wallet"
        assert subaddress.account_index is not None
        assert subaddress.index is not None
        account_index: int = subaddress.account_index
        subaddress_index: int = subaddress.index

        # test unrelayed single transaction
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = account_index
        tx_config.destinations.append(MoneroDestination(wallet.get_primary_address(), TxWalletUtils.MAX_FEE))
        spend_tx: MoneroTxWallet = wallet.create_tx(tx_config)
        TxWalletUtils.test_spend_tx(spend_tx)

        # test unrelayed split transactions
        txs: list[MoneroTxWallet] = wallet.create_txs(tx_config)
        for tx in txs:
            TxWalletUtils.test_spend_tx(tx)

        # test unrelayed sweep dust
        dust_key_images: list[str] = []
        txs = wallet.sweep_dust(False)
        for tx in txs:
            TxWalletUtils.test_spend_tx(tx)
            for tx_input in tx.inputs:
                assert tx_input.key_image is not None
                assert tx_input.key_image.hex is not None
                dust_key_images.append(tx_input.key_image.hex)

        # get available outputs above min amount
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.account_index = account_index
        output_query.subaddress_index = subaddress_index
        output_query.is_spent = False
        output_query.is_frozen = False
        output_query.min_amount = TxWalletUtils.MAX_FEE
        output_query.set_tx_query(MoneroTxQuery(), True)
        assert output_query.tx_query is not None
        output_query.tx_query.is_locked = False
        outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)

        assert len(outputs) > 0, "No outputs found"
        logger.debug(f"Found {len(outputs)} outputs")

        # filter dust outputs
        dust_outputs: list[MoneroOutputWallet] = []
        for output in outputs:
            assert output.key_image is not None
            assert output.key_image.hex is not None
            if output.key_image.hex in dust_key_images:
                dust_outputs.append(output)

        logger.debug(f"Found {len(dust_outputs)} dust outputs")

        # remove dust outputs from outputs
        outputs = list(filter(lambda output: output not in dust_outputs, outputs))

        assert len(outputs) > 0, "No available outputs found"
        logger.debug(f"Using {len(outputs)} available outputs")

        # test unrelayed sweep output
        tx_config = MoneroTxConfig()
        tx_config.address = wallet.get_primary_address()
        output_key_image: MoneroKeyImage | None = outputs[0].key_image
        assert output_key_image is not None
        tx_config.key_image = output_key_image.hex
        spend_tx = wallet.sweep_output(tx_config)
        TxWalletUtils.test_spend_tx(spend_tx)

        # test unrelayed sweep wallet ensuring all non-dust outputs are spent
        available_key_images: set[str] = set()
        for output in outputs:
            assert output.key_image is not None
            assert output.key_image.hex is not None
            available_key_images.add(output.key_image.hex)
        swept_key_images: set[str] = set()
        tx_config = MoneroTxConfig()
        tx_config.account_index = account_index
        tx_config.subaddress_indices.append(subaddress_index)
        tx_config.address = wallet.get_primary_address()
        txs = wallet.sweep_unlocked(tx_config)

        for tx in txs:
            TxWalletUtils.test_spend_tx(tx)
            for input_wallet in tx.inputs:
                assert input_wallet.key_image is not None
                assert input_wallet.key_image.hex is not None
                swept_key_images.add(input_wallet.key_image.hex)

        assert len(swept_key_images) > 0

        # max skipped output is less than max fee amount
        max_skipped_output: Optional[MoneroOutputWallet] = None
        for output in outputs:
            assert output.key_image is not None
            assert output.key_image.hex is not None
            assert output.amount is not None
            if output.key_image.hex not in swept_key_images:
                if max_skipped_output is None or max_skipped_output.amount < output.amount: # type: ignore
                    max_skipped_output = output

        if max_skipped_output is not None:
            assert max_skipped_output.amount is not None
            assert max_skipped_output.amount < TxWalletUtils.MAX_FEE

    # Can export signed key images
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_export_key_images(self, wallet: MoneroWallet) -> None:
        result: MoneroKeyImageExportResult = wallet.export_key_images(True)
        assert len(result.key_images) > 0, "No signed key images in wallet"

        for image in result.key_images:
            assert isinstance(image, MoneroKeyImage)
            assert image.hex is not None and len(image.hex) > 0
            assert image.signature is not None and len(image.signature) > 0

        # wallet exports key images since last export by default
        images: MoneroKeyImageExportResult = wallet.export_key_images()
        images_all: MoneroKeyImageExportResult = wallet.export_key_images(True)
        assert len(images_all.key_images) > len(images.key_images)

    # Can get new key images from the last import
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
        # get outputs hex
        outputs_hex: str = wallet.export_outputs()

        # import outputs hex
        if outputs_hex != "":
            num_imported: int = wallet.import_outputs(outputs_hex)
            assert num_imported >= 0

        # get and test new key images from last import
        export_result: MoneroKeyImageExportResult = wallet.get_new_key_images_from_last_import()
        if len(export_result.key_images) == 0:
            pytest.skip("wallet already knows every output's key image; run after tests that generate new ones")
        for image in export_result.key_images:
            assert image.hex is not None and len(image.hex) > 0
            assert image.signature is not None and len(image.signature) > 0

    # Can import key images
    # TODO monero-project: importing key images can cause erasure of incoming transfers per wallet2.cpp:11957
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        export_result: MoneroKeyImageExportResult = wallet.export_key_images()
        assert len(export_result.key_images) > 0, "Wallet does not have any key images run send tests"
        result: MoneroKeyImageImportResult = wallet.import_key_images(export_result.key_images)
        assert result.height is not None and result.height > 0

        # determine if non-zero spent and unspent amounts are expected
        query: MoneroTxQuery = MoneroTxQuery()
        query.is_outgoing = True
        query.is_confirmed = True
        txs: list[MoneroTxWallet] = wallet.get_txs(query)
        balance: int = wallet.get_balance()
        has_spent: bool = len(txs) > 0
        has_unspent: bool = balance > 0

        # test amounts
        GenUtils.test_unsigned_big_integer(result.spent_amount, has_spent)
        GenUtils.test_unsigned_big_integer(result.unspent_amount, has_unspent)


@pytest.mark.integration
class TestMoneroWalletFullOutputs(FullWalletSupport, BaseTestMoneroWalletOutputs):
    """Full wallet outputs integration tests."""

    @pytest.mark.skip(reason="TODO disabled because importing key images deletes corresponding incoming transfers: #5812")
    @override
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_import_key_images(wallet)


@pytest.mark.integration
class TestMoneroWalletRpcOutputs(RpcWalletSupport, BaseTestMoneroWalletOutputs):
    """Rpc wallet outputs integration tests."""

    @pytest.mark.skip(reason="TODO https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_import_key_images(wallet)


@pytest.mark.unit
class TestMoneroWalletKeysOutputs(KeysWalletSupport, BaseTestMoneroWalletOutputs):
    """Keys-only wallet outputs unit tests."""

    @pytest.mark.not_supported
    @override
    def test_get_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_get_outputs(wallet)

    @pytest.mark.not_supported
    @override
    def test_validate_inputs_get_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_validate_inputs_get_outputs(wallet)

    @pytest.mark.not_supported
    @override
    def test_export_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_export_key_images(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
        return super().test_get_new_key_images_from_last_import(wallet)

    @pytest.mark.not_supported
    @override
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_import_key_images(wallet)

    @pytest.mark.not_supported
    @override
    def test_export_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_export_outputs(wallet)

    @pytest.mark.not_supported
    @override
    def test_import_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_import_outputs(wallet)

    @pytest.mark.not_supported
    @override
    def test_freeze_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_freeze_outputs(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_outputs_with_query(self, wallet: MoneroWallet) -> None:
        return super().test_get_outputs_with_query(wallet)

    @override
    def test_input_key_images(self, wallet: MoneroWallet) -> None:
        # a keys-only wallet cannot enumerate accounts/subaddresses, which this test needs
        with pytest.raises(RuntimeError, match=r"get_accounts\(\) not supported"):
            super().test_input_key_images(wallet)
