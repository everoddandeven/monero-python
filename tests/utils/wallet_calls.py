from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from typing_extensions import override

from monero import (
    MoneroWallet, MoneroRpcConnection, MoneroWalletListener, MoneroTransferQuery, MoneroOutputQuery, MoneroTxQuery,
    MoneroTxConfig, MoneroTxSet, MoneroTxWallet, MoneroMessageSignatureType
)

from .string_utils import StringUtils

# what the error of a method that a wallet does not implement says
NOT_SUPPORTED_HINTS: tuple[str, ...] = ("not supported", "does not support", "doesn't support")


@dataclass(frozen=True)
class WalletCall:
    """A call of a method of the MoneroWallet interface, with arguments of the right types and no meaning: what it returns or raises
    says whether the wallet implements the method, not whether the method works."""

    method: str
    """The method of MoneroWallet that it calls."""
    args: str
    """The parameters of the overload that it calls, as the stubs name them."""
    call: Callable[[MoneroWallet], object]
    """Calls the method on a wallet."""
    in_base: bool = False
    """MoneroWallet implements it on top of its other methods, so it does not raise "not supported" there."""
    waits: bool = False
    """A wallet that implements it waits on the network, so it can only be made on the wallets that do not."""

    def __call__(self, wallet: MoneroWallet) -> object:
        return self.call(wallet)

    def is_implemented_by(self, wallet: MoneroWallet) -> bool:
        """Whether the wallet implements the method: the call returns, or raises an error that is not a "not supported" one."""
        try:
            self.call(wallet)
        except Exception as error:
            return not any(hint in str(error).lower() for hint in NOT_SUPPORTED_HINTS)
        return True

    @override
    def __str__(self) -> str:
        return f"{self.method}({self.args})"


def _tx_with_metadata() -> MoneroTxWallet:
    tx: MoneroTxWallet = MoneroTxWallet()
    tx.metadata = StringUtils.get_random_string()
    return tx


