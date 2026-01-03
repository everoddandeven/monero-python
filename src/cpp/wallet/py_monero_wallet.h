#pragma once

#include <pybind11/stl_bind.h>
#include <pybind11/eval.h>
#include "py_monero_wallet_model.h"
#include "daemon/py_monero_daemon.h"

void set_wallet_closed(const void* wallet, bool value);
bool is_wallet_closed(const void* wallet);
void assert_wallet_is_not_closed(const void* wallet);

class PyMoneroWalletConnectionManagerListener : public PyMoneroConnectionManagerListener {
public:
  PyMoneroWalletConnectionManagerListener(monero::monero_wallet* wallet);

  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection);

private:
  monero::monero_wallet *m_wallet;
};

class PyMoneroWalletListener : public monero_wallet_listener {
public:

  void on_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, double percent_done, const std::string& message) override;
  void on_new_block(uint64_t height) override;
  void on_balances_changed(uint64_t new_balance, uint64_t new_unlocked_balance) override;
  void on_output_received(const monero_output_wallet& output) override;
  void on_output_spent(const monero_output_wallet& output) override;
};

PYBIND11_MAKE_OPAQUE(std::vector<std::string>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_block>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_block_header>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_tx>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_tx_wallet>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_output>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_output_wallet>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_incoming_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_outgoing_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<monero::monero_subaddress>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_destination>>);

class PyMoneroWallet : public monero::monero_wallet {
public:
  using monero::monero_wallet::monero_wallet;

