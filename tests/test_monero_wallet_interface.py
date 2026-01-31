import pytest
import logging

from monero import (
    MoneroWallet, MoneroConnectionManager, MoneroRpcConnection,
    MoneroWalletListener, MoneroTransferQuery, MoneroOutputQuery,
    MoneroTxConfig, MoneroTxSet, MoneroMessageSignatureType,
    MoneroTxWallet
)

logger: logging.Logger = logging.getLogger("TestMoneroWalletInterface")


# Test calls to MoneroWallet interface
@pytest.mark.unit
class TestMoneroWalletInterface:
    """Wallet interface bindings unit tests"""

    @pytest.fixture(scope="class")
    def wallet(self) -> MoneroWallet:
        """Test wallet instance"""
        return MoneroWallet()

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    #region Tests

    # Test default language static property
    def test_default_language(self) -> None:
        assert MoneroWallet.DEFAULT_LANGUAGE is not None, "MoneroWallet.DEFAULT_LANGUAGE is None"
        assert MoneroWallet.DEFAULT_LANGUAGE == "English", f'Expected "English", got {MoneroWallet.DEFAULT_LANGUAGE}'

    @pytest.mark.not_supported
    def test_is_view_only(self, wallet: MoneroWallet) -> None:
        wallet.is_view_only()

    @pytest.mark.not_supported
    def test_get_version(self, wallet: MoneroWallet) -> None:
        wallet.get_version()

    @pytest.mark.not_supported
    def test_get_path(self, wallet: MoneroWallet) -> None:
        wallet.get_path()

    @pytest.mark.not_supported
    def test_get_network_type(self, wallet: MoneroWallet) -> None:
        wallet.get_network_type()

    # TODO move definitions to monero-cpp
    #@pytest.mark.not_supported
    def test_set_connection_manager(self, wallet: MoneroWallet) -> None:
        wallet.set_connection_manager(MoneroConnectionManager())

    @pytest.mark.skip(reason="TODO segmentation fault")
    def test_get_connection_manager(self, wallet: MoneroWallet) -> None:
        wallet.get_connection_manager()

    @pytest.mark.not_supported
    def test_set_daemon_connection_1(self, wallet: MoneroWallet) -> None:
        wallet.set_daemon_connection('')

    @pytest.mark.not_supported
    def test_set_daemon_connection_2(self, wallet: MoneroWallet) -> None:
        wallet.set_daemon_connection(MoneroRpcConnection())

    @pytest.mark.not_supported
    def test_get_daemon_connection(self, wallet: MoneroWallet) -> None:
        wallet.get_daemon_connection()

    @pytest.mark.not_supported
    def test_is_connected_to_daemon(self, wallet: MoneroWallet) -> None:
        wallet.is_connected_to_daemon()

    @pytest.mark.not_supported
    def test_is_daemon_trusted(self, wallet: MoneroWallet) -> None:
        wallet.is_daemon_trusted()

    @pytest.mark.not_supported
    def test_get_seed(self, wallet: MoneroWallet) -> None:
        wallet.get_seed()

    @pytest.mark.not_supported
    def test_get_seed_language(self, wallet: MoneroWallet) -> None:
        wallet.get_seed_language()

    @pytest.mark.not_supported
    def test_get_public_view_key(self, wallet: MoneroWallet) -> None:
        wallet.get_public_view_key()

    @pytest.mark.not_supported
    def test_get_private_view_key(self, wallet: MoneroWallet) -> None:
        wallet.get_private_view_key()

    @pytest.mark.not_supported
    def test_get_public_spend_key(self, wallet: MoneroWallet) -> None:
        wallet.get_public_spend_key()

    @pytest.mark.not_supported
    def test_get_private_spend_key(self, wallet: MoneroWallet) -> None:
        wallet.get_private_spend_key()

    @pytest.mark.not_supported
    def test_primary_address(self, wallet: MoneroWallet) -> None:
        wallet.get_primary_address()

    @pytest.mark.not_supported
    def test_get_address(self, wallet: MoneroWallet) -> None:
        wallet.get_address(0, 0)

    @pytest.mark.not_supported
    def test_get_address_index(self, wallet: MoneroWallet) -> None:
        wallet.get_address_index("")

    @pytest.mark.not_supported
    def test_get_integrated_address(self, wallet: MoneroWallet) -> None:
        wallet.get_integrated_address()

    @pytest.mark.not_supported
    def test_decode_integrated_address(self, wallet: MoneroWallet) -> None:
        wallet.decode_integrated_address("")

    @pytest.mark.not_supported
    def test_is_synced(self, wallet: MoneroWallet) -> None:
        wallet.is_synced()

    @pytest.mark.not_supported
    def test_get_height(self, wallet: MoneroWallet) -> None:
        wallet.get_height()

    @pytest.mark.not_supported
    def test_get_restore_height(self, wallet: MoneroWallet) -> None:
        wallet.get_restore_height()

    @pytest.mark.not_supported
    def test_set_restore_height(self, wallet: MoneroWallet) -> None:
        wallet.set_restore_height(0)

    @pytest.mark.not_supported
    def test_get_daemon_height(self, wallet: MoneroWallet) -> None:
        wallet.get_daemon_height()

    @pytest.mark.not_supported
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        wallet.get_daemon_max_peer_height()

    @pytest.mark.not_supported
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        wallet.get_height_by_date(0, 0, 0)

    @pytest.mark.not_supported
    def test_add_listener(self, wallet: MoneroWallet) -> None:
        wallet.add_listener(MoneroWalletListener())

    @pytest.mark.not_supported
    def test_remove_listener(self, wallet: MoneroWallet) -> None:
        wallet.remove_listener(MoneroWalletListener())

    @pytest.mark.not_supported
    def test_get_listeners(self, wallet: MoneroWallet) -> None:
        wallet.get_listeners()

    @pytest.mark.not_supported
    def test_sync(self, wallet: MoneroWallet) -> None:
        wallet.sync()

    @pytest.mark.not_supported
    def test_sync_with_listener(self, wallet: MoneroWallet) -> None:
        wallet.sync(MoneroWalletListener())

    @pytest.mark.not_supported
    def test_sync_with_start_height(self, wallet: MoneroWallet) -> None:
        wallet.sync(0)

    @pytest.mark.not_supported
    def test_sync_with_listener_and_start_height(self, wallet: MoneroWallet) -> None:
        wallet.sync(0, MoneroWalletListener())

    @pytest.mark.not_supported
    def test_start_syncing(self, wallet: MoneroWallet) -> None:
        wallet.start_syncing()

    @pytest.mark.not_supported
    def test_stop_syncing(self, wallet: MoneroWallet) -> None:
        wallet.stop_syncing()

    @pytest.mark.not_supported
    def test_scan_txs(self, wallet: MoneroWallet) -> None:
        wallet.scan_txs(["", "", ""])

    @pytest.mark.not_supported
    def test_rescan_spent(self, wallet: MoneroWallet) -> None:
        wallet.rescan_spent()

    @pytest.mark.not_supported
    def test_rescan_blockchain(self, wallet: MoneroWallet) -> None:
        wallet.rescan_blockchain()

    @pytest.mark.not_supported
    def test_get_balance(self, wallet: MoneroWallet) -> None:
        wallet.get_balance()

    @pytest.mark.not_supported
    def test_get_account_balance(self, wallet: MoneroWallet) -> None:
        wallet.get_balance(0)

    @pytest.mark.not_supported
    def test_get_subaddress_balance(self, wallet: MoneroWallet) -> None:
        wallet.get_balance(0, 0)

    @pytest.mark.not_supported
    def test_get_unlocked_balance(self, wallet: MoneroWallet) -> None:
        wallet.get_unlocked_balance()

    @pytest.mark.not_supported
    def test_get_account_unlocked_balance(self, wallet: MoneroWallet) -> None:
        wallet.get_unlocked_balance(0)

    @pytest.mark.not_supported
    def test_get_subaddress_unlocked_balance(self, wallet: MoneroWallet) -> None:
        wallet.get_unlocked_balance(0, 0)

    @pytest.mark.not_supported
    def test_get_accounts(self, wallet: MoneroWallet) -> None:
        wallet.get_accounts()

    @pytest.mark.not_supported
    def test_get_accounts_with_tag(self, wallet: MoneroWallet) -> None:
        wallet.get_accounts("")

    @pytest.mark.not_supported
    def test_get_accounts_with_subaddresses(self, wallet: MoneroWallet) -> None:
        wallet.get_accounts(True)

    @pytest.mark.not_supported
    def test_get_accounts_with_subaddresses_and_tag(self, wallet: MoneroWallet) -> None:
        wallet.get_accounts(True, "")

    @pytest.mark.not_supported
    def test_get_account(self, wallet: MoneroWallet) -> None:
        wallet.get_account(0)

    @pytest.mark.not_supported
    def test_get_account_with_subaddresses(self, wallet: MoneroWallet) -> None:
        wallet.get_account(0, True)

    @pytest.mark.not_supported
    def test_create_account(self, wallet: MoneroWallet) -> None:
        wallet.create_account()

    @pytest.mark.not_supported
    def test_get_subaddress(self, wallet: MoneroWallet) -> None:
        wallet.get_subaddress(0, 0)

    @pytest.mark.not_supported
    def test_get_account_subaddresses(self, wallet: MoneroWallet) -> None:
        wallet.get_subaddresses(0)

    @pytest.mark.not_supported
    def test_create_account_subaddress(self, wallet: MoneroWallet) -> None:
        wallet.create_subaddress(0, "")

    @pytest.mark.not_supported
    def test_set_subaddress_label(self, wallet: MoneroWallet) -> None:
        wallet.set_subaddress_label(1, 1, "")

    @pytest.mark.not_supported
    def test_get_txs(self, wallet: MoneroWallet) -> None:
        wallet.get_txs()

    @pytest.mark.not_supported
    def test_get_transfers(self, wallet: MoneroWallet) -> None:
        wallet.get_transfers(MoneroTransferQuery())

    @pytest.mark.not_supported
    def test_get_outputs(self, wallet: MoneroWallet) -> None:
        wallet.get_outputs(MoneroOutputQuery())

    @pytest.mark.not_supported
    def test_export_outputs(self, wallet: MoneroWallet) -> None:
        wallet.export_outputs(True)

    @pytest.mark.not_supported
    def test_import_outputs(self, wallet: MoneroWallet) -> None:
        wallet.import_outputs("")

    @pytest.mark.not_supported
    def test_export_key_images(self, wallet: MoneroWallet) -> None:
        wallet.export_key_images(True)

    @pytest.mark.not_supported
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        wallet.import_key_images([])

    #@pytest.mark.not_supported
    @pytest.mark.skip(reason="TODO segmentation fault")
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
        wallet.get_new_key_images_from_last_import()

    @pytest.mark.not_supported
    def test_freeze_output(self, wallet: MoneroWallet) -> None:
        wallet.freeze_output("")

    @pytest.mark.not_supported
    def test_thaw_output(self, wallet: MoneroWallet) -> None:
        wallet.thaw_output("")

    @pytest.mark.not_supported
    def test_is_output_frozen(self, wallet: MoneroWallet) -> None:
        wallet.is_output_frozen("")

    @pytest.mark.not_supported
    def test_get_default_fee_priority(self, wallet: MoneroWallet) -> None:
        wallet.get_default_fee_priority()

    @pytest.mark.not_supported
    def test_create_tx(self, wallet: MoneroWallet) -> None:
        wallet.create_tx(MoneroTxConfig())

    @pytest.mark.not_supported
    def test_create_txs(self, wallet: MoneroWallet) -> None:
        wallet.create_txs(MoneroTxConfig())

    @pytest.mark.not_supported
    def test_sweep_unlocked(self, wallet: MoneroWallet) -> None:
        wallet.sweep_unlocked(MoneroTxConfig())

    @pytest.mark.not_supported
    def test_sweep_output(self, wallet: MoneroWallet) -> None:
        wallet.sweep_output(MoneroTxConfig())

    @pytest.mark.not_supported
    def test_sweep_dust(self, wallet: MoneroWallet) -> None:
        wallet.sweep_dust(True)

    @pytest.mark.not_supported
    def test_relay_tx_metadata(self, wallet: MoneroWallet) -> None:
        wallet.relay_tx("")

    #@pytest.mark.not_supported
    @pytest.mark.skip(reason="TODO aborted: insert check for tx.metadata != boost::none")
    def test_relay_tx(self, wallet: MoneroWallet) -> None:
        wallet.relay_tx(MoneroTxWallet())

    @pytest.mark.not_supported
    def test_relay_txs(self, wallet: MoneroWallet) -> None:
        wallet.relay_txs([])

    @pytest.mark.not_supported
    def test_describe_tx_set(self, wallet: MoneroWallet) -> None:
        wallet.describe_tx_set(MoneroTxSet())

    @pytest.mark.not_supported
    def test_sign_txs(self, wallet: MoneroWallet) -> None:
        wallet.sign_txs("")

    @pytest.mark.not_supported
    def test_submit_txs(self, wallet: MoneroWallet) -> None:
        wallet.submit_txs("")

    @pytest.mark.not_supported
    def test_get_tx_key(self, wallet: MoneroWallet) -> None:
        wallet.get_tx_key("")

    @pytest.mark.not_supported
    def test_check_tx_key(self, wallet: MoneroWallet) -> None:
        wallet.check_tx_key("", "", "")

    @pytest.mark.not_supported
    def test_get_tx_proof(self, wallet: MoneroWallet) -> None:
        wallet.get_tx_proof("", "", "")

    @pytest.mark.not_supported
    def test_check_tx_proof(self, wallet: MoneroWallet) -> None:
        wallet.check_tx_proof("", "", "", "")

    @pytest.mark.not_supported
    def test_get_spend_proof(self, wallet: MoneroWallet) -> None:
        wallet.get_spend_proof("", "")

    @pytest.mark.not_supported
    def test_check_spend_proof(self, wallet: MoneroWallet) -> None:
        wallet.check_spend_proof("", "", "")

    @pytest.mark.not_supported
    def test_get_reserve_proof_wallet(self, wallet: MoneroWallet) -> None:
        wallet.get_reserve_proof_wallet("")

    @pytest.mark.not_supported
    def test_get_reserve_proof_account(self, wallet: MoneroWallet) -> None:
        wallet.get_reserve_proof_account(0, 0, "")

    @pytest.mark.not_supported
    def test_check_reserve_proof(self, wallet: MoneroWallet) -> None:
        wallet.check_reserve_proof("", "", "")

    @pytest.mark.not_supported
    def test_get_tx_note(self, wallet: MoneroWallet) -> None:
        wallet.get_tx_note("")

    @pytest.mark.not_supported
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        wallet.set_tx_note("", "")

    @pytest.mark.not_supported
    def test_set_tx_notes(self, wallet: MoneroWallet) -> None:
        wallet.set_tx_notes([], [])

    @pytest.mark.not_supported
    def test_get_address_book_entries(self, wallet: MoneroWallet) -> None:
        wallet.get_address_book_entries([])

    @pytest.mark.not_supported
    def test_add_address_book_entry(self, wallet: MoneroWallet) -> None:
        wallet.add_address_book_entry("", "")

    @pytest.mark.not_supported
    def test_edit_address_book_entry(self, wallet: MoneroWallet) -> None:
        wallet.edit_address_book_entry(1, False, "", True, "")

    @pytest.mark.not_supported
    def test_delete_address_book_entry(self, wallet: MoneroWallet) -> None:
        wallet.delete_address_book_entry(0)

    #@pytest.mark.not_supported
    @pytest.mark.skip(reason="TODO segmentation fault")
    def test_tag_accounts(self, wallet: MoneroWallet) -> None:
        wallet.tag_accounts("", [])

    #@pytest.mark.not_supported
    @pytest.mark.skip(reason="TODO segmentation fault")
    def test_untag_accounts(self, wallet: MoneroWallet) -> None:
        wallet.untag_accounts([])

    #@pytest.mark.not_supported
    @pytest.mark.skip(reason="TODO segmentation fault")
    def test_get_account_tags(self, wallet: MoneroWallet) -> None:
        wallet.get_account_tags()

    # TODO move definitions to monero-cpp
    #@pytest.mark.not_supported
    def test_set_account_tag_label(self, wallet: MoneroWallet) -> None:
        wallet.set_account_tag_label("", "")

    # TODO move definitions to monero-cpp
    #@pytest.mark.not_supported
    def test_set_account_label(self, wallet: MoneroWallet) -> None:
        wallet.set_account_label(0, "")

    @pytest.mark.not_supported
    def test_get_attribute(self, wallet: MoneroWallet) -> None:
        wallet.get_attribute("")

    @pytest.mark.not_supported
    def test_set_attribute(self, wallet: MoneroWallet) -> None:
        wallet.set_attribute("", "")

    @pytest.mark.not_supported
    def test_is_multisig_import_needed(self, wallet: MoneroWallet) -> None:
        wallet.is_multisig_import_needed()

    @pytest.mark.not_supported
    def test_is_multisig(self, wallet: MoneroWallet) -> None:
        wallet.is_multisig()

    @pytest.mark.not_supported
    def test_get_multisig_info(self, wallet: MoneroWallet) -> None:
        wallet.get_multisig_info()

    @pytest.mark.not_supported
    def test_prepare_multisig(self, wallet: MoneroWallet) -> None:
        wallet.prepare_multisig()

    @pytest.mark.not_supported
    def test_make_multisig(self, wallet: MoneroWallet) -> None:
        wallet.make_multisig([], 0, "")

    @pytest.mark.not_supported
    def test_exchange_multisig_keys(self, wallet: MoneroWallet) -> None:
        wallet.exchange_multisig_keys([], "")

    @pytest.mark.not_supported
    def test_export_multisig_hex(self, wallet: MoneroWallet) -> None:
        wallet.export_multisig_hex()

    @pytest.mark.not_supported
    def test_import_multisig_hex(self, wallet: MoneroWallet) -> None:
        wallet.import_multisig_hex([])

    @pytest.mark.not_supported
    def test_sign_multisig_tx_hex(self, wallet: MoneroWallet) -> None:
        wallet.sign_multisig_tx_hex("")

    @pytest.mark.not_supported
    def test_submit_multisig_tx_hex(self, wallet: MoneroWallet) -> None:
        wallet.submit_multisig_tx_hex("")

    @pytest.mark.not_supported
    def test_sign_message(self, wallet: MoneroWallet) -> None:
        wallet.sign_message("", MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY)

    @pytest.mark.not_supported
    def test_verify_message(self, wallet: MoneroWallet) -> None:
        wallet.verify_message("", "", "")

    @pytest.mark.not_supported
    def test_get_payment_uri(self, wallet: MoneroWallet) -> None:
        wallet.get_payment_uri(MoneroTxConfig())

    @pytest.mark.not_supported
    def test_parse_payment_uri(self, wallet: MoneroWallet) -> None:
        wallet.parse_payment_uri("")

    @pytest.mark.not_supported
    def test_start_mining(self, wallet: MoneroWallet) -> None:
        wallet.start_mining()

    @pytest.mark.not_supported
    def test_stop_mining(self, wallet: MoneroWallet) -> None:
        wallet.stop_mining()

    @pytest.mark.not_supported
    def test_wait_for_next_block(self, wallet: MoneroWallet) -> None:
        wallet.wait_for_next_block()

    @pytest.mark.not_supported
    def test_change_password(self, wallet: MoneroWallet) -> None:
        wallet.change_password("", "")

    @pytest.mark.not_supported
    def test_move_to(self, wallet: MoneroWallet) -> None:
        wallet.move_to("", "")

    @pytest.mark.not_supported
    def test_save(self, wallet: MoneroWallet) -> None:
        wallet.save()

    @pytest.mark.not_supported
    def test_close(self, wallet: MoneroWallet) -> None:
        wallet.close()

    #endregion