# A call of every overload of every method of MoneroWallet, in the order of the sections of the docs. tests/wallet/test_interface.py makes
# them on MoneroWallet, which implements almost none, and tests/wallet/test_support.py on each wallet, to check the support matrix of the
# docs. close() is last: the calls after it would be on a closed wallet.
WALLET_CALLS: list[WalletCall] = [
    # wallet
    WalletCall("get_version", "", lambda w: w.get_version()),
    WalletCall("get_path", "", lambda w: w.get_path()),
    WalletCall("get_network_type", "", lambda w: w.get_network_type()),
    WalletCall("is_view_only", "", lambda w: w.is_view_only()),
    WalletCall("get_attribute", "key", lambda w: w.get_attribute("")),
    WalletCall("set_attribute", "key,val", lambda w: w.set_attribute("", "")),
    WalletCall("change_password", "old_password,new_password", lambda w: w.change_password("", "")),
    WalletCall("move_to", "path,password", lambda w: w.move_to("", "")),
    WalletCall("save", "", lambda w: w.save()),

    # keys and addresses
    WalletCall("get_seed", "", lambda w: w.get_seed()),
    WalletCall("get_seed_language", "", lambda w: w.get_seed_language()),
    WalletCall("get_public_view_key", "", lambda w: w.get_public_view_key()),
    WalletCall("get_private_view_key", "", lambda w: w.get_private_view_key()),
    WalletCall("get_public_spend_key", "", lambda w: w.get_public_spend_key()),
    WalletCall("get_private_spend_key", "", lambda w: w.get_private_spend_key()),
    WalletCall("get_primary_address", "", lambda w: w.get_primary_address()),
    WalletCall("get_address", "account_idx,subaddress_idx", lambda w: w.get_address(0, 0)),
    WalletCall("get_address_index", "address", lambda w: w.get_address_index("")),
    WalletCall("get_integrated_address", "standard_address,payment_id", lambda w: w.get_integrated_address()),
    WalletCall("decode_integrated_address", "integrated_address", lambda w: w.decode_integrated_address("")),

    # daemon connection
    WalletCall("set_daemon_connection", "uri", lambda w: w.set_daemon_connection("")),
    WalletCall("set_daemon_connection", "connection", lambda w: w.set_daemon_connection(MoneroRpcConnection())),
    WalletCall("get_daemon_connection", "", lambda w: w.get_daemon_connection()),
    WalletCall("is_connected_to_daemon", "", lambda w: w.is_connected_to_daemon()),
    WalletCall("is_daemon_synced", "", lambda w: w.is_daemon_synced()),
    WalletCall("is_daemon_trusted", "", lambda w: w.is_daemon_trusted()),
    WalletCall("get_daemon_height", "", lambda w: w.get_daemon_height()),
    WalletCall("get_daemon_max_peer_height", "", lambda w: w.get_daemon_max_peer_height()),
    WalletCall("get_height_by_date", "year,month,day", lambda w: w.get_height_by_date(0, 0, 0)),
    WalletCall("wait_for_next_block", "", lambda w: w.wait_for_next_block(), waits=True),

    # sync
    WalletCall("is_synced", "", lambda w: w.is_synced()),
    WalletCall("get_height", "", lambda w: w.get_height()),
    WalletCall("get_restore_height", "", lambda w: w.get_restore_height()),
    WalletCall("set_restore_height", "restore_height", lambda w: w.set_restore_height(0)),
    WalletCall("sync", "", lambda w: w.sync()),
    WalletCall("sync", "listener", lambda w: w.sync(MoneroWalletListener())),
    WalletCall("sync", "start_height", lambda w: w.sync(0)),
    WalletCall("sync", "start_height,listener", lambda w: w.sync(0, MoneroWalletListener())),
    WalletCall("start_syncing", "sync_period_in_ms", lambda w: w.start_syncing()),
    WalletCall("stop_syncing", "", lambda w: w.stop_syncing()),
    WalletCall("scan_txs", "tx_hashes", lambda w: w.scan_txs(["", "", ""])),
    WalletCall("rescan_spent", "", lambda w: w.rescan_spent()),
    WalletCall("rescan_blockchain", "", lambda w: w.rescan_blockchain()),

    # listeners
    WalletCall("add_listener", "listener", lambda w: w.add_listener(MoneroWalletListener())),
    WalletCall("remove_listener", "listener", lambda w: w.remove_listener(MoneroWalletListener())),
    WalletCall("get_listeners", "", lambda w: w.get_listeners()),

    # balances
    WalletCall("get_balance", "", lambda w: w.get_balance()),
    WalletCall("get_balance", "account_idx", lambda w: w.get_balance(0)),
    WalletCall("get_balance", "account_idx,subaddress_idx", lambda w: w.get_balance(0, 0)),
    WalletCall("get_unlocked_balance", "", lambda w: w.get_unlocked_balance()),
    WalletCall("get_unlocked_balance", "account_idx", lambda w: w.get_unlocked_balance(0)),
    WalletCall("get_unlocked_balance", "account_idx,subaddress_idx", lambda w: w.get_unlocked_balance(0, 0)),

    # accounts and subaddresses
    WalletCall("get_accounts", "", lambda w: w.get_accounts()),
    WalletCall("get_accounts", "include_subaddresses", lambda w: w.get_accounts(True)),
    WalletCall("get_accounts", "tag", lambda w: w.get_accounts("")),
    WalletCall("get_accounts", "include_subaddresses,tag", lambda w: w.get_accounts(True, "")),
    WalletCall("get_account", "account_idx", lambda w: w.get_account(0)),
    WalletCall("get_account", "account_idx,include_subaddresses", lambda w: w.get_account(0, True)),
    WalletCall("create_account", "label", lambda w: w.create_account()),
    WalletCall("set_account_label", "account_idx,label", lambda w: w.set_account_label(0, "")),
    WalletCall("get_subaddresses", "account_idx", lambda w: w.get_subaddresses(0)),
    WalletCall("get_subaddresses", "account_idx,subaddress_indices", lambda w: w.get_subaddresses(0, [0])),
    WalletCall("get_subaddress", "account_idx,subaddress_idx", lambda w: w.get_subaddress(0, 0)),
    WalletCall("create_subaddress", "account_idx,label", lambda w: w.create_subaddress(0, "")),
    WalletCall("set_subaddress_label", "account_idx,subaddress_idx,label", lambda w: w.set_subaddress_label(1, 1, "")),

    # account tags
    WalletCall("tag_accounts", "tag,account_indices", lambda w: w.tag_accounts("", [])),
    WalletCall("untag_accounts", "account_indices", lambda w: w.untag_accounts([])),
    WalletCall("get_account_tags", "", lambda w: w.get_account_tags()),
    WalletCall("set_account_tag_label", "tag,label", lambda w: w.set_account_tag_label("", "")),

    # txs, transfers and outputs
    WalletCall("get_tx", "tx_hash", lambda w: w.get_tx("")),
    WalletCall("get_txs", "", lambda w: w.get_txs()),
    WalletCall("get_txs", "tx_hashes", lambda w: w.get_txs([""])),
    WalletCall("get_txs", "query", lambda w: w.get_txs(MoneroTxQuery())),
    WalletCall("get_transfers", "", lambda w: w.get_transfers()),
    WalletCall("get_transfers", "query", lambda w: w.get_transfers(MoneroTransferQuery())),
    WalletCall("get_transfers", "account_idx", lambda w: w.get_transfers(0)),
    WalletCall("get_transfers", "account_idx,subaddress_idx", lambda w: w.get_transfers(0, 0)),
    WalletCall("get_incoming_transfers", "", lambda w: w.get_incoming_transfers()),
    WalletCall("get_incoming_transfers", "query", lambda w: w.get_incoming_transfers(MoneroTransferQuery())),
    WalletCall("get_outgoing_transfers", "", lambda w: w.get_outgoing_transfers()),
    WalletCall("get_outgoing_transfers", "query", lambda w: w.get_outgoing_transfers(MoneroTransferQuery())),
    WalletCall("get_outputs", "", lambda w: w.get_outputs()),
    WalletCall("get_outputs", "query", lambda w: w.get_outputs(MoneroOutputQuery())),
    WalletCall("export_outputs", "all", lambda w: w.export_outputs(True)),
    WalletCall("import_outputs", "outputs_hex", lambda w: w.import_outputs("")),
    WalletCall("export_key_images", "all", lambda w: w.export_key_images(True)),
    WalletCall("import_key_images", "key_images,offset", lambda w: w.import_key_images([])),
    WalletCall("get_new_key_images_from_last_import", "", lambda w: w.get_new_key_images_from_last_import()),
    WalletCall("freeze_output", "key_image", lambda w: w.freeze_output("")),
    WalletCall("thaw_output", "key_image", lambda w: w.thaw_output("")),
    WalletCall("is_output_frozen", "key_image", lambda w: w.is_output_frozen("")),

    # sending
    WalletCall("get_default_fee_priority", "", lambda w: w.get_default_fee_priority()),
    WalletCall("create_tx", "config", lambda w: w.create_tx(MoneroTxConfig())),
    WalletCall("create_txs", "config", lambda w: w.create_txs(MoneroTxConfig())),
    WalletCall("sweep_unlocked", "config", lambda w: w.sweep_unlocked(MoneroTxConfig())),
    WalletCall("sweep_output", "config", lambda w: w.sweep_output(MoneroTxConfig())),
    WalletCall("sweep_dust", "relay", lambda w: w.sweep_dust(True)),
    WalletCall("relay_tx", "tx_metadata", lambda w: w.relay_tx(StringUtils.get_random_string())),
    WalletCall("relay_tx", "tx", lambda w: w.relay_tx(_tx_with_metadata())),
    WalletCall("relay_txs", "txs", lambda w: w.relay_txs([_tx_with_metadata()])),
    WalletCall("relay_txs", "tx_metadatas", lambda w: w.relay_txs([StringUtils.get_random_string()])),
    WalletCall("describe_tx_set", "tx_set", lambda w: w.describe_tx_set(MoneroTxSet())),
    WalletCall("describe_unsigned_tx_set", "unsigned_tx_hex", lambda w: w.describe_unsigned_tx_set("")),
    WalletCall("describe_multisig_tx_set", "multisig_tx_hex", lambda w: w.describe_multisig_tx_set("")),
    WalletCall("sign_txs", "unsigned_tx_hex", lambda w: w.sign_txs("")),
    WalletCall("submit_txs", "signed_tx_hex", lambda w: w.submit_txs("")),

    # proofs
    WalletCall("get_tx_key", "tx_hash", lambda w: w.get_tx_key("")),
    WalletCall("check_tx_key", "tx_hash,tx_key,address", lambda w: w.check_tx_key("", "", "")),
    WalletCall("get_tx_proof", "tx_hash,address,message", lambda w: w.get_tx_proof("", "", "")),
    WalletCall("check_tx_proof", "tx_hash,address,message,signature", lambda w: w.check_tx_proof("", "", "", "")),
    WalletCall("get_spend_proof", "tx_hash,message", lambda w: w.get_spend_proof("", "")),
    WalletCall("check_spend_proof", "tx_hash,message,signature", lambda w: w.check_spend_proof("", "", "")),
    WalletCall("get_reserve_proof_wallet", "message", lambda w: w.get_reserve_proof_wallet("")),
    WalletCall("get_reserve_proof_account", "account_idx,amount,message", lambda w: w.get_reserve_proof_account(0, 0, "")),
    WalletCall("check_reserve_proof", "address,message,signature", lambda w: w.check_reserve_proof("", "", "")),

    # messages and payment uris
    WalletCall("sign_message", "msg,signature_type", lambda w: w.sign_message("", MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY)),
    WalletCall("verify_message", "msg,address,signature", lambda w: w.verify_message("", "", ""), in_base=True),
    WalletCall("get_payment_uri", "config", lambda w: w.get_payment_uri(MoneroTxConfig())),
    WalletCall("parse_payment_uri", "uri", lambda w: w.parse_payment_uri("")),

    # tx notes and address book
    WalletCall("get_tx_note", "tx_hash", lambda w: w.get_tx_note("")),
    WalletCall("get_tx_notes", "tx_hashes", lambda w: w.get_tx_notes(["", ""])),
    WalletCall("set_tx_note", "tx_hash,note", lambda w: w.set_tx_note("", "")),
    WalletCall("set_tx_notes", "tx_hashes,notes", lambda w: w.set_tx_notes([], [])),
    WalletCall("get_address_book_entries", "", lambda w: w.get_address_book_entries()),
    WalletCall("get_address_book_entries", "indices", lambda w: w.get_address_book_entries([])),
    WalletCall("add_address_book_entry", "address,description", lambda w: w.add_address_book_entry("", "")),
    WalletCall("edit_address_book_entry", "index,set_address,address,set_description,description",
               lambda w: w.edit_address_book_entry(1, False, "", True, "")),
    WalletCall("delete_address_book_entry", "index", lambda w: w.delete_address_book_entry(0)),

    # multisig
    WalletCall("is_multisig_import_needed", "", lambda w: w.is_multisig_import_needed()),
    WalletCall("is_multisig", "", lambda w: w.is_multisig()),
    WalletCall("get_multisig_info", "", lambda w: w.get_multisig_info()),
    WalletCall("prepare_multisig", "", lambda w: w.prepare_multisig()),
    WalletCall("make_multisig", "multisig_hexes,threshold,password", lambda w: w.make_multisig([], 0, "")),
    WalletCall("exchange_multisig_keys", "multisig_hexes,password", lambda w: w.exchange_multisig_keys([], "")),
    WalletCall("export_multisig_hex", "", lambda w: w.export_multisig_hex()),
    WalletCall("import_multisig_hex", "multisig_hexes,refresh_after_import", lambda w: w.import_multisig_hex([])),
    WalletCall("sign_multisig_tx_hex", "multisig_tx_hex", lambda w: w.sign_multisig_tx_hex("")),
    WalletCall("submit_multisig_tx_hex", "signed_multisig_tx_hex", lambda w: w.submit_multisig_tx_hex("")),

    # mining
    WalletCall("start_mining", "num_threads,background_mining,ignore_battery", lambda w: w.start_mining()),
    WalletCall("stop_mining", "", lambda w: w.stop_mining()),

    # closing
    WalletCall("is_closed", "", lambda w: w.is_closed()),
    WalletCall("close", "save", lambda w: w.close()),
]