  virtual void tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) {
    PYBIND11_OVERRIDE_PURE(void, PyMoneroWallet, tag_accounts);
  }

  virtual void untag_accounts(const std::vector<uint32_t>& account_indices) {
    PYBIND11_OVERRIDE_PURE(void, PyMoneroWallet, untag_accounts);
  }

  virtual std::vector<std::shared_ptr<PyMoneroAccountTag>> get_account_tags() {
    PYBIND11_OVERRIDE_PURE(std::vector<std::shared_ptr<PyMoneroAccountTag>>, PyMoneroWallet, get_account_tags);
  }

  virtual void set_account_tag_label(const std::string& tag, const std::string& label) {
    PYBIND11_OVERRIDE_PURE(void, PyMoneroWallet, set_account_tag_label);
  }

  virtual void set_account_label(uint32_t account_idx, const std::string& label) {
    PYBIND11_OVERRIDE_PURE(void, PyMoneroWallet, set_account_label);
  }

  bool is_view_only() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_view_only);
  }

  void set_daemon_connection(const std::string& uri, const std::string& username = "", const std::string& password = "", const std::string& proxy = "") override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_daemon_connection, uri, username, password, proxy);
  }

  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection) override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_daemon_connection, connection);
  }

  boost::optional<monero_rpc_connection> get_daemon_connection() const override {
    PYBIND11_OVERRIDE(boost::optional<monero_rpc_connection>, monero_wallet, get_daemon_connection);
  }

  bool is_connected_to_daemon() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_connected_to_daemon);
  }

  bool is_daemon_synced() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_daemon_synced);
  }

  bool is_daemon_trusted() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_daemon_trusted);
  }

  bool is_synced() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_synced);
  }

  monero_version get_version() const override {
    PYBIND11_OVERRIDE(monero_version, monero_wallet, get_version);
  }

  monero_network_type get_network_type() const override {
    PYBIND11_OVERRIDE(monero_network_type, monero_wallet, get_network_type);
  }

  std::string get_seed() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_seed);
  }

  std::string get_seed_language() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_seed_language);
  }

  std::string get_public_view_key() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_public_view_key);
  }

  std::string get_private_view_key() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_private_view_key);
  }

  std::string get_public_spend_key() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_public_spend_key);
  }

  std::string get_private_spend_key() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_private_spend_key);
  }

  std::string get_primary_address() const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_primary_address);
  }

  std::string get_address(const uint32_t account_idx, const uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_address, account_idx, subaddress_idx);
  }

  monero_subaddress get_address_index(const std::string& address) const override {
    PYBIND11_OVERRIDE(monero_subaddress, monero_wallet, get_address_index, address);
  }

  monero_integrated_address get_integrated_address(const std::string& standard_address = "", const std::string& payment_id = "") const override {
    PYBIND11_OVERRIDE(monero_integrated_address, monero_wallet, get_integrated_address, standard_address, payment_id);
  }

  monero_integrated_address decode_integrated_address(const std::string& integrated_address) const override {
    PYBIND11_OVERRIDE(monero_integrated_address, monero_wallet, decode_integrated_address, integrated_address);
  }

  uint64_t get_height() const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_height);
  }

  uint64_t get_restore_height() const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_restore_height);
  }

  void set_restore_height(uint64_t restore_height) override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_restore_height, restore_height);
  }

  uint64_t get_daemon_height() const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_daemon_height);
  }

  uint64_t get_daemon_max_peer_height() const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_daemon_max_peer_height);
  }

  uint64_t get_height_by_date(uint16_t year, uint8_t month, uint8_t day) const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_height_by_date, year, month, day);
  }

  void add_listener(monero_wallet_listener& listener) override {
    m_listeners.insert(&listener);
  }

  void remove_listener(monero_wallet_listener& listener) override {
    m_listeners.erase(&listener);
  }
  
  std::set<monero_wallet_listener*> get_listeners() override {
    return m_listeners;
  }

  monero_sync_result sync() override {
    PYBIND11_OVERRIDE(monero_sync_result, monero_wallet, sync);
  }

  monero_sync_result sync(monero_wallet_listener& listener) override {
    PYBIND11_OVERRIDE(monero_sync_result, monero_wallet, sync, listener);
  }

  monero_sync_result sync(uint64_t start_height) override {
    PYBIND11_OVERRIDE(monero_sync_result, monero_wallet, sync, start_height);
  }

  monero_sync_result sync(uint64_t start_height, monero_wallet_listener& listener) override {
    PYBIND11_OVERRIDE(monero_sync_result, monero_wallet, sync, start_height, listener);
  }

  void start_syncing(uint64_t sync_period_in_ms = 10000) override {
    PYBIND11_OVERRIDE(void, monero_wallet, start_syncing, sync_period_in_ms);
  }

  void scan_txs(const std::vector<std::string>& tx_hashes) override {
    PYBIND11_OVERRIDE(void, monero_wallet, scan_txs, tx_hashes);
  }

  void rescan_spent() override {
    PYBIND11_OVERRIDE(void, monero_wallet, rescan_spent);
  }

  void rescan_blockchain() override {
    PYBIND11_OVERRIDE(void, monero_wallet, rescan_blockchain);
  }

  uint64_t get_balance() const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_balance);
  }

  uint64_t get_balance(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_balance, account_idx);
  }

  uint64_t get_balance(uint32_t account_idx, uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_balance, account_idx, subaddress_idx);
  }

  uint64_t get_unlocked_balance() const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_unlocked_balance);
  }

  uint64_t get_unlocked_balance(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_unlocked_balance, account_idx);
  }

  uint64_t get_unlocked_balance(uint32_t account_idx, uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, get_unlocked_balance, account_idx, subaddress_idx);
  }

  std::vector<monero_account> get_accounts() const override {
    PYBIND11_OVERRIDE(std::vector<monero_account>, monero_wallet, get_accounts);
  }

  std::vector<monero_account> get_accounts(bool include_subaddresses) const override {
    PYBIND11_OVERRIDE(std::vector<monero_account>, monero_wallet, get_accounts, include_subaddresses);
  }

  std::vector<monero_account> get_accounts(const std::string& tag) const override {
    PYBIND11_OVERRIDE(std::vector<monero_account>, monero_wallet, get_accounts, tag);
  }

  std::vector<monero_account> get_accounts(bool include_subaddresses, const std::string& tag) const override {
    PYBIND11_OVERRIDE(std::vector<monero_account>, monero_wallet, get_accounts, include_subaddresses, tag);
  }

  monero_account get_account(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(monero_account, monero_wallet, get_account, account_idx);
  }

  monero_account get_account(const uint32_t account_idx, bool include_subaddresses) const {
    PYBIND11_OVERRIDE(monero_account, monero_wallet, get_account, account_idx, include_subaddresses);
  }

  monero_account create_account(const std::string& label = "") override {
    PYBIND11_OVERRIDE(monero_account, monero_wallet, create_account, label);
  }

  std::vector<monero_subaddress> get_subaddresses(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(std::vector<monero_subaddress>, monero_wallet, get_subaddresses, account_idx);
  }

  std::vector<monero_subaddress> get_subaddresses(uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) const override {
    PYBIND11_OVERRIDE(std::vector<monero_subaddress>, monero_wallet, get_subaddresses, account_idx, subaddress_indices);
  }

  monero_subaddress get_subaddress(uint32_t account_idx, uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(monero_subaddress, monero_wallet, get_subaddress, account_idx, subaddress_idx);
  }

  monero_subaddress create_subaddress(uint32_t account_idx, const std::string& label = "") override {
    PYBIND11_OVERRIDE(monero_subaddress, monero_wallet, create_subaddress, account_idx, label);
  }

  void set_subaddress_label(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label = "") override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_subaddress_label, account_idx, subaddress_idx, label);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> get_txs() const override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx_wallet>>, monero_wallet, get_txs);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> get_txs(const monero_tx_query& query) const override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx_wallet>>, monero_wallet, get_txs, query);
  }

  std::vector<std::shared_ptr<monero_transfer>> get_transfers(const monero_transfer_query& query) const override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_transfer>>, monero_wallet, get_transfers, query);
  }

  std::vector<std::shared_ptr<monero_output_wallet>> get_outputs(const monero_output_query& query) const override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_output_wallet>>, monero_wallet, get_outputs, query);
  }

  std::string export_outputs(bool all = false) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, export_outputs, all);
  }

  int import_outputs(const std::string& outputs_hex) override {
    PYBIND11_OVERRIDE(int, monero_wallet, import_outputs, outputs_hex);
  }

  std::vector<std::shared_ptr<monero_key_image>> export_key_images(bool all = false) const override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_key_image>>, monero_wallet, export_key_images, all);
  }

  std::shared_ptr<monero_key_image_import_result> import_key_images(const std::vector<std::shared_ptr<monero_key_image>>& key_images) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_key_image_import_result>, monero_wallet, import_key_images, key_images);
  }

  virtual std::vector<std::shared_ptr<monero_key_image>> get_new_key_images_from_last_import() {
    PYBIND11_OVERRIDE_PURE(std::vector<std::shared_ptr<monero_key_image>>, PyMoneroWallet, get_new_key_images_from_last_import);
  }

  void freeze_output(const std::string& key_image) override {
    PYBIND11_OVERRIDE(void, monero_wallet, freeze_output, key_image);
  }

  void thaw_output(const std::string& key_image) override {
    PYBIND11_OVERRIDE(void, monero_wallet, thaw_output, key_image);
  }

  bool is_output_frozen(const std::string& key_image) override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_output_frozen, key_image);
  }

  monero_tx_priority get_default_fee_priority() const override {
    PYBIND11_OVERRIDE(monero_tx_priority, monero_wallet, get_default_fee_priority);
  }

  std::shared_ptr<monero_tx_wallet> create_tx(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_tx_wallet>, monero_wallet, create_tx, config);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> create_txs(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx_wallet>>, monero_wallet, create_txs, config);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_unlocked(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx_wallet>>, monero_wallet, sweep_unlocked, config);
  }

  std::shared_ptr<monero_tx_wallet> sweep_output(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_tx_wallet>, monero_wallet, sweep_output, config);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_dust(bool relay) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx_wallet>>, monero_wallet, sweep_dust, relay);
  }

  std::string relay_tx(const std::string& tx_metadata) override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, relay_tx, tx_metadata);
  }

  std::string relay_tx(const monero_tx_wallet& tx) override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, relay_tx, tx);
  }

  std::vector<std::string> relay_txs(const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_wallet, relay_txs, txs);
  }

  std::vector<std::string> relay_txs(const std::vector<std::string>& tx_metadatas) override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_wallet, relay_txs, tx_metadatas);
  }

  monero_tx_set describe_tx_set(const monero_tx_set& tx_set) override {
    PYBIND11_OVERRIDE(monero_tx_set, monero_wallet, describe_tx_set, tx_set);
  }

  monero_tx_set sign_txs(const std::string& unsigned_tx_hex) override {
    PYBIND11_OVERRIDE(monero_tx_set, monero_wallet, sign_txs, unsigned_tx_hex);
  }

  std::vector<std::string> submit_txs(const std::string& signed_tx_hex) override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_wallet, submit_txs, signed_tx_hex);
  }

  std::string sign_message(const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx = 0, uint32_t subaddress_idx = 0) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, sign_message, msg, signature_type, account_idx, subaddress_idx);
  }

  monero_message_signature_result verify_message(const std::string& msg, const std::string& address, const std::string& signature) const override {
    PYBIND11_OVERRIDE(monero_message_signature_result, monero_wallet, verify_message, msg, address, signature);
  }

  std::string get_tx_key(const std::string& tx_hash) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_tx_key, tx_hash);
  }

  std::shared_ptr<monero_check_tx> check_tx_key(const std::string& tx_hash, const std::string& tx_key, const std::string& address) const override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_check_tx>, monero_wallet, check_tx_key, tx_hash, tx_key, address);
  }

  std::string get_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_tx_proof, tx_hash, address, message);
  }

  std::shared_ptr<monero_check_tx> check_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) const override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_check_tx>, monero_wallet, check_tx_proof, tx_hash, address, message, signature);
  }

  std::string get_spend_proof(const std::string& tx_hash, const std::string& message) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_spend_proof, tx_hash, message);
  }

  bool check_spend_proof(const std::string& tx_hash, const std::string& message, const std::string& signature) const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, check_spend_proof, tx_hash, message, signature);
  }

  std::string get_reserve_proof_wallet(const std::string& message) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_reserve_proof_wallet, message);
  }

  std::string get_reserve_proof_account(uint32_t account_idx, uint64_t amount, const std::string& message) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_reserve_proof_account, account_idx, amount, message);
  }

  std::shared_ptr<monero_check_reserve> check_reserve_proof(const std::string& address, const std::string& message, const std::string& signature) const override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_check_reserve>, monero_wallet, check_reserve_proof, address, message, signature);
  }

  std::string get_tx_note(const std::string& tx_hash) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_tx_note, tx_hash);
  }

  std::vector<std::string> get_tx_notes(const std::vector<std::string>& tx_hashes) const override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_wallet, get_tx_notes, tx_hashes);
  }

  void set_tx_note(const std::string& tx_hash, const std::string& note) override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_tx_note, tx_hash, note);
  }

  void set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_tx_notes, tx_hashes, notes);
  }

  std::vector<monero_address_book_entry> get_address_book_entries(const std::vector<uint64_t>& indices) const override {
    PYBIND11_OVERRIDE(std::vector<monero_address_book_entry>, monero_wallet, get_address_book_entries, indices);
  }

  uint64_t add_address_book_entry(const std::string& address, const std::string& description) override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, add_address_book_entry, address, description);
  }

  void edit_address_book_entry(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) override {
    PYBIND11_OVERRIDE(void, monero_wallet, edit_address_book_entry, index, set_address, address, set_description, description);
  }

  void delete_address_book_entry(uint64_t index) override {
    PYBIND11_OVERRIDE(void, monero_wallet, delete_address_book_entry, index);
  }

  std::string get_payment_uri(const monero_tx_config& config) const override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, get_payment_uri, config);
  }

  std::shared_ptr<monero_tx_config> parse_payment_uri(const std::string& uri) const override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_tx_config>, monero_wallet, parse_payment_uri, uri);
  }

  bool get_attribute(const std::string& key, std::string& value) const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, get_attribute, key, value);
  }

  void set_attribute(const std::string& key, const std::string& val) override {
    PYBIND11_OVERRIDE(void, monero_wallet, set_attribute, key, val);
  }

  void start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) {
    PYBIND11_OVERRIDE(void, monero_wallet, start_mining, num_threads, background_mining, ignore_battery);
  }

  void stop_mining() override {
    PYBIND11_OVERRIDE(void, monero_wallet, stop_mining);
  }

  uint64_t wait_for_next_block() override {
    PYBIND11_OVERRIDE(uint64_t, monero_wallet, wait_for_next_block);
  }

  bool is_multisig_import_needed() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_multisig_import_needed);
  }

  bool is_multisig() const override {
    PYBIND11_OVERRIDE(bool, monero_wallet, is_multisig);
  }

  monero_multisig_info get_multisig_info() const override {
    PYBIND11_OVERRIDE(monero_multisig_info, monero_wallet, get_multisig_info);
  }

  std::string prepare_multisig() override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, prepare_multisig);
  }

  std::string make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, make_multisig, multisig_hexes, threshold, password);
  }

  monero_multisig_init_result exchange_multisig_keys(const std::vector<std::string>& multisig_hexes, const std::string& password) override {
    PYBIND11_OVERRIDE(monero_multisig_init_result, monero_wallet, exchange_multisig_keys, multisig_hexes, password);
  }

  std::string export_multisig_hex() override {
    PYBIND11_OVERRIDE(std::string, monero_wallet, export_multisig_hex);
  }

  int import_multisig_hex(const std::vector<std::string>& multisig_hexes) override {
    PYBIND11_OVERRIDE(int, monero_wallet, import_multisig_hex, multisig_hexes);
  }

  monero_multisig_sign_result sign_multisig_tx_hex(const std::string& multisig_tx_hex) override {
    PYBIND11_OVERRIDE(monero_multisig_sign_result, monero_wallet, sign_multisig_tx_hex, multisig_tx_hex);
  }

  std::vector<std::string> submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex) override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_wallet, submit_multisig_tx_hex, signed_multisig_tx_hex);
  }

  void change_password(const std::string& old_password, const std::string& new_password) override {
    PYBIND11_OVERRIDE(void, monero_wallet, change_password, old_password, new_password);
  }

  void move_to(const std::string& path, const std::string& password) override {
    PYBIND11_OVERRIDE(void, monero_wallet, move_to, path, password);
  }

  void save() override {
    PYBIND11_OVERRIDE(void, monero_wallet, save);
  }

  void close(bool save = false) override {
    PYBIND11_OVERRIDE(void, monero_wallet, close, save);
  }

  virtual void set_connection_manager(const std::shared_ptr<PyMoneroConnectionManager> &connection_manager);
  virtual std::optional<std::shared_ptr<PyMoneroConnectionManager>> get_connection_manager() const;
  virtual void announce_new_block(uint64_t height);
  virtual void announce_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, float percent_done, const std::string &message);
  virtual void announce_balances_changed(uint64_t balance, uint64_t unlocked_balance);
  virtual void announce_output_spent(const std::shared_ptr<monero::monero_output_wallet> &output);
  virtual void announce_output_received(const std::shared_ptr<monero::monero_output_wallet> &output);
  virtual std::shared_ptr<PyMoneroWalletBalance> get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const;
  virtual bool is_closed() const { return m_is_closed; }

