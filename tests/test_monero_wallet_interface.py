import pytest
import logging

from typing import Optional
from monero import (
    MoneroWallet, MoneroConnectionManager, MoneroRpcConnection,
    MoneroWalletListener, MoneroTransferQuery, MoneroOutputQuery,
    MoneroTxConfig, MoneroTxSet, MoneroMessageSignatureType
)
from utils import AssertUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletInterface")


# Test calls to MoneroWallet interface
class TestMoneroWalletInterface:

    _wallet: Optional[MoneroWallet] = None

    def _get_wallet(self) -> MoneroWallet:
        if self._wallet is None:
            self._wallet = MoneroWallet()

        return self._wallet

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    #region Tests

    # Test static default language
    def test_defaults(self) -> None:
        assert MoneroWallet.DEFAULT_LANGUAGE is not None, "MoneroWallet.DEFAULT_LANGUAGE is None"
        assert MoneroWallet.DEFAULT_LANGUAGE == "English", f'Expected "English", got {MoneroWallet.DEFAULT_LANGUAGE}'

    # Test wallet general info
    def test_info(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.is_view_only()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_version()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_path()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_network_type()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet connection
    def test_connection(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.set_connection_manager(MoneroConnectionManager())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

# TODO segmentation fault
#        try:
#            wallet.get_connection_manager()
#        except Exception as e:
#            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_daemon_connection('')
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_daemon_connection(MoneroRpcConnection())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_daemon_connection()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.is_connected_to_daemon()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.is_daemon_trusted()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test get wallet keys
    def test_keys(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_seed()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_seed_language()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_public_view_key()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_private_view_key()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_public_spend_key()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_private_spend_key()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet addresses
    def test_addresses(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_primary_address()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_address(0, 0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_address_index("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_integrated_address()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.decode_integrated_address("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test get wallet sync info
    def test_sync_utils(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.is_synced()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_height()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_restore_height()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_restore_height(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_daemon_height()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_daemon_max_peer_height()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_height_by_date(0, 0, 0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.add_listener(MoneroWalletListener())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.remove_listener(MoneroWalletListener())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_listeners()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sync()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sync(MoneroWalletListener())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sync(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sync(0, MoneroWalletListener())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.start_syncing()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.stop_syncing()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.scan_txs(["", "", ""])
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.rescan_spent()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.rescan_blockchain()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet balance
    def test_get_balances(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_balance()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_balance(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_balance(0, 0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_unlocked_balance()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_unlocked_balance(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_unlocked_balance(0, 0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test get wallet accounts
    def test_get_accounts(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_accounts()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_accounts("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_accounts(True)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_accounts(True, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_account(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_account(0, True)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.create_account()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test get wallet subaddresses
    def test_get_subaddresses(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_subaddress(0, 0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_subaddresses(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.create_subaddress(0, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_subaddress_label(1, 1, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test txs wallet data
    def test_txs_data(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_txs()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_transfers(MoneroTransferQuery())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_outputs(MoneroOutputQuery())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.export_outputs(True)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.import_outputs("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.export_key_images(True)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.import_key_images([])
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        # TODO segmentation fault
#        try:
#            wallet.get_new_key_images_from_last_import()
#        except Exception as e:
#            AssertUtils.assert_not_supported(e)

        try:
            wallet.freeze_output("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.thaw_output("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.is_output_frozen("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_default_fee_priority()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet tx creation
    def test_txs_creation(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.create_tx(MoneroTxConfig())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.create_txs(MoneroTxConfig())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sweep_unlocked(MoneroTxConfig())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sweep_output(MoneroTxConfig())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sweep_dust(True)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.relay_tx("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

# TODO aborted
#        try:
#            wallet.relay_tx(MoneroTxWallet())
#        except Exception as e:
#            AssertUtils.assert_not_supported(e)

        try:
            wallet.relay_txs([])
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.describe_tx_set(MoneroTxSet())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sign_txs("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.submit_txs("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_tx_key("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.check_tx_key("", "", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet proofs
    def test_proofs(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_tx_proof("", "", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.check_tx_proof("", "", "", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_spend_proof("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.check_spend_proof("", "", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_reserve_proof_wallet("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_reserve_proof_account(0, 0, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.check_reserve_proof("", "", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet notes
    def test_notes(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.get_tx_note("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_tx_note("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_tx_notes([], [])
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_address_book_entries([])
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.add_address_book_entry("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.edit_address_book_entry(1, False, "", True, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.delete_address_book_entry(0)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

# TODO segmentation fault
#        try:
#            wallet.tag_accounts("", [])
#        except Exception as e:
#            AssertUtils.assert_not_supported(e)

#        try:
#            wallet.untag_accounts([])
#        except Exception as e:
#            AssertUtils.assert_not_supported(e)

#        try:
#            wallet.get_account_tags()
#        except Exception as e:
#            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_account_tag_label("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_account_label(0, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_attribute("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.set_attribute("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet multisig info
    def test_multisig(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.is_multisig_import_needed()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.is_multisig()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_multisig_info()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.prepare_multisig()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.make_multisig([], 0, "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.exchange_multisig_keys([], "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.export_multisig_hex()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.import_multisig_hex([])
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.sign_multisig_tx_hex("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.submit_multisig_tx_hex("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    # Test wallet utils
    def test_utils(self) -> None:
        wallet = self._get_wallet()

        try:
            wallet.sign_message("", MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY)
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.verify_message("", "", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.get_payment_uri(MoneroTxConfig())
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.parse_payment_uri("")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.start_mining()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.stop_mining()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.wait_for_next_block()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.change_password("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.move_to("", "")
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.save()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

        try:
            wallet.close()
        except Exception as e:
            AssertUtils.assert_not_supported(e)

    #endregion
