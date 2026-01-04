#include "py_monero_wallet.h"

namespace {
  std::unordered_map<const void*, bool> wallet_closed_map;
  std::mutex wallet_map_mutex;
}

void set_wallet_closed(const void* wallet, bool value) {
  std::lock_guard<std::mutex> lock(wallet_map_mutex);
  wallet_closed_map[wallet] = value;
}

bool is_wallet_closed(const void* wallet) {
  std::lock_guard<std::mutex> lock(wallet_map_mutex);
  auto it = wallet_closed_map.find(wallet);
  return it != wallet_closed_map.end() ? it->second : false;
}

void assert_wallet_is_not_closed(const void* wallet) {
  if (is_wallet_closed(wallet)) throw std::runtime_error("Wallet is closed");
}

PyMoneroWalletConnectionManagerListener::PyMoneroWalletConnectionManagerListener(monero::monero_wallet* wallet) {
  m_wallet = wallet;
}

void PyMoneroWalletConnectionManagerListener::on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection) {
  if (m_wallet != nullptr) m_wallet->set_daemon_connection(*connection);
}

void PyMoneroWalletListener::on_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, double percent_done, const std::string& message) {
  PYBIND11_OVERRIDE(
    void,                               
    monero_wallet_listener,
    on_sync_progress,
    height, start_height, end_height, percent_done, message
  );
}

void PyMoneroWalletListener::on_new_block(uint64_t height) {
  PYBIND11_OVERRIDE(
    void,                               
    monero_wallet_listener,
    on_new_block,
    height
  );
}

void PyMoneroWalletListener::on_balances_changed(uint64_t new_balance, uint64_t new_unlocked_balance) {
  PYBIND11_OVERRIDE(
    void,                               
    monero_wallet_listener,
    on_balances_changed,
    new_balance, new_unlocked_balance
  );
}

void PyMoneroWalletListener::on_output_received(const monero_output_wallet& output) {
  PYBIND11_OVERRIDE(
    void,                               
    monero_wallet_listener,
    on_output_received,
    output
  );
}

void PyMoneroWalletListener::on_output_spent(const monero_output_wallet& output) {
  PYBIND11_OVERRIDE(
    void,                               
    monero_wallet_listener,
    on_output_spent,
    output
  );
}

void PyMoneroWallet::set_connection_manager(const std::shared_ptr<PyMoneroConnectionManager> &connection_manager) {
  if (m_connection_manager != nullptr) m_connection_manager->remove_listener(m_connection_manager_listener);
  m_connection_manager = connection_manager;
  if (m_connection_manager == nullptr) return;
  if (m_connection_manager_listener == nullptr) m_connection_manager_listener = std::make_shared<PyMoneroWalletConnectionManagerListener>(this);
  connection_manager->add_listener(m_connection_manager_listener);
  auto connection = connection_manager->get_connection();
  if (connection) set_daemon_connection(*connection);
}

std::optional<std::shared_ptr<PyMoneroConnectionManager>> PyMoneroWallet::get_connection_manager() const {
  std::optional<std::shared_ptr<PyMoneroConnectionManager>> result;
  if (m_connection_manager != nullptr) result = m_connection_manager;
  return result;
}

void PyMoneroWallet::announce_new_block(uint64_t height) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_new_block(height);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, float percent_done, const std::string &message) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_sync_progress(height, start_height, end_height, percent_done, message);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_balances_changed(uint64_t balance, uint64_t unlocked_balance) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_balances_changed(balance, unlocked_balance);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_output_spent(const std::shared_ptr<monero::monero_output_wallet> &output) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_output_spent(*output);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_output_received(const std::shared_ptr<monero::monero_output_wallet> &output) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_output_received(*output);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

std::shared_ptr<PyMoneroWalletBalance> PyMoneroWallet::get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const {
  throw std::runtime_error("MoneroWallet::get_balances(): not implemented");
}

void PyMoneroWalletFull::close(bool save) {
  if (m_is_closed) throw std::runtime_error("Wallet already closed");
  monero::monero_wallet_full::close(save);
}

void PyMoneroWalletFull::set_account_label(uint32_t account_idx, const std::string& label) {
  set_subaddress_label(account_idx, 0, label);
}

PyMoneroWalletPoller::~PyMoneroWalletPoller() {
  set_is_polling(false);
}

void PyMoneroWalletPoller::set_is_polling(bool is_polling) {
  if (is_polling == m_is_polling) return;
  m_is_polling = is_polling;

  if (m_is_polling) {
    m_thread = std::thread([this]() {
      loop();
    });
    m_thread.detach();
  } else {
    if (m_thread.joinable()) m_thread.join();
  }
}

void PyMoneroWalletPoller::set_period_in_ms(uint64_t period_ms) {
  m_poll_period_ms = period_ms;
}

void PyMoneroWalletPoller::poll() {
  if (m_num_polling > 1) return;
  m_num_polling++;

  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  try {
    // skip if wallet is closed
    if (m_wallet->is_closed()) {
      m_num_polling--;
      return;
    }

    if (m_prev_balances == boost::none) {
      m_prev_height = m_wallet->get_height();
      monero::monero_tx_query tx_query;
      tx_query.m_is_locked = true;
      m_prev_locked_txs = m_wallet->get_txs(tx_query);
      m_prev_balances = m_wallet->get_balances(boost::none, boost::none);
      m_num_polling--;
      return;
    }

    // announce height changes
    uint64_t height = m_wallet->get_height();
    if (m_prev_height.get() != height) {
      for (uint64_t i = m_prev_height.get(); i < height; i++) {
        on_new_block(i);
      }

      m_prev_height = height;
    }
    
    // get locked txs for comparison to previous
    uint64_t min_height = 0; // only monitor recent txs
    if (height > 70) min_height = height - 70; 
    monero::monero_tx_query tx_query;
    tx_query.m_is_locked = true;
    tx_query.m_min_height = min_height;
    tx_query.m_include_outputs = true;

    auto locked_txs = m_wallet->get_txs(tx_query);

    // collect hashes of txs no longer locked
    std::vector<std::string> no_longer_locked_hashes;
    for (const auto &prev_locked_tx : m_prev_locked_txs) {
      if (get_tx(locked_txs, prev_locked_tx->m_hash.get()) == nullptr) {
        no_longer_locked_hashes.push_back(prev_locked_tx->m_hash.get());
      }
    }
    m_prev_locked_txs = locked_txs;
    std::vector<std::shared_ptr<monero::monero_tx_wallet>> unlocked_txs;

    if (!no_longer_locked_hashes.empty()) {
      monero_tx_query tx_query;
      tx_query.m_is_locked = false;
      tx_query.m_min_height = min_height;
      tx_query.m_hashes = no_longer_locked_hashes;
      tx_query.m_include_outputs = true;
      unlocked_txs = m_wallet->get_txs(tx_query);
    }

    // announce new unconfirmed and confirmed txs
    for (const auto &locked_tx : locked_txs) {
      if (locked_tx->m_is_confirmed) {
        m_prev_confirmed_notifications.push_back(locked_tx->m_hash.get());
        notify_outputs(locked_tx);
      }
      else {
        m_prev_unconfirmed_notifications.push_back(locked_tx->m_hash.get());
      }
    }
    
    // announce new unlocked outputs
    for (const auto &unlocked_tx : unlocked_txs) {
      std::string tx_hash = unlocked_tx->m_hash.get();
      m_prev_confirmed_notifications.erase(std::remove_if(m_prev_confirmed_notifications.begin(), m_prev_confirmed_notifications.end(), [&tx_hash](const std::string& iter){ return iter == tx_hash; }), m_prev_confirmed_notifications.end());
      m_prev_unconfirmed_notifications.erase(std::remove_if(m_prev_unconfirmed_notifications.begin(), m_prev_unconfirmed_notifications.end(), [&tx_hash](const std::string& iter){ return iter == tx_hash; }), m_prev_unconfirmed_notifications.end());
      notify_outputs(unlocked_tx);
    }

    check_for_changed_balances();

    m_num_polling--;
  }
  catch (const std::exception &e) {
    m_num_polling--;
    if (m_is_polling) {
      std::cout << "Failed to background poll wallet " << m_wallet->get_path() << ": " << e.what() << std::endl;
    }
  }
}

