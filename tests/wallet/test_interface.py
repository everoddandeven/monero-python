import pytest
import logging

from typing_extensions import override

from monero import MoneroWallet, MoneroTxWallet, MoneroMessageSignatureResult

from utils import WalletUtils, BaseTestClass, WalletCall, WALLET_CALLS

logger: logging.Logger = logging.getLogger("TestMoneroWalletInterface")


# Test binding calls to MoneroWallet interface
@pytest.mark.unit
class TestMoneroWalletInterface(BaseTestClass):
    """Wallet interface binding calls unit tests."""

    @pytest.fixture(scope="class")
    @classmethod
    def wallet(cls) -> MoneroWallet:
        """Test wallet instance."""
        return MoneroWallet()

    #region Tests

    # Test default language static property
    def test_default_language(self) -> None:
        assert MoneroWallet.DEFAULT_LANGUAGE is not None, "MoneroWallet.DEFAULT_LANGUAGE is None"
        assert MoneroWallet.DEFAULT_LANGUAGE == "English", f'Expected "English", got {MoneroWallet.DEFAULT_LANGUAGE}'

    # Can call every method of the interface: the ones that MoneroWallet does not implement itself are not supported
    @pytest.mark.not_supported
    @pytest.mark.parametrize("call", [call for call in WALLET_CALLS if not call.in_base], ids=str)
    def test_call(self, wallet: MoneroWallet, call: WalletCall) -> None:
        call(wallet)

    def test_relay_txs_none_tx_raises(self, wallet: MoneroWallet) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            wallet.relay_txs([None]) # type: ignore
        assert str(exc_info.value) == "Tx metadata is not initialized"

    def test_relay_txs_uninitialized_metadata_raises(self, wallet: MoneroWallet) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        with pytest.raises(RuntimeError) as exc_info:
            wallet.relay_txs([tx])
        assert str(exc_info.value) == "Tx metadata is not initialized"

    def test_relay_txs_empty_metadata_raises(self, wallet: MoneroWallet) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.metadata = ""
        with pytest.raises(RuntimeError) as exc_info:
            wallet.relay_txs([tx])
        assert str(exc_info.value) == "Tx metadata is not initialized"

    def test_verify_message(self, wallet: MoneroWallet) -> None:
        result: MoneroMessageSignatureResult = wallet.verify_message("", "", "")
        WalletUtils.test_message_signature_result(result, False)

    # A python override of import_multisig_hex gets the refresh flag of the caller
    def test_import_multisig_hex_forwards_refresh_after_import(self) -> None:
        forwarded: list[bool] = []

        class MultisigWallet(MoneroWallet):
            @override
            def import_multisig_hex(self, multisig_hexes: list[str], refresh_after_import: bool = True) -> int:
                forwarded.append(refresh_after_import)
                return 42

        wallet: MoneroWallet = MultisigWallet()

        # the binding dispatches to the override through the trampoline
        assert MoneroWallet.import_multisig_hex(wallet, ["ab"], False) == 42
        assert MoneroWallet.import_multisig_hex(wallet, ["cd"], True) == 42
        assert MoneroWallet.import_multisig_hex(wallet, ["ef"]) == 42
        assert MoneroWallet.import_multisig_hex(wallet, multisig_hexes=["gh"], refresh_after_import=False) == 42
        assert forwarded == [False, True, True, False]

    #endregion