protected:
  bool m_is_closed = false;
  std::shared_ptr<PyMoneroConnectionManager> m_connection_manager;
  std::shared_ptr<PyMoneroWalletConnectionManagerListener> m_connection_manager_listener;
  std::set<monero::monero_wallet_listener*> m_listeners;
};

class PyMoneroWalletFull : public monero::monero_wallet_full {
public:

  bool is_closed() const { return m_is_closed; }
  void close(bool save = false) override;
  void set_account_label(uint32_t account_idx, const std::string& label);

  std::vector<std::shared_ptr<monero_key_image>> get_new_key_images_from_last_import() {
    throw std::runtime_error("get_new_key_images_from_last_import(): not implemented");
  }

protected:
  bool m_is_closed = false;
};

class PyMoneroWalletPoller {
public:
  explicit PyMoneroWalletPoller(PyMoneroWallet *wallet) {
    m_wallet = wallet;
    m_is_polling = false;
    m_num_polling = 0;
  }

  ~PyMoneroWalletPoller();

  bool is_polling() const { return m_is_polling; }
  void set_is_polling(bool is_polling);
  void set_period_in_ms(uint64_t period_ms);
  void poll();

protected:
  mutable boost::recursive_mutex m_mutex;
  PyMoneroWallet *m_wallet;
  std::atomic<bool> m_is_polling;
  uint64_t m_poll_period_ms;
  std::thread m_thread;
  int m_num_polling;
  std::vector<std::string> m_prev_unconfirmed_notifications;
  std::vector<std::string> m_prev_confirmed_notifications;