std::shared_ptr<monero::monero_tx_wallet> PyMoneroWalletPoller::get_tx(const std::vector<std::shared_ptr<monero::monero_tx_wallet>>& txs, const std::string& tx_hash) {
  for (auto tx : txs) {
    if (tx->m_hash == tx_hash) return tx;
  }

  return nullptr;
}

void PyMoneroWalletPoller::loop() {
  while (m_is_polling) {
    try {
      poll();
    } catch (const std::exception& e) {
      std::cout << "ERROR " << e.what() << std::endl;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(m_poll_period_ms));
  }
}

void PyMoneroWalletPoller::on_new_block(uint64_t height) {
  m_wallet->announce_new_block(height);
}

void PyMoneroWalletPoller::notify_outputs(const std::shared_ptr<monero::monero_tx_wallet> &tx) {
  if (tx->m_outgoing_transfer != boost::none) {
    auto outgoing_transfer = tx->m_outgoing_transfer.get();
    if (!tx->m_inputs.empty()) throw std::runtime_error("Tx inputs should be empty");
    auto output = std::make_shared<monero::monero_output_wallet>();
    output->m_amount = outgoing_transfer->m_amount.get() + tx->m_fee.get();
    output->m_account_index = outgoing_transfer->m_account_index;
    output->m_tx = tx;
    if (outgoing_transfer->m_subaddress_indices.size() == 1) {
      output->m_subaddress_index = outgoing_transfer->m_subaddress_indices[0];
    }
    tx->m_inputs.push_back(output);
    m_wallet->announce_output_spent(output);
  }

  if (tx->m_incoming_transfers.size() > 0) {
    if (!tx->m_outputs.empty()) {
      for(const auto &output : tx->get_outputs_wallet()) {
        m_wallet->announce_output_received(output);
      }
    }
    else {
      for (const auto &transfer : tx->m_incoming_transfers) {
        auto output = std::make_shared<monero::monero_output_wallet>();
        output->m_account_index = transfer->m_account_index;
        output->m_subaddress_index = transfer->m_subaddress_index;
        output->m_amount = transfer->m_amount.get();
        output->m_tx = tx;
        tx->m_outputs.push_back(output);
      }

      for (const auto &output : tx->get_outputs_wallet()) {
        m_wallet->announce_output_received(output);
      }
    }
  }
} 

bool PyMoneroWalletPoller::check_for_changed_balances() {
  auto balances = m_wallet->get_balances(boost::none, boost::none);
  if (balances->m_balance != m_prev_balances.get()->m_balance || balances->m_unlocked_balance != m_prev_balances.get()->m_unlocked_balance) {
    m_prev_balances = balances;
    m_wallet->announce_balances_changed(balances->m_balance, balances->m_unlocked_balance);
    return true;
  }
  return false;
}

PyMoneroWalletRpc::~PyMoneroWalletRpc() {
}

boost::optional<monero::monero_rpc_connection> PyMoneroWalletRpc::get_rpc_connection() const {
  if (m_rpc == nullptr) return boost::none;
  return boost::optional<monero::monero_rpc_connection>(*m_rpc);
}

PyMoneroWalletRpc* PyMoneroWalletRpc::open_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config) {
  if (config == nullptr) throw std::runtime_error("Must provide configuration of wallet to open");
  if (config->m_path == boost::none || config->m_path->empty()) throw std::runtime_error("Filename is not initialized");
  std::string path = config->m_path.get();
  std::string password = std::string("");
  if (config->m_password != boost::none) password = config->m_password.get();

  auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(path, password);
  PyMoneroJsonRequest request("open_wallet", params);
  m_rpc->send_json_request(request);
  clear();

  if (config->m_connection_manager != boost::none) {
    if (config->m_server != boost::none) throw std::runtime_error("Wallet can be opened with a server or connection manager but not both");
    set_connection_manager(config->m_connection_manager.get());
  }
  else if (config->m_server != boost::none) {
    set_daemon_connection(config->m_server);
  }
  
  return this;
}

PyMoneroWalletRpc* PyMoneroWalletRpc::open_wallet(const std::string& name, const std::string& password) {
  auto config = std::make_shared<PyMoneroWalletConfig>();
  config->m_path = name;
  config->m_password = password;
  return open_wallet(config);
}

PyMoneroWalletRpc* PyMoneroWalletRpc::create_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config) {
  if (!config) throw std::runtime_error("Must specify config to create wallet");
  if (config->m_network_type != boost::none) throw std::runtime_error("Cannot specify network type when creating RPC wallet");
  if (config->m_seed != boost::none && (config->m_primary_address != boost::none || config->m_private_view_key != boost::none || config->m_private_spend_key != boost::none)) {
    throw std::runtime_error("Wallet can be initialized with a seed or keys but not both");
  }
  if (config->m_account_lookahead != boost::none || config->m_subaddress_lookahead != boost::none) throw std::runtime_error("monero-wallet-rpc does not support creating wallets with subaddress lookahead over rpc");
  if (config->m_connection_manager != boost::none) {
    if (config->m_server != boost::none) throw std::runtime_error("Wallet can be opened with a server or connection manager but not both");
    auto connection = config->m_connection_manager.get()->get_connection();
    if (connection) config->m_server = *connection;
  }

  if (config->m_seed != boost::none) create_wallet_from_seed(config);
  else if (config->m_private_spend_key != boost::none || config->m_primary_address != boost::none) create_wallet_from_keys(config);
  else create_wallet_random(config);

  if (config->m_connection_manager != boost::none) {
    set_connection_manager(config->m_connection_manager.get());
  }
  else if (config->m_server != boost::none) {
    set_daemon_connection(config->m_server);
  }

  return this;
}

std::vector<std::string> PyMoneroWalletRpc::get_seed_languages() const {
  PyMoneroJsonRequest request("get_languages");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  std::vector<std::string> languages;

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("languages")) {
      auto languages_node = it->second;

      for (auto it2 = languages_node.begin(); it2 != languages_node.end(); ++it2) {
        languages.push_back(it2->second.data());
      }
    }
  }

  return languages;
}

void PyMoneroWalletRpc::stop() {
  PyMoneroJsonRequest request("stop_wallet");
  m_rpc->send_json_request(request);
}

bool PyMoneroWalletRpc::is_view_only() const {
  try {
    std::string key = "mnemonic";
    query_key(key);
    return false;
  }
  catch (const PyMoneroRpcError& e) {
    if (e.code == -29) return true;
    if (e.code == -1) return false;
    throw;
  }
}

boost::optional<monero::monero_rpc_connection> PyMoneroWalletRpc::get_daemon_connection() const {
  if (m_daemon_connection == nullptr) return boost::none;
  return boost::optional<monero::monero_rpc_connection>(*m_daemon_connection);
}

