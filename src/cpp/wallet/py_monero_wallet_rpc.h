#pragma once

#include "py_monero_wallet.h"


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
  void set_daemon_connection(const std::string& uri, const std::string& username = "", const std::string& password = "", const std::string& proxy_uri = "") override;
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
  monero_account get_account(const uint32_t account_idx, bool include_subaddresses) const override;
  monero_account get_account(const uint32_t account_idx, bool include_subaddresses, bool skip_balances) const;
  std::vector<monero_account> get_accounts(bool include_subaddresses, const std::string& tag) const override;
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
  mutable serializable_unordered_map<uint32_t, serializable_unordered_map<uint32_t, std::string>> m_address_cache;

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