  boost::optional<std::shared_ptr<PyMoneroWalletBalance>> m_prev_balances;
  boost::optional<uint64_t> m_prev_height;
  std::vector<std::shared_ptr<monero::monero_tx_wallet>> m_prev_locked_txs;

  std::shared_ptr<monero::monero_tx_wallet> get_tx(const std::vector<std::shared_ptr<monero::monero_tx_wallet>>& txs, const std::string& tx_hash);
  void loop();
  void on_new_block(uint64_t height);
  void notify_outputs(const std::shared_ptr<monero::monero_tx_wallet> &tx);
  bool check_for_changed_balances();
};

class PyMoneroWalletRpc : public PyMoneroWallet {
public:

  PyMoneroWalletRpc() {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroWalletRpc(std::shared_ptr<PyMoneroRpcConnection> rpc_connection) {
    m_rpc = rpc_connection;
    if (!m_rpc->is_online() && !m_rpc->m_uri->empty()) m_rpc->check_connection();
  }

  PyMoneroWalletRpc(const std::string& uri = "", const std::string& username = "", const std::string& password = "") {
    m_rpc = std::make_shared<PyMoneroRpcConnection>(uri, username, password);
    if (!m_rpc->m_uri->empty()) m_rpc->check_connection();
  }

  ~PyMoneroWalletRpc();

  PyMoneroWalletRpc* open_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config);
  PyMoneroWalletRpc* open_wallet(const std::string& name, const std::string& password);
  PyMoneroWalletRpc* create_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config);
  boost::optional<monero::monero_rpc_connection> get_rpc_connection() const;
  std::vector<std::string> get_seed_languages() const;
  void stop();
  bool is_view_only() const override;
  boost::optional<monero::monero_rpc_connection> get_daemon_connection() const override;
  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection, bool is_trusted, const boost::optional<std::shared_ptr<PyMoneroSslOptions>> ssl_options);
  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection) override;
  bool is_connected_to_daemon() const override;
  monero::monero_version get_version() const override;
  std::string get_path() const override;
  std::string get_seed() const override;
  std::string get_seed_language() const override;
  std::string get_public_view_key() const override;
  std::string get_private_view_key() const override;
  std::string get_public_spend_key() const override;
  std::string get_private_spend_key() const override;
  std::string get_address(const uint32_t account_idx, const uint32_t subaddress_idx) const override;
  monero_subaddress get_address_index(const std::string& address) const override;
  monero_integrated_address get_integrated_address(const std::string& standard_address = "", const std::string& payment_id = "") const override;
  monero_integrated_address decode_integrated_address(const std::string& integrated_address) const override;
  uint64_t get_height() const override;
  uint64_t get_daemon_height() const override;
  uint64_t get_height_by_date(uint16_t year, uint8_t month, uint8_t day) const override;
  monero_sync_result sync() override;
  monero_sync_result sync(monero_wallet_listener& listener) override;
  monero_sync_result sync(uint64_t start_height, monero_wallet_listener& listener) override;
  monero_sync_result sync(uint64_t start_height) override;
  void start_syncing(uint64_t sync_period_in_ms = 10000) override;
  void stop_syncing() override;
  void scan_txs(const std::vector<std::string>& tx_hashes) override;
  void rescan_spent() override;
  void rescan_blockchain() override;
  uint64_t get_balance() const override;
  uint64_t get_balance(uint32_t account_index) const override;
  uint64_t get_balance(uint32_t account_idx, uint32_t subaddress_idx) const override;
  uint64_t get_unlocked_balance() const override;
  uint64_t get_unlocked_balance(uint32_t account_index) const override;
  uint64_t get_unlocked_balance(uint32_t account_idx, uint32_t subaddress_idx) const override;
  std::vector<monero_account> get_accounts(bool include_subaddresses, const std::string& tag, bool skip_balances) const;
  monero_account create_account(const std::string& label = "") override;
  std::vector<monero_subaddress> get_subaddresses(const uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices, bool skip_balances) const;
  std::vector<monero_subaddress> get_subaddresses(uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) const override;
  std::vector<monero_subaddress> get_subaddresses(const uint32_t account_idx) const override;
  monero_subaddress get_subaddress(const uint32_t account_idx, const uint32_t subaddress_idx) const override;
  monero_subaddress create_subaddress(uint32_t account_idx, const std::string& label = "") override;
  void set_subaddress_label(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label = "") override;
  std::string export_outputs(bool all = false) const override;
  int import_outputs(const std::string& outputs_hex) override;
  std::vector<std::shared_ptr<monero_key_image>> export_key_images(bool all = false) const override;
  std::shared_ptr<monero_key_image_import_result> import_key_images(const std::vector<std::shared_ptr<monero_key_image>>& key_images) override;
  std::vector<std::shared_ptr<monero_key_image>> get_new_key_images_from_last_import() override;
  void freeze_output(const std::string& key_image) override;
  void thaw_output(const std::string& key_image) override;
  bool is_output_frozen(const std::string& key_image) override;
  monero_tx_priority get_default_fee_priority() const override;
  std::vector<std::shared_ptr<monero_tx_wallet>> create_txs(const monero_tx_config& conf) override;
  std::shared_ptr<monero_tx_wallet> sweep_output(const monero_tx_config& config) override;
  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_dust(bool relay = false) override;
  std::vector<std::string> relay_txs(const std::vector<std::string>& tx_metadatas) override;
  monero_tx_set describe_tx_set(const monero_tx_set& tx_set) override;
  monero_tx_set sign_txs(const std::string& unsigned_tx_hex) override;
  std::vector<std::string> submit_txs(const std::string& signed_tx_hex) override;
  std::string sign_message(const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx = 0, uint32_t subaddress_idx = 0) const override;
  monero_message_signature_result verify_message(const std::string& msg, const std::string& address, const std::string& signature) const override;
  std::string get_tx_key(const std::string& tx_hash) const override;
  std::shared_ptr<monero_check_tx> check_tx_key(const std::string& tx_hash, const std::string& tx_key, const std::string& address) const override;
  std::string get_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message) const override;
  // TODO why no override ?
  std::shared_ptr<monero_check_tx> check_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) const;
  std::string get_spend_proof(const std::string& tx_hash, const std::string& message) const override;
  bool check_spend_proof(const std::string& tx_hash, const std::string& message, const std::string& signature) const override;
  std::string get_reserve_proof_wallet(const std::string& message) const override;
  std::string get_reserve_proof_account(uint32_t account_idx, uint64_t amount, const std::string& message) const override;
  std::shared_ptr<monero_check_reserve> check_reserve_proof(const std::string& address, const std::string& message, const std::string& signature) const override;
  std::vector<std::string> get_tx_notes(const std::vector<std::string>& tx_hashes) const override;
  void set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) override;
  std::vector<monero_address_book_entry> get_address_book_entries(const std::vector<uint64_t>& indices) const override;
  uint64_t add_address_book_entry(const std::string& address, const std::string& description) override;
  void edit_address_book_entry(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) override;
  void delete_address_book_entry(uint64_t index) override;
  void tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) override;
  void untag_accounts(const std::vector<uint32_t>& account_indices) override;
  std::vector<std::shared_ptr<PyMoneroAccountTag>> get_account_tags() override;
  void set_account_tag_label(const std::string& tag, const std::string& label) override;
  void set_account_label(uint32_t account_index, const std::string& label) override;
  std::string get_payment_uri(const monero_tx_config& config) const override;
  // TODO why no override ?
  std::shared_ptr<monero_tx_config> parse_payment_uri(const std::string& uri) const;
  void set_attribute(const std::string& key, const std::string& val) override;
  bool get_attribute(const std::string& key, std::string& value) const override;
  void start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) override;
  void stop_mining() override;
  bool is_multisig_import_needed() const override;
  monero_multisig_info get_multisig_info() const override;
  std::string prepare_multisig() override;
  std::string make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) override;
  monero_multisig_init_result exchange_multisig_keys(const std::vector<std::string>& multisig_hexes, const std::string& password);
  std::string export_multisig_hex() override;
  int import_multisig_hex(const std::vector<std::string>& multisig_hexes) override;
  monero_multisig_sign_result sign_multisig_tx_hex(const std::string& multisig_tx_hex) override;
  std::vector<std::string> submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex);
  void change_password(const std::string& old_password, const std::string& new_password) override;
  void save() override;
  void close(bool save = false) override;
  std::shared_ptr<PyMoneroWalletBalance> get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const override;

protected:
  inline static const uint64_t DEFAULT_SYNC_PERIOD_IN_MS = 20000;
  boost::optional<uint64_t> m_sync_period_in_ms;
  std::string m_path = "";
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;
  std::shared_ptr<PyMoneroRpcConnection> m_daemon_connection;
  std::shared_ptr<PyMoneroWalletPoller> m_poller;

  mutable boost::recursive_mutex m_sync_mutex;
  serializable_unordered_map<uint32_t, serializable_unordered_map<uint32_t, std::string>> m_address_cache;

  PyMoneroWalletRpc* create_wallet_random(const std::shared_ptr<PyMoneroWalletConfig> &conf);
  PyMoneroWalletRpc* create_wallet_from_seed(const std::shared_ptr<PyMoneroWalletConfig> &conf);
  PyMoneroWalletRpc* create_wallet_from_keys(const std::shared_ptr<PyMoneroWalletConfig> &config);

  std::string query_key(const std::string& key_type) const;
  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_account(const monero_tx_config &conf);
  void clear_address_cache();
  void refresh_listening();
  void poll();
  void clear();
};