void PyMoneroWalletRpc::set_daemon_connection(const boost::optional<monero_rpc_connection>& connection, bool is_trusted, const boost::optional<std::shared_ptr<PyMoneroSslOptions>> ssl_options) {
  auto params = std::make_shared<PyMoneroSetDaemonParams>();
  if (connection == boost::none) {
    params->m_address = "placeholder";
    params->m_username = "";
    params->m_password = "";
  }
  else { 
    params->m_address = connection->m_uri;
    params->m_username = connection->m_username;
    params->m_password = connection->m_password;
  }

  params->m_trusted = is_trusted;
  params->m_ssl_support = "autodetect";

  if (ssl_options != boost::none) {
    params->m_ssl_private_key_path = ssl_options.get()->m_ssl_private_key_path;
    params->m_ssl_certificate_path = ssl_options.get()->m_ssl_certificate_path;
    params->m_ssl_ca_file = ssl_options.get()->m_ssl_ca_file;
    params->m_ssl_allowed_fingerprints = ssl_options.get()->m_ssl_allowed_fingerprints;
    params->m_ssl_allow_any_cert = ssl_options.get()->m_ssl_allow_any_cert;
  }

  PyMoneroJsonRequest request("set_daemon", params);
  m_rpc->send_json_request(request);

  if (connection == boost::none || connection->m_uri == boost::none || connection->m_uri->empty()) {
    m_daemon_connection = nullptr;
  }
  else {
    m_daemon_connection = std::make_shared<PyMoneroRpcConnection>(connection.get());
  }
}

void PyMoneroWalletRpc::set_daemon_connection(const boost::optional<monero_rpc_connection>& connection) {
  set_daemon_connection(connection, false, boost::none);
}

bool PyMoneroWalletRpc::is_connected_to_daemon() const {
  try {
    check_reserve_proof(get_primary_address(), "", "");
    return false;
  }
  catch (const PyMoneroRpcError& e) {
    if (e.message == std::string("Failed to connect to daemon")) return false;
    return true;
  }
}

monero::monero_version PyMoneroWalletRpc::get_version() const { 
  PyMoneroJsonRequest request("get_version");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroVersion> info = std::make_shared<PyMoneroVersion>();
  PyMoneroVersion::from_property_tree(res, info);
  return *info;
}

std::string PyMoneroWalletRpc::get_path() const {
  return m_path;
}

std::string PyMoneroWalletRpc::get_seed() const {
  std::string key = "mnemonic";
  return query_key(key);
}

std::string PyMoneroWalletRpc::get_seed_language() const {
  throw std::runtime_error("MoneroWalletRpc::get_seed_language() not supported");
}

std::string PyMoneroWalletRpc::get_public_view_key() const {
  std::string key = "public_view_key";
  return query_key(key);
}

std::string PyMoneroWalletRpc::get_private_view_key() const {
  std::string key = "view_key";
  return query_key(key);
}

std::string PyMoneroWalletRpc::get_public_spend_key() const {
  std::string key = "public_spend_key";
  return query_key(key);
}

std::string PyMoneroWalletRpc::get_private_spend_key() const {
  std::string key = "spend_key";
  return query_key(key);
}

std::string PyMoneroWalletRpc::get_address(const uint32_t account_idx, const uint32_t subaddress_idx) const {
  auto it = m_address_cache.find(account_idx);
  std::vector<uint32_t> empty_indices;
  if (it == m_address_cache.end()) {
    get_subaddresses(account_idx, empty_indices, true);
    return get_address(account_idx, subaddress_idx);
  }
  
  auto subaddress_map = it->second;
  auto it2 = subaddress_map.find(subaddress_idx);

  if (it2 == subaddress_map.end()) {
    get_subaddresses(account_idx, empty_indices, true);
    return get_address(account_idx, subaddress_idx);
  }

  return it2->second.data();
}

monero_subaddress PyMoneroWalletRpc::get_address_index(const std::string& address) const {
  auto params = std::make_shared<PyMoneroGetAddressIndexParams>(address);
  PyMoneroJsonRequest request("get_address_index", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  auto tmplt = std::make_shared<monero::monero_subaddress>();
  PyMoneroSubaddress::from_property_tree(res, tmplt);
  return *tmplt;
}

monero_integrated_address PyMoneroWalletRpc::get_integrated_address(const std::string& standard_address, const std::string& payment_id) const {
  auto params = std::make_shared<PyMoneroMakeIntegratedAddressParams>(standard_address, payment_id);
  PyMoneroJsonRequest request("make_integrated_address", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  auto tmplt = std::make_shared<monero::monero_integrated_address>();
  PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
  return decode_integrated_address(tmplt->m_integrated_address);
}

monero_integrated_address PyMoneroWalletRpc::decode_integrated_address(const std::string& integrated_address) const {
  auto params = std::make_shared<PyMoneroSplitIntegratedAddressParams>(integrated_address);
  PyMoneroJsonRequest request("split_integrated_address", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto tmplt = std::make_shared<monero::monero_integrated_address>();
  PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
  tmplt->m_integrated_address = integrated_address;
  return *tmplt;
}

uint64_t PyMoneroWalletRpc::get_height() const {
  PyMoneroJsonRequest request("get_height");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroWalletGetHeightResponse::from_property_tree(res);
}

uint64_t PyMoneroWalletRpc::get_daemon_height() const {
  throw std::runtime_error("monero-wallet-rpc does not support getting the chain height");
}

uint64_t PyMoneroWalletRpc::get_height_by_date(uint16_t year, uint8_t month, uint8_t day) const {
  throw std::runtime_error("monero-wallet-rpc does not support getting a height by date");
}

monero_sync_result PyMoneroWalletRpc::sync() {
  auto params = std::make_shared<PyMoneroRefreshWalletParams>();
  boost::lock_guard<boost::recursive_mutex> lock(m_sync_mutex);
  PyMoneroJsonRequest request("refresh", params);
  poll();
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  monero_sync_result sync_result(0, false);

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("blocks_fetched")) sync_result.m_num_blocks_fetched = it->second.get_value<uint64_t>();
    else if (key == std::string("received_money")) sync_result.m_received_money = it->second.get_value<bool>();
  }

  return sync_result;
}

monero_sync_result PyMoneroWalletRpc::sync(monero_wallet_listener& listener) {
  throw std::runtime_error("Monero Wallet RPC does not support reporting sync progress");
}

monero_sync_result PyMoneroWalletRpc::sync(uint64_t start_height, monero_wallet_listener& listener) {
  throw std::runtime_error("Monero Wallet RPC does not support reporting sync progress");
}

monero_sync_result PyMoneroWalletRpc::sync(uint64_t start_height) {
  auto params = std::make_shared<PyMoneroRefreshWalletParams>(start_height);
  boost::lock_guard<boost::recursive_mutex> lock(m_sync_mutex);
  PyMoneroJsonRequest request("refresh", params);
  auto response = m_rpc->send_json_request(request);
  poll();
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  monero_sync_result sync_result(0, false);

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("blocks_fetched")) sync_result.m_num_blocks_fetched = it->second.get_value<uint64_t>();
    else if (key == std::string("received_money")) sync_result.m_received_money = it->second.get_value<bool>();
  }

  return sync_result;
}

void PyMoneroWalletRpc::start_syncing(uint64_t sync_period_in_ms) {
  // convert ms to seconds for rpc parameter
  uint64_t sync_period_in_seconds = sync_period_in_ms / 1000;
  
  // send rpc request
  auto params = std::make_shared<PyMoneroRefreshWalletParams>(true, sync_period_in_seconds);
  PyMoneroJsonRequest request("auto_refresh", params);
  auto response = m_rpc->send_json_request(request);
  
  // update sync period for poller
  m_sync_period_in_ms = sync_period_in_seconds * 1000;
  if (m_poller != nullptr) m_poller->set_period_in_ms(m_sync_period_in_ms.get());
  
  // poll if listening
  poll();
}

void PyMoneroWalletRpc::stop_syncing() {
  auto params = std::make_shared<PyMoneroAutoRefreshParams>(false);
  PyMoneroJsonRequest request("auto_refresh", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::scan_txs(const std::vector<std::string>& tx_hashes) {
  if (tx_hashes.empty()) throw std::runtime_error("No tx hashes given to scan");
  auto params = std::make_shared<PyMoneroScanTxParams>(tx_hashes);
  PyMoneroJsonRequest request("scan_tx", params);
  m_rpc->send_json_request(request);
  poll();
}

void PyMoneroWalletRpc::rescan_spent() {
  PyMoneroJsonRequest request("rescan_spent");
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::rescan_blockchain() {
  PyMoneroJsonRequest request("rescan_blockchain");
  m_rpc->send_json_request(request);
}

uint64_t PyMoneroWalletRpc::get_balance() const {
  auto wallet_balance = get_balances(boost::none, boost::none);
  return wallet_balance->m_balance;
}

uint64_t PyMoneroWalletRpc::get_balance(uint32_t account_index) const {
  auto wallet_balance = get_balances(account_index, boost::none);
  return wallet_balance->m_balance;
}

uint64_t PyMoneroWalletRpc::get_balance(uint32_t account_idx, uint32_t subaddress_idx) const {
  auto wallet_balance = get_balances(account_idx, subaddress_idx);
  return wallet_balance->m_balance;
}

uint64_t PyMoneroWalletRpc::get_unlocked_balance() const {
  auto wallet_balance = get_balances(boost::none, boost::none);
  return wallet_balance->m_unlocked_balance;
}

uint64_t PyMoneroWalletRpc::get_unlocked_balance(uint32_t account_index) const {
  auto wallet_balance = get_balances(account_index, boost::none);
  return wallet_balance->m_unlocked_balance;
}

uint64_t PyMoneroWalletRpc::get_unlocked_balance(uint32_t account_idx, uint32_t subaddress_idx) const {
  auto wallet_balance = get_balances(account_idx, subaddress_idx);
  return wallet_balance->m_unlocked_balance;
}

std::vector<monero_account> PyMoneroWalletRpc::get_accounts(bool include_subaddresses, const std::string& tag, bool skip_balances) const {
  auto params = std::make_shared<PyMoneroGetAccountsParams>(tag);
  PyMoneroJsonRequest request("get_accounts", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  std::vector<monero_account> accounts;
  PyMoneroAccount::from_property_tree(node, accounts);

  if (include_subaddresses) {

    for (auto &account : accounts) {
      std::vector<uint32_t> empty_indices;
      account.m_subaddresses = get_subaddresses(account.m_index.get(), empty_indices, true);

      if (!skip_balances) {
        for (auto &subaddress : account.m_subaddresses) {
          subaddress.m_balance = 0;
          subaddress.m_unlocked_balance = 0;
          subaddress.m_num_unspent_outputs = 0;
          subaddress.m_num_blocks_to_unlock = 0;
        }
      }
    }

    if (!skip_balances) {
      auto params2 = std::make_shared<PyMoneroGetBalanceParams>(true);
      PyMoneroJsonRequest request2("get_balance", params2);
      auto response2 = m_rpc->send_json_request(request2);
      if (response2->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
      auto node2 = response2->m_result.get();
      auto bal_res = std::make_shared<PyMoneroGetBalanceResponse>();
      PyMoneroGetBalanceResponse::from_property_tree(node2, bal_res);

      for (const auto &subaddress : bal_res->m_per_subaddress) {
        // merge info
        auto account = &accounts[subaddress->m_account_index.get()];
        if (account->m_index != subaddress->m_account_index) throw std::runtime_error("RPC accounts are out of order"); 
        auto tgt_subaddress = &account->m_subaddresses[subaddress->m_account_index.get()];
        if (tgt_subaddress->m_index != subaddress->m_index) throw std::runtime_error("RPC subaddresses are out of order");

        if (subaddress->m_balance != boost::none) tgt_subaddress->m_balance = subaddress->m_balance;
        if (subaddress->m_unlocked_balance != boost::none) tgt_subaddress->m_unlocked_balance = subaddress->m_unlocked_balance;
        if (subaddress->m_num_unspent_outputs != boost::none) tgt_subaddress->m_num_unspent_outputs = subaddress->m_num_unspent_outputs;
        if (subaddress->m_num_blocks_to_unlock != boost::none) tgt_subaddress->m_num_blocks_to_unlock = subaddress->m_num_blocks_to_unlock;
      }
    }
  }

  return accounts;
}

monero_account PyMoneroWalletRpc::create_account(const std::string& label) {
  auto params = std::make_shared<PyMoneroCreateAccountParams>(label);
  PyMoneroJsonRequest request("create_account", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  monero_account res;
  bool found_index = false;
  bool address_found = false;
  
  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("account_index")) {
      found_index = true;
      res.m_index = it->second.get_value<uint32_t>();
    }
    else if (key == std::string("address")) {
      address_found = true;
      res.m_primary_address = it->second.data();
    }
  }

  if (!found_index || !address_found) throw std::runtime_error("Could not create account");

  return res;
}

std::vector<monero_subaddress> PyMoneroWalletRpc::get_subaddresses(const uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices, bool skip_balances) const {
  // fetch subaddresses
  auto params = std::make_shared<PyMoneroGetAddressParams>(account_idx, subaddress_indices);
  PyMoneroJsonRequest request("get_address", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  std::vector<monero_subaddress> subaddresses;

  // initialize subaddressesb
  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("addresses")) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it != node2.end(); ++it2) {
        auto subaddress = std::make_shared<monero::monero_subaddress>();
        PyMoneroSubaddress::from_rpc_property_tree(node2, subaddress);
        subaddress->m_account_index = account_idx;
        subaddresses.push_back(*subaddress);
      }
    }

  }
  
  // fetch and initialize subaddress balances
  if (!skip_balances) {
    
    // these fields are not initialized if subaddress is unused and therefore not returned from `get_balance`
    for (auto &subaddress : subaddresses) {
      subaddress.m_balance = 0;
      subaddress.m_unlocked_balance = 0;
      subaddress.m_num_unspent_outputs = 0;
      subaddress.m_num_blocks_to_unlock = 0;
    }

    // fetch and initialize balances
    PyMoneroJsonRequest request2("get_balance", params);
    auto response2 = m_rpc->send_json_request(request);
    if (response2->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node2 = response2->m_result.get();

    std::vector<std::shared_ptr<monero::monero_subaddress>> subaddresses2;
    PyMoneroSubaddress::from_rpc_property_tree(node2, subaddresses2);

    for (auto &tgt_subaddress: subaddresses) {
      for (const auto &rpc_subaddress : subaddresses2) {
        if (rpc_subaddress->m_index != tgt_subaddress.m_index) continue;

        if (rpc_subaddress->m_balance != boost::none) tgt_subaddress.m_balance = rpc_subaddress->m_balance;
        if (rpc_subaddress->m_unlocked_balance != boost::none) tgt_subaddress.m_unlocked_balance = rpc_subaddress->m_unlocked_balance;
        if (rpc_subaddress->m_num_unspent_outputs != boost::none) tgt_subaddress.m_num_unspent_outputs = rpc_subaddress->m_num_unspent_outputs;
        if (rpc_subaddress->m_num_blocks_to_unlock != boost::none) tgt_subaddress.m_num_blocks_to_unlock = rpc_subaddress->m_num_blocks_to_unlock;
      }
    }
  }
  
  // cache addresses
  /*
  Map<Integer, String> subaddressMap = addressCache.get(accountIdx);
  if (subaddressMap == null) {
    subaddressMap = new HashMap<Integer, String>();
    addressCache.put(accountIdx, subaddressMap);
  }

  for (const auto &subaddress : subaddresses) {
    subaddressMap.put(subaddress.getIndex(), subaddress.getAddress());
  }
  */
  // return results
  return subaddresses;
}

std::vector<monero_subaddress> PyMoneroWalletRpc::get_subaddresses(uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) const {
  return get_subaddresses(account_idx, subaddress_indices, false);
}

std::vector<monero_subaddress> PyMoneroWalletRpc::get_subaddresses(const uint32_t account_idx) const {
  std::vector<uint32_t> subaddress_indices;
  return get_subaddresses(account_idx, subaddress_indices);
}

monero_subaddress PyMoneroWalletRpc::get_subaddress(const uint32_t account_idx, const uint32_t subaddress_idx) const {
  std::vector<uint32_t> subaddress_indices;
  subaddress_indices.push_back(subaddress_idx);
  auto subaddresses = get_subaddresses(account_idx, subaddress_indices);
  if (subaddresses.empty()) throw std::runtime_error("Subaddress is not initialized");
  if (subaddresses.size() != 1) throw std::runtime_error("Only 1 subaddress should be returned");
  return subaddresses[0];
}

monero_subaddress PyMoneroWalletRpc::create_subaddress(uint32_t account_idx, const std::string& label) {
  auto params = std::make_shared<PyMoneroCreateSubaddressParams>(account_idx, label);
  PyMoneroJsonRequest request("create_address", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  monero_subaddress sub;
  sub.m_account_index = account_idx;
  sub.m_label = label;
  sub.m_balance = 0;
  sub.m_unlocked_balance = 0;
  sub.m_num_unspent_outputs = 0;
  sub.m_is_used = false;
  sub.m_num_blocks_to_unlock = 0;

  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("address_index")) sub.m_index = it->second.get_value<uint32_t>();
    else if (key == std::string("address")) sub.m_address = it->second.data();
  }

  return sub;
}

void PyMoneroWalletRpc::set_subaddress_label(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
  auto params = std::make_shared<PyMoneroSetSubaddressLabelParams>(account_idx, subaddress_idx, label);
  PyMoneroJsonRequest request("label_address", params);
  m_rpc->send_json_request(request);
}

std::string PyMoneroWalletRpc::export_outputs(bool all) const {
  auto params = std::make_shared<PyMoneroImportExportOutputsParams>(all);
  PyMoneroJsonRequest request("export_outputs", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("outputs_data_hex")) return it->second.data();
  }

  throw std::runtime_error("Could not get outputs hex");
}

int PyMoneroWalletRpc::import_outputs(const std::string& outputs_hex) {
  auto params = std::make_shared<PyMoneroImportExportOutputsParams>(outputs_hex);
  PyMoneroJsonRequest request("import_outputs", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("num_imported")) return it->second.get_value<int>();
  }

  return 0;
}

std::vector<std::shared_ptr<monero_key_image>> PyMoneroWalletRpc::export_key_images(bool all) const {
  auto params = std::make_shared<PyMoneroImportExportKeyImagesParams>(all);
  PyMoneroJsonRequest request("export_key_images", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  std::vector<std::shared_ptr<monero::monero_key_image>> key_images;
  PyMoneroKeyImage::from_property_tree(node, key_images);
  return key_images;
}

std::shared_ptr<monero_key_image_import_result> PyMoneroWalletRpc::import_key_images(const std::vector<std::shared_ptr<monero_key_image>>& key_images) {
  auto params = std::make_shared<PyMoneroImportExportKeyImagesParams>(key_images);
  PyMoneroJsonRequest request("import_key_images", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto import_result = std::make_shared<monero_key_image_import_result>();
  PyMoneroKeyImageImportResult::from_property_tree(node, import_result);
  return import_result;
}

std::vector<std::shared_ptr<monero_key_image>> PyMoneroWalletRpc::get_new_key_images_from_last_import() {
  throw std::runtime_error("get_new_key_images_from_last_import(): not implemented");
}

void PyMoneroWalletRpc::freeze_output(const std::string& key_image) {
  auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
  PyMoneroJsonRequest request("freeze", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::thaw_output(const std::string& key_image) {
  auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
  PyMoneroJsonRequest request("thaw", params);
  m_rpc->send_json_request(request);
}

bool PyMoneroWalletRpc::is_output_frozen(const std::string& key_image) {
  auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
  PyMoneroJsonRequest request("frozen", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("frozen")) return it->second.get_value<bool>();
  }

  throw std::runtime_error("Could not get output");
}

monero_tx_priority PyMoneroWalletRpc::get_default_fee_priority() const {
  PyMoneroJsonRequest request("get_default_fee_priority");
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("priority")) {
      int priority = it->second.get_value<int>();

      if (priority == 0) return monero_tx_priority::DEFAULT;
      else if (priority == 1) return monero_tx_priority::UNIMPORTANT;
      else if (priority == 2) return monero_tx_priority::NORMAL; 
      else if (priority == 3) return monero_tx_priority::ELEVATED; 
    }
  }

  throw std::runtime_error("Could not get default fee priority");
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::create_txs(const monero_tx_config& conf) {
  // validate, copy, and normalize request
  monero_tx_config config = conf;
  if (config.m_destinations.empty()) throw std::runtime_error("Destinations cannot be empty");
  if (config.m_sweep_each_subaddress != boost::none) throw std::runtime_error("Sweep each subaddress not supported");
  if (config.m_below_amount != boost::none) throw std::runtime_error("Below amount not supported");
  
  if (config.m_can_split == boost::none) {
    config = config.copy();
    config.m_can_split = true;
  }
  if (config.m_relay == true && is_multisig()) throw std::runtime_error("Cannot relay multisig transaction until co-signed");
  
  // determine account and subaddresses to send from
  if (config.m_account_index == boost::none) throw std::runtime_error("Must specify the account index to send from");
  auto account_idx = config.m_account_index.get();

  // cannot apply subtractFeeFrom with `transfer_split` call
  if (config.m_can_split && config.m_subtract_fee_from.size() > 0) {
    throw std::runtime_error("subtractfeefrom transfers cannot be split over multiple transactions yet");
  }

  // build request parameters
  auto params = std::make_shared<PyMoneroTransferParams>(config);
  std::string request_path = "transfer";
  if (config.m_can_split) request_path = "transfer_split";

  PyMoneroJsonRequest request(request_path, params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  // pre-initialize txs iff present. multisig and view-only wallets will have tx set without transactions
  std::vector<std::shared_ptr<monero_tx_wallet>> txs;
  int num_txs = 0;
  
  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (config.m_can_split && key == std::string("fee_list")) {
      auto fee_list_node = it->second;

      for(auto it2 = fee_list_node.begin(); it2 != fee_list_node.end(); ++it2) {
        num_txs++;
      }
    }
  }
      
  bool copy_destinations = num_txs == 1;
  for (int i = 0; i < num_txs; i++) {
    auto tx = std::make_shared<monero::monero_tx_wallet>();
    PyMoneroTxWallet::init_sent(config, tx, copy_destinations);
    tx->m_outgoing_transfer.get()->m_account_index = account_idx;

    if (config.m_subaddress_indices.size() == 1) {
      tx->m_outgoing_transfer.get()->m_subaddress_indices = config.m_subaddress_indices;
    }

    txs.push_back(tx);
  }
  
  // notify of changes
  if (config.m_relay) poll();
  
  // initialize tx set from rpc response with pre-initialized txs
  auto tx_set = std::make_shared<monero::monero_tx_set>();
  if (config.m_can_split) {
    PyMoneroTxSet::from_sent_txs(node, tx_set, txs, config);
  }
  else {
    if (txs.empty()) {
      auto __tx = std::make_shared<monero::monero_tx_wallet>();
      PyMoneroTxSet::from_tx(node, tx_set, __tx, true, config);
    }
    else {
      PyMoneroTxSet::from_tx(node, tx_set, txs[0], true, config);
    }
  }

  return tx_set->m_txs;
}

std::shared_ptr<monero_tx_wallet> PyMoneroWalletRpc::sweep_output(const monero_tx_config& config) {
  auto params = std::make_shared<PyMoneroSweepParams>(config);
  PyMoneroJsonRequest request("sweep_single", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  if (config.m_relay) poll();
  auto set = std::make_shared<monero_tx_set>();
  auto tx = std::make_shared<monero::monero_tx_wallet>();
  PyMoneroTxWallet::init_sent(config, tx, true);
  PyMoneroTxSet::from_tx(node, set, tx, true, config);
  return tx;
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::sweep_dust(bool relay) {
  auto params = std::make_shared<PyMoneroSweepParams>(relay);
  PyMoneroJsonRequest request("sweep_dust", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_sent_txs(node, set);
  return set->m_txs;
}

std::vector<std::string> PyMoneroWalletRpc::relay_txs(const std::vector<std::string>& tx_metadatas) {
  if (tx_metadatas.empty()) throw std::runtime_error("Must provide an array of tx metadata to relay");

  std::vector<std::string> tx_hashes;

  for (const auto &tx_metadata : tx_metadatas) {
    auto params = std::make_shared<PyMoneroWalletRelayTxParams>(tx_metadata);
    PyMoneroJsonRequest request("relay_tx", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tx_hash")) tx_hashes.push_back(it->second.data());
    }
  }

  return tx_hashes;
}

monero_tx_set PyMoneroWalletRpc::describe_tx_set(const monero_tx_set& tx_set) {
  auto params = std::make_shared<PyMoneroSignDescribeTransferParams>();
  params->m_multisig_txset = tx_set.m_multisig_tx_hex;
  params->m_unsigned_txset = tx_set.m_unsigned_tx_hex;
  PyMoneroJsonRequest request("describe_transfer", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_describe_transfer(node, set);
  return *set;
}

monero_tx_set PyMoneroWalletRpc::sign_txs(const std::string& unsigned_tx_hex) {
  auto params = std::make_shared<PyMoneroSignDescribeTransferParams>(unsigned_tx_hex);
  PyMoneroJsonRequest request("sign_transfer", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_sent_txs(node, set);
  return *set;
}

std::vector<std::string> PyMoneroWalletRpc::submit_txs(const std::string& signed_tx_hex) {
  auto params = std::make_shared<PyMoneroSubmitTransferParams>(signed_tx_hex);
  PyMoneroJsonRequest request("submit_transfer", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  poll();
  std::vector<std::string> hashes;

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("tx_hash_list")) {
      auto hashes_node = it->second;

      for (auto it2 = hashes_node.begin(); it2 != hashes_node.end(); ++it2) {
        hashes.push_back(it2->second.data());
      }
    }
  }

  return hashes;
}

std::string PyMoneroWalletRpc::sign_message(const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx, uint32_t subaddress_idx) const {
  auto params = std::make_shared<PyMoneroVerifySignMessageParams>(msg, signature_type, account_idx, subaddress_idx);
  PyMoneroJsonRequest request("sign", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

monero_message_signature_result PyMoneroWalletRpc::verify_message(const std::string& msg, const std::string& address, const std::string& signature) const {
  auto params = std::make_shared<PyMoneroVerifySignMessageParams>(msg, address, signature);
  PyMoneroJsonRequest request("verify", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto sig_result = std::make_shared<monero_message_signature_result>();
  PyMoneroMessageSignatureResult::from_property_tree(node, sig_result);
  return *sig_result;
}

std::string PyMoneroWalletRpc::get_tx_key(const std::string& tx_hash) const {
  auto params = std::make_shared<PyMoneroCheckTxKeyParams>(tx_hash);
  PyMoneroJsonRequest request("get_tx_key", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("tx_key")) {
      return it->second.data();
    }
  }

  throw std::runtime_error("Could not get tx key");
}

std::shared_ptr<monero_check_tx> PyMoneroWalletRpc::check_tx_key(const std::string& tx_hash, const std::string& tx_key, const std::string& address) const {
  auto params = std::make_shared<PyMoneroCheckTxKeyParams>(tx_hash, tx_key, address);
  PyMoneroJsonRequest request("check_tx_key", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto check = std::make_shared<monero::monero_check_tx>();
  PyMoneroCheckTxProof::from_property_tree(node, check);
  return check;
}

std::string PyMoneroWalletRpc::get_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
  params->m_address = address;
  PyMoneroJsonRequest request("get_tx_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

std::shared_ptr<monero_check_tx> PyMoneroWalletRpc::check_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, address, message, signature);
  PyMoneroJsonRequest request("check_tx_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto check = std::make_shared<monero::monero_check_tx>();
  PyMoneroCheckTxProof::from_property_tree(node, check);
  return check;
}

std::string PyMoneroWalletRpc::get_spend_proof(const std::string& tx_hash, const std::string& message) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
  PyMoneroJsonRequest request("get_spend_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

bool PyMoneroWalletRpc::check_spend_proof(const std::string& tx_hash, const std::string& message, const std::string& signature) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message, signature);
  PyMoneroJsonRequest request("check_spend_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto proof = std::make_shared<monero::monero_check_reserve>();
  PyMoneroCheckReserve::from_property_tree(node, proof);
  return proof->m_is_good;
}

std::string PyMoneroWalletRpc::get_reserve_proof_wallet(const std::string& message) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(message);
  PyMoneroJsonRequest request("get_reserve_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

std::string PyMoneroWalletRpc::get_reserve_proof_account(uint32_t account_idx, uint64_t amount, const std::string& message) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(account_idx, amount, message);
  PyMoneroJsonRequest request("get_reserve_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

std::shared_ptr<monero_check_reserve> PyMoneroWalletRpc::check_reserve_proof(const std::string& address, const std::string& message, const std::string& signature) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(address, message, signature);
  PyMoneroJsonRequest request("check_reserve_proof", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  auto proof = std::make_shared<monero::monero_check_reserve>();
  PyMoneroCheckReserve::from_property_tree(node, proof);
  return proof;
}

std::vector<std::string> PyMoneroWalletRpc::get_tx_notes(const std::vector<std::string>& tx_hashes) const {
  auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes);
  PyMoneroJsonRequest request("get_tx_notes", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  std::vector<std::string> notes;

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("notes")) {
      auto notes_node = it->second;

      for (auto it2 = notes_node.begin(); it2 != notes_node.end(); ++it2) {
        notes.push_back(it2->second.data());
      }
    }
  }

  return notes;
}

void PyMoneroWalletRpc::set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
  auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes, notes);
  PyMoneroJsonRequest request("set_tx_notes", params);
  m_rpc->send_json_request(request);
}

std::vector<monero_address_book_entry> PyMoneroWalletRpc::get_address_book_entries(const std::vector<uint64_t>& indices) const {
  auto params = std::make_shared<PyMoneroAddressBookEntryParams>(indices);
  PyMoneroJsonRequest request("get_address_book", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  std::vector<std::shared_ptr<monero_address_book_entry>> entries_ptr;
  PyMoneroAddressBookEntry::from_property_tree(node, entries_ptr);
  std::vector<monero_address_book_entry> entries;

  for (const auto &entry : entries_ptr) {
    entries.push_back(*entry);
  }

  return entries;
}

uint64_t PyMoneroWalletRpc::add_address_book_entry(const std::string& address, const std::string& description) {
  auto params = std::make_shared<PyMoneroAddressBookEntryParams>(address, description);
  PyMoneroJsonRequest request("add_address_book", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("index")) {
      return it->second.get_value<uint64_t>();
    }
  }

  throw std::runtime_error("Invalid response from wallet rpc");
}

void PyMoneroWalletRpc::edit_address_book_entry(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
  auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index, set_address, address, set_description, description);
  PyMoneroJsonRequest request("edit_address_book", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::delete_address_book_entry(uint64_t index) {
  auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index);
  PyMoneroJsonRequest request("delete_address_book", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) {
  auto params = std::make_shared<PyMoneroTagAccountsParams>(tag, account_indices);
  PyMoneroJsonRequest request("tag_accounts", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::untag_accounts(const std::vector<uint32_t>& account_indices) {
  auto params = std::make_shared<PyMoneroTagAccountsParams>(account_indices);
  PyMoneroJsonRequest request("untag_accounts", params);
  m_rpc->send_json_request(request);
}

std::vector<std::shared_ptr<PyMoneroAccountTag>> PyMoneroWalletRpc::get_account_tags() {
  PyMoneroJsonRequest request("get_account_tags");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  std::vector<std::shared_ptr<PyMoneroAccountTag>> account_tags;
  PyMoneroAccountTag::from_property_tree(res, account_tags);
  return account_tags;
}

void PyMoneroWalletRpc::set_account_tag_label(const std::string& tag, const std::string& label) {
  auto params = std::make_shared<PyMoneroSetAccountTagDescriptionParams>(tag, label);
  PyMoneroJsonRequest request("set_account_tag_description", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::set_account_label(uint32_t account_index, const std::string& label) {
  set_subaddress_label(account_index, 0, label);
}

std::string PyMoneroWalletRpc::get_payment_uri(const monero_tx_config& config) const {
  auto params = std::make_shared<PyMoneroGetPaymentUriParams>(config);
  PyMoneroJsonRequest request("make_uri", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroGetPaymentUriResponse::from_property_tree(res);
}

std::shared_ptr<monero_tx_config> PyMoneroWalletRpc::parse_payment_uri(const std::string& uri) const {
  auto params = std::make_shared<PyMoneroParsePaymentUriParams>(uri);
  PyMoneroJsonRequest request("parse_uri", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto uri_response = std::make_shared<PyMoneroParsePaymentUriResponse>();
  PyMoneroParsePaymentUriResponse::from_property_tree(res, uri_response);
  return uri_response->to_tx_config();
}

void PyMoneroWalletRpc::set_attribute(const std::string& key, const std::string& val) {
  auto params = std::make_shared<PyMoneroWalletAttributeParams>(key, val);
  PyMoneroJsonRequest request("set_attribute", params);
  m_rpc->send_json_request(request);
}

bool PyMoneroWalletRpc::get_attribute(const std::string& key, std::string& value) const {
  try {
    auto params = std::make_shared<PyMoneroWalletAttributeParams>(key);
    PyMoneroJsonRequest request("get_attribute", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    PyMoneroWalletAttributeParams::from_property_tree(res, params);
    if (params->m_value == boost::none) return false;
    value = params->m_value.get();
    return true;
  }
  catch (...) {
    return false;
  }
}

void PyMoneroWalletRpc::start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) {
  auto params = std::make_shared<PyMoneroWalletStartMiningParams>(num_threads.value_or(0), background_mining.value_or(false), ignore_battery.value_or(false));
  PyMoneroJsonRequest request("start_mining", params);
  auto response = m_rpc->send_json_request(request);
  PyMoneroDaemonRpc::check_response_status(response);
}

void PyMoneroWalletRpc::stop_mining() {
  PyMoneroJsonRequest request("stop_mining");
  m_rpc->send_json_request(request);
}

bool PyMoneroWalletRpc::is_multisig_import_needed() const {
  PyMoneroJsonRequest request("get_balance");
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto balance = std::make_shared<PyMoneroGetBalanceResponse>();
  PyMoneroGetBalanceResponse::from_property_tree(res, balance);
  if (balance->m_multisig_import_needed) return true;
  return false;
}

monero_multisig_info PyMoneroWalletRpc::get_multisig_info() const {
  PyMoneroJsonRequest request("is_multisig");
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto info = std::make_shared<monero::monero_multisig_info>();
  PyMoneroMultisigInfo::from_property_tree(res, info);
  return *info;
}

std::string PyMoneroWalletRpc::prepare_multisig() {
  auto params = std::make_shared<PyMoneroPrepareMultisigParams>();
  PyMoneroJsonRequest request("prepare_multisig", params);
  auto response = m_rpc->send_json_request(request);
  clear_address_cache();
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
}

std::string PyMoneroWalletRpc::make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) {
  auto params = std::make_shared<PyMoneroMakeMultisigParams>(multisig_hexes, threshold, password);
  PyMoneroJsonRequest request("make_multisig", params);
  auto response = m_rpc->send_json_request(request);
  clear_address_cache();
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
}

monero_multisig_init_result PyMoneroWalletRpc::exchange_multisig_keys(const std::vector<std::string>& multisig_hexes, const std::string& password) {
  auto params = std::make_shared<PyMoneroExchangeMultisigKeysParams>(multisig_hexes, password);
  PyMoneroJsonRequest request("exchange_multisig_keys", params);
  auto response = m_rpc->send_json_request(request);
  clear_address_cache();
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto multisig_init = std::make_shared<monero_multisig_init_result>();
  PyMoneroMultisigInitResult::from_property_tree(res, multisig_init);
  return *multisig_init;
}

std::string PyMoneroWalletRpc::export_multisig_hex() {
  PyMoneroJsonRequest request("export_multisig_info");
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroExportMultisigHexResponse::from_property_tree(res);
}

int PyMoneroWalletRpc::import_multisig_hex(const std::vector<std::string>& multisig_hexes) {
  auto params = std::make_shared<PyMoneroImportMultisigHexParams>(multisig_hexes);
  PyMoneroJsonRequest request("import_multisig_info", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroImportMultisigHexResponse::from_property_tree(res);
}

monero_multisig_sign_result PyMoneroWalletRpc::sign_multisig_tx_hex(const std::string& multisig_tx_hex) {
  auto params = std::make_shared<PyMoneroMultisigTxDataParams>(multisig_tx_hex);
  PyMoneroJsonRequest request("sign_multisig", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto multisig_result = std::make_shared<monero::monero_multisig_sign_result>();
  PyMoneroMultisigSignResult::from_property_tree(res, multisig_result);
  return *multisig_result;
}

std::vector<std::string> PyMoneroWalletRpc::submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex) {
  auto params = std::make_shared<PyMoneroMultisigTxDataParams>(signed_multisig_tx_hex);
  PyMoneroJsonRequest request("submit_multisig", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  return PyMoneroSubmitMultisigTxHexResponse::from_property_tree(res);
}

void PyMoneroWalletRpc::change_password(const std::string& old_password, const std::string& new_password) {
  auto params = std::make_shared<PyMoneroChangeWalletPasswordParams>(old_password, new_password);
  PyMoneroJsonRequest request("change_wallet_password", params);
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::save() {
  PyMoneroJsonRequest request("store");
  m_rpc->send_json_request(request);
}

void PyMoneroWalletRpc::close(bool save) {
  auto params = std::make_shared<PyMoneroCloseWalletParams>(save);
  PyMoneroJsonRequest request("close_wallet", params);
  m_rpc->send_json_request(request);
}

std::shared_ptr<PyMoneroWalletBalance> PyMoneroWalletRpc::get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const {
  auto balance = std::make_shared<PyMoneroWalletBalance>();

  if (account_idx == boost::none) {
    if (subaddress_idx != boost::none) throw std::runtime_error("Must provide account index with subaddress index");
  
    auto accounts = monero::monero_wallet::get_accounts();

    for(const auto &account : accounts) {
      balance->m_balance += account.m_balance.get();
      balance->m_unlocked_balance += account.m_unlocked_balance.get();
    }

    return balance;
  }
  else {
    auto params = std::make_shared<PyMoneroGetBalanceParams>(account_idx.get(), subaddress_idx);
    PyMoneroJsonRequest request("get_balance", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto bal_res = std::make_shared<PyMoneroGetBalanceResponse>();
    PyMoneroGetBalanceResponse::from_property_tree(res, bal_res);

    if (subaddress_idx == boost::none) {
      balance->m_balance = bal_res->m_balance.get();
      balance->m_unlocked_balance = bal_res->m_unlocked_balance.get();
      return balance;
    }
    else if (bal_res->m_per_subaddress.size() > 0) {
      auto sub = bal_res->m_per_subaddress[0];
      balance->m_balance = sub->m_balance.get();
      balance->m_unlocked_balance = sub->m_unlocked_balance.get();
    }
  }

  return balance;
}

PyMoneroWalletRpc* PyMoneroWalletRpc::create_wallet_random(const std::shared_ptr<PyMoneroWalletConfig> &conf) {
  // validate and normalize config
  auto config = conf->copy();
  if (config.m_seed_offset != boost::none) throw std::runtime_error("Cannot specify seed offset when creating random wallet");
  if (config.m_restore_height != boost::none) throw std::runtime_error("Cannot specify restore height when creating random wallet");
  if (config.m_save_current != boost::none && config.m_save_current == false) throw std::runtime_error("Current wallet is saved automatically when creating random wallet");
  if (config.m_path == boost::none || config.m_path->empty()) throw std::runtime_error("Wallet name is not initialized");
  if (config.m_language == boost::none || config.m_language->empty()) config.m_language = "English";

  // send request
  std::string filename = config.m_path.get();
  std::string password = config.m_password.get();
  std::string language = config.m_language.get();

  auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(filename, password, language);
  PyMoneroJsonRequest request("create_wallet", params);
  m_rpc->send_json_request(request);
  clear();
  m_path = config.m_path.get();
  return this;
}

PyMoneroWalletRpc* PyMoneroWalletRpc::create_wallet_from_seed(const std::shared_ptr<PyMoneroWalletConfig> &conf) {
  auto config = conf->copy();
  if (config.m_language == boost::none || config.m_language->empty()) config.m_language = "English";
  auto filename = config.m_path;
  auto password = config.m_password;
  auto seed = config.m_seed;
  auto seed_offset = config.m_seed_offset;
  auto restore_height = config.m_restore_height;
  auto language = config.m_language;
  bool autosave_current = false;
  bool enable_multisig_experimental = false;
  if (config.m_save_current != boost::none) autosave_current = config.m_save_current.get();
  if (config.m_is_multisig != boost::none) enable_multisig_experimental = config.m_is_multisig.get();
  auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(filename, password, seed, seed_offset, restore_height, language, autosave_current, enable_multisig_experimental);
  PyMoneroJsonRequest request("restore_deterministic_wallet", params);
  m_rpc->send_json_request(request);
  clear();
  m_path = config.m_path.get();
  return this;
}

PyMoneroWalletRpc* PyMoneroWalletRpc::create_wallet_from_keys(const std::shared_ptr<PyMoneroWalletConfig> &config) {
  if (config->m_seed_offset != boost::none) throw std::runtime_error("Cannot specify seed offset when creating wallet from keys");
  if (config->m_restore_height == boost::none) config->m_restore_height = 0;
  std::string filename = config->m_path.get();
  std::string password = config->m_password.get();
  std::string address = config->m_primary_address.get();
  std::string view_key = "";
  std::string spend_key = "";
  if (config->m_private_view_key != boost::none) view_key = config->m_private_view_key.get();
  if (config->m_private_spend_key != boost::none) spend_key = config->m_private_spend_key.get();
  uint64_t restore_height = config->m_restore_height.get();
  bool autosave_current = false;
  if (config->m_save_current != boost::none) autosave_current = config->m_save_current.get();
  auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(filename, password, address, view_key, spend_key, restore_height, autosave_current);
  PyMoneroJsonRequest request("generate_from_keys", params);
  m_rpc->send_json_request(request);
  clear();
  m_path = config->m_path.get();
  return this;
}

std::string PyMoneroWalletRpc::query_key(const std::string& key_type) const {
  auto params = std::make_shared<PyMoneroQueryKeyParams>(key_type);
  PyMoneroJsonRequest request("query_key", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("key")) return it->second.data();
  }

  throw std::runtime_error(std::string("Cloud not query key: ") + key_type);
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::sweep_account(const monero_tx_config &conf) {
  auto config = conf.copy();
  if (config.m_account_index == boost::none) throw std::runtime_error("Must specify an account index to sweep from");
  if (config.m_destinations.size() != 1) throw std::runtime_error("Must specify exactly one destination to sweep to");
  if (config.m_destinations[0]->m_address == boost::none) throw std::runtime_error("Must specify destination address to sweep to");
  if (config.m_destinations[0]->m_amount != boost::none) throw std::runtime_error("Cannot specify amount in sweep request");
  if (config.m_key_image != boost::none) throw std::runtime_error("Key image defined; use sweepOutput() to sweep an output by its key image");
  //if (config.m_subaddress_indices.size() == 0) throw std::runtime_error("Empty list given for subaddresses indices to sweep");
  if (config.m_sweep_each_subaddress) throw std::runtime_error("Cannot sweep each subaddress with RPC `sweep_all`");
  if (config.m_subtract_fee_from.size() > 0) throw std::runtime_error("Sweeping output does not support subtracting fees from destinations");
  
  // sweep from all subaddresses if not otherwise defined
  if (config.m_subaddress_indices.empty()) {
    uint32_t account_idx = config.m_account_index.get();
    auto subaddresses = get_subaddresses(account_idx);
    for (const auto &subaddress : subaddresses) {
      config.m_subaddress_indices.push_back(subaddress.m_index.get());
    }
  }
  if (config.m_subaddress_indices.size() == 0) throw std::runtime_error("No subaddresses to sweep from");
  bool relay = config.m_relay == true;
  auto params = std::make_shared<PyMoneroSweepParams>(config);
  PyMoneroJsonRequest request("sweep_all", params);
  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto node = response->m_result.get();
  if (config.m_relay) poll();
  std::vector<std::shared_ptr<monero_tx_wallet>> txs;
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_sent_txs(node, set, txs, config);

  for (auto &tx : set->m_txs) {
    tx->m_is_locked = true;
    tx->m_is_confirmed = false;
    tx->m_num_confirmations = 0;
    tx->m_relay = relay;
    tx->m_in_tx_pool = relay;
    tx->m_is_relayed = relay;
    tx->m_is_miner_tx = false;
    tx->m_is_failed = false;
    tx->m_ring_size = monero_utils::RING_SIZE;
    auto transfer = tx->m_outgoing_transfer.get();
    transfer->m_account_index = config.m_account_index;
    if (config.m_subaddress_indices.size() == 1) 
    {
      transfer->m_subaddress_indices = config.m_subaddress_indices;
    }
    auto destination = std::make_shared<monero_destination>();
    destination->m_address = config.m_destinations[0]->m_address;
    destination->m_amount = config.m_destinations[0]->m_amount;
    std::vector<std::shared_ptr<monero_destination>> destinations;
    destinations.push_back(destination);
    transfer->m_destinations = destinations;
    tx->m_payment_id = config.m_payment_id;
    if (tx->m_unlock_time == boost::none) tx->m_unlock_time = 0;
    if (tx->m_relay) {
      if (tx->m_last_relayed_timestamp == boost::none) {
        //tx.setLastRelayedTimestamp(System.currentTimeMillis());  // TODO (monero-wallet-rpc): provide timestamp on response; unconfirmed timestamps vary
      }  
      if (tx->m_is_double_spend_seen == boost::none) tx->m_is_double_spend_seen = false;
    }
  }

  return set->m_txs;
}

void PyMoneroWalletRpc::clear_address_cache() {
  m_address_cache.clear();
}

void PyMoneroWalletRpc::refresh_listening() {
  if (m_rpc->m_zmq_uri == boost::none) {
    if (m_poller == nullptr && m_listeners.size() > 0) m_poller = std::make_shared<PyMoneroWalletPoller>(this);
    if (m_poller != nullptr) m_poller->set_is_polling(m_listeners.size() > 0);
  } 
  /*
  else {
    if (m_zmq_listener == nullptr && m_listeners.size() > 0) m_zmq_listener = std::make_shared<PyMoneroWalletRpcZmqListener>();
    if (m_zmq_listener != nullptr) m_zmq_listener.set_is_polling(m_listeners.size() > 0);
  }
  */
}

void PyMoneroWalletRpc::poll() {
  if (m_poller != nullptr && m_poller->is_polling()) m_poller->poll(); 
}

void PyMoneroWalletRpc::clear() {
  m_listeners.clear();
  refresh_listening();
  clear_address_cache();
  m_path = "";
}
