#include "py_monero_wallet_rpc.h"
#include "utils/monero_utils.h"

PyMoneroWalletPoller::PyMoneroWalletPoller(PyMoneroWallet *wallet): m_num_polling(0) {
  m_wallet = wallet;
  init_common("monero_wallet_rpc");
}

void PyMoneroWalletPoller::poll() {
  // skip if next poll is queued
  if (m_num_polling > 1) return;
  m_num_polling++;

  // synchronize polls
  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  try {
    // skip if wallet is closed
    if (m_wallet->is_closed()) {
      m_num_polling--;
      return;
    }

    // take initial snapshot
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

    // save locked txs for next comparison
    m_prev_locked_txs = locked_txs;
    std::vector<std::shared_ptr<monero::monero_tx_wallet>> unlocked_txs;

    if (!no_longer_locked_hashes.empty()) {
      // fetch txs which are no longer locked
      monero_tx_query tx_query;
      tx_query.m_is_locked = false;
      tx_query.m_min_height = min_height;
      tx_query.m_hashes = no_longer_locked_hashes;
      tx_query.m_include_outputs = true;
      unlocked_txs = m_wallet->get_txs(tx_query);
    }

    // announce new unconfirmed and confirmed txs
    for (const auto &locked_tx : locked_txs) {
      bool announced = false;
      const std::string& tx_hash = locked_tx->m_hash.get();
      if (bool_equals_2(true, locked_tx->m_is_confirmed)) {
        if (std::find(m_prev_confirmed_notifications.begin(), m_prev_confirmed_notifications.end(), tx_hash) == m_prev_confirmed_notifications.end()) {
          m_prev_confirmed_notifications.push_back(tx_hash);
          announced = true;
        }
      }
      else {
        if (std::find(m_prev_unconfirmed_notifications.begin(), m_prev_unconfirmed_notifications.end(), tx_hash) == m_prev_unconfirmed_notifications.end()) {
          m_prev_unconfirmed_notifications.push_back(tx_hash);
          announced = true;
        }
      }

      if (announced) notify_outputs(locked_tx);
    }

    // announce new unlocked outputs
    for (const auto &unlocked_tx : unlocked_txs) {
      std::string tx_hash = unlocked_tx->m_hash.get();
      // stop tracking tx notifications
      m_prev_confirmed_notifications.erase(std::remove_if(m_prev_confirmed_notifications.begin(), m_prev_confirmed_notifications.end(), [&tx_hash](const std::string& iter){ return iter == tx_hash; }), m_prev_confirmed_notifications.end());
      m_prev_unconfirmed_notifications.erase(std::remove_if(m_prev_unconfirmed_notifications.begin(), m_prev_unconfirmed_notifications.end(), [&tx_hash](const std::string& iter){ return iter == tx_hash; }), m_prev_unconfirmed_notifications.end());
      notify_outputs(unlocked_tx);
    }

    // announce balance changes
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
  for (const auto& tx : txs) {
    if (tx->m_hash == tx_hash) return tx;
  }

  return nullptr;
}

void PyMoneroWalletPoller::on_new_block(uint64_t height) {
  m_wallet->announce_new_block(height);
}

void PyMoneroWalletPoller::notify_outputs(const std::shared_ptr<monero::monero_tx_wallet> &tx) {
  // notify spent outputs
  // TODO (monero-project): monero-wallet-rpc does not allow scrape of tx inputs so providing one input with outgoing amount
  if (tx->m_outgoing_transfer != boost::none) {
    auto outgoing_transfer = tx->m_outgoing_transfer.get();
    if (!tx->m_inputs.empty()) throw std::runtime_error("Tx inputs should be empty");
    auto output = std::make_shared<monero::monero_output_wallet>();
    output->m_amount = outgoing_transfer->m_amount.get() + tx->m_fee.get();
    output->m_account_index = outgoing_transfer->m_account_index;
    output->m_tx = tx;
    // initialize if transfer sourced from single subaddress
    if (outgoing_transfer->m_subaddress_indices.size() == 1) {
      output->m_subaddress_index = outgoing_transfer->m_subaddress_indices[0];
    }
    tx->m_inputs.clear();
    tx->m_inputs.push_back(output);
    m_wallet->announce_output_spent(output);
  }

  // notify received outputs
  if (tx->m_incoming_transfers.size() > 0) {
    if (!tx->m_outputs.empty()) {
      // TODO (monero-project): outputs only returned for confirmed txs
      for(const auto &output : tx->get_outputs_wallet()) {
        m_wallet->announce_output_received(output);
      }
    }
    else {
      // TODO (monero-project): monero-wallet-rpc does not allow scrape of unconfirmed received outputs so using incoming transfer values
      tx->m_outputs.clear();
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

// TODO: factor to common wallet rpc listener
bool PyMoneroWalletPoller::check_for_changed_balances() {
  auto balances = m_wallet->get_balances(boost::none, boost::none);
  if (balances->m_balance != m_prev_balances.get()->m_balance || balances->m_unlocked_balance != m_prev_balances.get()->m_unlocked_balance) {
    m_prev_balances = balances;
    m_wallet->announce_balances_changed(balances->m_balance, balances->m_unlocked_balance);
    return true;
  }
  return false;
}

PyMoneroWalletRpc::PyMoneroWalletRpc(const std::shared_ptr<PyMoneroRpcConnection>& rpc_connection) {
  m_rpc = rpc_connection;
  if (!m_rpc->is_online() && m_rpc->m_uri != boost::none) m_rpc->check_connection();
}

PyMoneroWalletRpc::PyMoneroWalletRpc(const std::string& uri, const std::string& username, const std::string& password, const std::string& proxy_uri, const std::string& zmq_uri, uint64_t timeout) {
  m_rpc = std::make_shared<PyMoneroRpcConnection>(uri, username, password, proxy_uri, zmq_uri, 0, timeout);
  if (m_rpc->m_uri != boost::none) m_rpc->check_connection();
}

PyMoneroWalletRpc::~PyMoneroWalletRpc() {
  MTRACE("~PyMoneroWalletRpc()");
  clear();
}

void PyMoneroWalletRpc::add_listener(monero_wallet_listener& listener) {
  PyMoneroWallet::add_listener(listener);
  refresh_listening();
}

void PyMoneroWalletRpc::remove_listener(monero_wallet_listener& listener) {
  PyMoneroWallet::remove_listener(listener);
  refresh_listening();
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
  m_rpc->send_json_request("open_wallet", params);
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

void handle_create_wallet_error(const PyMoneroRpcError& ex, const std::string& path) {
  std::string msg = ex.what();
  std::transform(msg.begin(), msg.end(), msg.begin(), [](unsigned char c){ return std::tolower(c); });
  if (msg.find("already exists") != std::string::npos) throw PyMoneroRpcError(ex.code, std::string("Wallet already exists: ") + path);
  if (msg == std::string("electrum-style word list failed verification")) throw PyMoneroRpcError(ex.code, std::string("Invalid mnemonic"));
  throw ex;
}

PyMoneroWalletRpc* PyMoneroWalletRpc::create_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config) {
  if (config == nullptr) throw std::runtime_error("Must specify config to create wallet");
  if (config->m_network_type != boost::none) throw std::runtime_error("Cannot specify network type when creating RPC wallet");
  if (config->m_seed != boost::none && (config->m_primary_address != boost::none || config->m_private_view_key != boost::none || config->m_private_spend_key != boost::none)) {
    throw std::runtime_error("Wallet can be initialized with a seed or keys but not both");
  }
  if (config->m_account_lookahead != boost::none || config->m_subaddress_lookahead != boost::none) throw std::runtime_error("monero-wallet-rpc does not support creating wallets with subaddress lookahead over rpc");
  if (config->m_connection_manager != boost::none) {
    if (config->m_server != boost::none) throw std::runtime_error("Wallet can be opened with a server or connection manager but not both");
    auto cm = config->m_connection_manager.get();
    if (cm != nullptr) {
      auto connection = cm->get_connection();
      if (connection) {
        config->m_server = *connection;
      }
    }
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
  auto node = m_rpc->send_json_request("get_languages");
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
  m_rpc->send_json_request("stop_wallet");
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

void PyMoneroWalletRpc::set_daemon_connection(const std::string& uri, const std::string& username, const std::string& password, const std::string& proxy_uri) {
  if (uri.empty()) {
    set_daemon_connection(boost::none);
    return;
  }
  boost::optional<monero_rpc_connection> rpc = PyMoneroRpcConnection(uri, username, password, proxy_uri);
  set_daemon_connection(rpc);
}

void PyMoneroWalletRpc::set_daemon_connection(const boost::optional<monero_rpc_connection>& connection, bool is_trusted, const boost::optional<PyMoneroSslOptions>& ssl_options) {
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
    params->m_ssl_private_key_path = ssl_options->m_ssl_private_key_path;
    params->m_ssl_certificate_path = ssl_options->m_ssl_certificate_path;
    params->m_ssl_ca_file = ssl_options->m_ssl_ca_file;
    params->m_ssl_allowed_fingerprints = ssl_options->m_ssl_allowed_fingerprints;
    params->m_ssl_allow_any_cert = ssl_options->m_ssl_allow_any_cert;
  }

  m_rpc->send_json_request("set_daemon", params);

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
    if (e.code == -13) throw; // no wallet file
    return e.message.find("Failed to connect to daemon") == std::string::npos;
  }
}

monero::monero_version PyMoneroWalletRpc::get_version() const {
  auto res = m_rpc->send_json_request("get_version");
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
  if (it == m_address_cache.end()) {
    // cache's all addresses at this account
    std::vector<uint32_t> empty_indices;
    get_subaddresses(account_idx, empty_indices, true);
    // uses cache
    return get_address(account_idx, subaddress_idx);
  }

  auto subaddress_map = it->second;
  auto it2 = subaddress_map.find(subaddress_idx);

  if (it2 == subaddress_map.end()) {
    // cache's all addresses at this account
    std::vector<uint32_t> empty_indices;
    get_subaddresses(account_idx, empty_indices, true);
    auto it3 = m_address_cache.find(account_idx);
    if (it3 == m_address_cache.end()) throw std::runtime_error("Could not find account address at index (" + std::to_string(account_idx) + ", " + std::to_string(subaddress_idx) + ")" );
    auto it4 = it3->second.find(subaddress_idx);
    if (it4 == it3->second.end()) return std::string("");
    return it4->second;
  }

  return it2->second;
}

monero_subaddress PyMoneroWalletRpc::get_address_index(const std::string& address) const {
  auto params = std::make_shared<PyMoneroGetAddressIndexParams>(address);
  auto res = m_rpc->send_json_request("get_address_index", params);
  auto tmplt = std::make_shared<monero::monero_subaddress>();
  PyMoneroSubaddress::from_property_tree(res, tmplt);
  return *tmplt;
}

monero_integrated_address PyMoneroWalletRpc::get_integrated_address(const std::string& standard_address, const std::string& payment_id) const {
  auto params = std::make_shared<PyMoneroMakeIntegratedAddressParams>(standard_address, payment_id);
  auto res = m_rpc->send_json_request("make_integrated_address", params);
  auto tmplt = std::make_shared<monero::monero_integrated_address>();
  PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
  return decode_integrated_address(tmplt->m_integrated_address);
}

monero_integrated_address PyMoneroWalletRpc::decode_integrated_address(const std::string& integrated_address) const {
  auto params = std::make_shared<PyMoneroSplitIntegratedAddressParams>(integrated_address);
  auto res = m_rpc->send_json_request("split_integrated_address", params);
  auto tmplt = std::make_shared<monero::monero_integrated_address>();
  PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
  tmplt->m_integrated_address = integrated_address;
  return *tmplt;
}

uint64_t PyMoneroWalletRpc::get_height() const {
  auto res = m_rpc->send_json_request("get_height");
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
  try {
    auto node = m_rpc->send_json_request("refresh", params);
    poll();
    monero_sync_result sync_result(0, false);

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("blocks_fetched")) sync_result.m_num_blocks_fetched = it->second.get_value<uint64_t>();
      else if (key == std::string("received_money")) sync_result.m_received_money = it->second.get_value<bool>();
    }

    return sync_result;
  } catch (const PyMoneroRpcError& ex) {
    if (ex.message == std::string("no connection to daemon")) throw PyMoneroError("Wallet is not connected to daemon");
    throw;
  }
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
  try {
    auto node = m_rpc->send_json_request("refresh", params);
    poll();
    monero_sync_result sync_result(0, false);

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("blocks_fetched")) sync_result.m_num_blocks_fetched = it->second.get_value<uint64_t>();
      else if (key == std::string("received_money")) sync_result.m_received_money = it->second.get_value<bool>();
    }

    return sync_result;
  } catch (const PyMoneroRpcError& ex) {
    if (ex.message == std::string("no connection to daemon")) throw PyMoneroError("Wallet is not connected to daemon");
    throw;
  }
}

void PyMoneroWalletRpc::start_syncing(uint64_t sync_period_in_ms) {
  // convert ms to seconds for rpc parameter
  uint64_t sync_period_in_seconds = sync_period_in_ms / 1000;

  // send rpc request
  auto params = std::make_shared<PyMoneroRefreshWalletParams>(true, sync_period_in_seconds);
  m_rpc->send_json_request("auto_refresh", params);

  // update sync period for poller
  m_sync_period_in_ms = sync_period_in_ms;
  if (m_poller != nullptr) m_poller->set_period_in_ms(m_sync_period_in_ms.get());

  // poll if listening
  poll();
}

void PyMoneroWalletRpc::stop_syncing() {
  auto params = std::make_shared<PyMoneroAutoRefreshParams>(false);
  m_rpc->send_json_request("auto_refresh", params);
}

void PyMoneroWalletRpc::scan_txs(const std::vector<std::string>& tx_hashes) {
  if (tx_hashes.empty()) throw std::runtime_error("No tx hashes given to scan");
  auto params = std::make_shared<PyMoneroScanTxParams>(tx_hashes);
  m_rpc->send_json_request("scan_tx", params);
  poll();
}

void PyMoneroWalletRpc::rescan_spent() {
  m_rpc->send_json_request("rescan_spent");
}

void PyMoneroWalletRpc::rescan_blockchain() {
  m_rpc->send_json_request("rescan_blockchain");
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

monero_account PyMoneroWalletRpc::get_account(const uint32_t account_idx, bool include_subaddresses) const {
  return get_account(account_idx, include_subaddresses, false);
}

monero_account PyMoneroWalletRpc::get_account(const uint32_t account_idx, bool include_subaddresses, bool skip_balances) const {
  for(auto& account : monero::monero_wallet::get_accounts()) {
    if (account.m_index.get() == account_idx) {
      if (include_subaddresses) {
        std::vector<uint32_t> empty_indices;
        account.m_subaddresses = get_subaddresses(account_idx, empty_indices, skip_balances);
      }
      return account;
    }
  }
  throw std::runtime_error("Account with index " + std::to_string(account_idx) + " does not exist");
}

std::vector<monero_account> PyMoneroWalletRpc::get_accounts(bool include_subaddresses, const std::string& tag) const {
  return get_accounts(include_subaddresses, tag, false);
}

std::vector<monero_account> PyMoneroWalletRpc::get_accounts(bool include_subaddresses, const std::string& tag, bool skip_balances) const {
  auto params = std::make_shared<PyMoneroGetAccountsParams>(tag);
  auto node = m_rpc->send_json_request("get_accounts", params);
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
      auto node2 = m_rpc->send_json_request("get_balance", params2);
      auto bal_res = std::make_shared<PyMoneroGetBalanceResponse>();
      PyMoneroGetBalanceResponse::from_property_tree(node2, bal_res);
      for (const auto &subaddress : bal_res->m_per_subaddress) {
        // merge info
        auto account = &accounts[subaddress->m_account_index.get()];
        if (account->m_index != subaddress->m_account_index) throw std::runtime_error("RPC accounts are out of order");
        auto tgt_subaddress = &account->m_subaddresses[subaddress->m_index.get()];
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
  auto node = m_rpc->send_json_request("create_account", params);
  monero_account res;
  res.m_balance = 0;
  res.m_unlocked_balance = 0;
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
  auto node = m_rpc->send_json_request("get_address", params);
  std::vector<monero_subaddress> subaddresses;

  // initialize subaddresses
  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("addresses")) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto subaddress = std::make_shared<monero::monero_subaddress>();
        PyMoneroSubaddress::from_rpc_property_tree(it2->second, subaddress);
        subaddress->m_account_index = account_idx;
        subaddresses.push_back(*subaddress);
      }
      break;
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
    auto node2 = m_rpc->send_json_request("get_balance", params);
    std::vector<std::shared_ptr<monero::monero_subaddress>> subaddresses2;
    PyMoneroSubaddress::from_rpc_property_tree(node2, subaddresses2);

    for (auto &tgt_subaddress: subaddresses) {
      for (const auto &rpc_subaddress : subaddresses2) {
        if (rpc_subaddress->m_index != tgt_subaddress.m_index) continue; // skip to subaddress with same index
        if (rpc_subaddress->m_balance != boost::none) tgt_subaddress.m_balance = rpc_subaddress->m_balance;
        if (rpc_subaddress->m_unlocked_balance != boost::none) tgt_subaddress.m_unlocked_balance = rpc_subaddress->m_unlocked_balance;
        if (rpc_subaddress->m_num_unspent_outputs != boost::none) tgt_subaddress.m_num_unspent_outputs = rpc_subaddress->m_num_unspent_outputs;
        if (rpc_subaddress->m_num_blocks_to_unlock != boost::none) tgt_subaddress.m_num_blocks_to_unlock = rpc_subaddress->m_num_blocks_to_unlock;
      }
    }
  }

  // cache addresses
  auto it = m_address_cache.find(account_idx);
  if (it == m_address_cache.end()) {
    m_address_cache[account_idx] = std::unordered_map<uint32_t, std::string>();
  }

  for (const auto& subaddress : subaddresses) {
    m_address_cache[account_idx][subaddress.m_index.get()] = subaddress.m_address.get();
  }

  // return results
  return subaddresses;
}

std::vector<monero_subaddress> PyMoneroWalletRpc::get_subaddresses(uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) const {
  return get_subaddresses(account_idx, subaddress_indices, false);
}

std::vector<monero_subaddress> PyMoneroWalletRpc::get_subaddresses(const uint32_t account_idx) const {
  std::vector<uint32_t> empty_indices;
  return get_subaddresses(account_idx, empty_indices);
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
  auto node = m_rpc->send_json_request("create_address", params);
  monero_subaddress sub;
  sub.m_account_index = account_idx;
  if (!label.empty()) sub.m_label = label;
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
  m_rpc->send_json_request("label_address", params);
}

std::string PyMoneroWalletRpc::export_outputs(bool all) const {
  auto params = std::make_shared<PyMoneroImportExportOutputsParams>(all);
  auto node = m_rpc->send_json_request("export_outputs", params);

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("outputs_data_hex")) return it->second.data();
  }

  throw std::runtime_error("Could not get outputs hex");
}

int PyMoneroWalletRpc::import_outputs(const std::string& outputs_hex) {
  auto params = std::make_shared<PyMoneroImportExportOutputsParams>(outputs_hex);
  auto node = m_rpc->send_json_request("import_outputs", params);
  int num_imported = 0;

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("num_imported")) {
      num_imported = it->second.get_value<int>();
      break;
    }
  }

  return num_imported;
}

std::vector<std::shared_ptr<monero_key_image>> PyMoneroWalletRpc::export_key_images(bool all) const {
  auto params = std::make_shared<PyMoneroImportExportKeyImagesParams>(all);
  auto node = m_rpc->send_json_request("export_key_images", params);
  std::vector<std::shared_ptr<monero::monero_key_image>> key_images;
  PyMoneroKeyImage::from_property_tree(node, key_images);
  return key_images;
}

std::shared_ptr<monero_key_image_import_result> PyMoneroWalletRpc::import_key_images(const std::vector<std::shared_ptr<monero_key_image>>& key_images) {
  auto params = std::make_shared<PyMoneroImportExportKeyImagesParams>(key_images);
  auto node = m_rpc->send_json_request("import_key_images", params);
  auto import_result = std::make_shared<monero_key_image_import_result>();
  PyMoneroKeyImageImportResult::from_property_tree(node, import_result);
  return import_result;
}

void PyMoneroWalletRpc::freeze_output(const std::string& key_image) {
  auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
  m_rpc->send_json_request("freeze", params);
}

void PyMoneroWalletRpc::thaw_output(const std::string& key_image) {
  auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
  m_rpc->send_json_request("thaw", params);
}

bool PyMoneroWalletRpc::is_output_frozen(const std::string& key_image) {
  auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
  auto node = m_rpc->send_json_request("frozen", params);

  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("frozen")) return it->second.get_value<bool>();
  }

  throw std::runtime_error("Could not get output");
}

monero_tx_priority PyMoneroWalletRpc::get_default_fee_priority() const {
  auto node = m_rpc->send_json_request("get_default_fee_priority");

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
  if (config.m_address == boost::none && config.m_destinations.empty()) throw std::runtime_error("Destinations cannot be empty");
  if (config.m_sweep_each_subaddress != boost::none) throw std::runtime_error("Sweep each subaddress not supported");
  if (config.m_below_amount != boost::none) throw std::runtime_error("Below amount not supported");

  if (config.m_can_split == boost::none) {
    config = config.copy();
    config.m_can_split = true;
  }
  if (bool_equals_2(true, config.m_relay) && is_multisig()) throw std::runtime_error("Cannot relay multisig transaction until co-signed");

  // determine account and subaddresses to send from
  if (config.m_account_index == boost::none) throw std::runtime_error("Must specify the account index to send from");
  auto account_idx = config.m_account_index.get();

  // cannot apply subtractFeeFrom with `transfer_split` call
  if (bool_equals_2(true, config.m_can_split) && config.m_subtract_fee_from.size() > 0) {
    throw std::runtime_error("subtractfeefrom transfers cannot be split over multiple transactions yet");
  }

  // build request parameters
  auto params = std::make_shared<PyMoneroTransferParams>(config);
  std::string request_path = "transfer";
  if (bool_equals_2(true, config.m_can_split)) request_path = "transfer_split";

  boost::property_tree::ptree node;
  try {
    node = m_rpc->send_json_request(request_path, params);
  } catch (const PyMoneroRpcError& ex) {
    std::string message = ex.what();
    if (message.find("WALLET_RPC_ERROR_CODE_WRONG_ADDRESS") != std::string::npos) throw PyMoneroError("Invalid destination address");
    throw;
  }

  // pre-initialize txs iff present. multisig and view-only wallets will have tx set without transactions
  std::vector<std::shared_ptr<monero_tx_wallet>> txs;
  int num_txs = 0;
  bool can_split = bool_equals_2(true, config.m_can_split);
  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (can_split && key == std::string("fee_list")) {
      auto fee_list_node = it->second;
      for(auto it2 = fee_list_node.begin(); it2 != fee_list_node.end(); ++it2) {
        num_txs++;
      }
    }
    else if (!can_split && key == std::string("fee")) {
      num_txs = 1;
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
  if (bool_equals_2(true, config.m_relay)) poll();

  // initialize tx set from rpc response with pre-initialized txs
  auto tx_set = std::make_shared<monero::monero_tx_set>();
  if (can_split) {
    PyMoneroTxSet::from_sent_txs(node, tx_set, txs, config);
  }
  else if (txs.empty()) {
    auto __tx = std::make_shared<monero::monero_tx_wallet>();
    PyMoneroTxSet::from_tx(node, tx_set, __tx, true, config);
  }
  else {
    PyMoneroTxSet::from_tx(node, tx_set, txs[0], true, config);
  }

  return tx_set->m_txs;
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::sweep_unlocked(const monero_tx_config& config) {
  // validate config
  std::vector<std::shared_ptr<monero_destination>> destinations = config.get_normalized_destinations();
  if (destinations.size() != 1) throw std::runtime_error("Must specify exactly one destination to sweep to");
  if (destinations[0]->m_address == boost::none) throw std::runtime_error("Must specify destination address to sweep to");
  if (destinations[0]->m_amount != boost::none) throw std::runtime_error("Cannot specify amount to sweep");
  if (config.m_account_index == boost::none && config.m_subaddress_indices.size() != 0) throw std::runtime_error("Must specify account index if subaddress indices are specified");

  // determine account and subaddress indices to sweep; default to all with unlocked balance if not specified
  std::map<uint32_t, std::vector<uint32_t>> indices;
  if (config.m_account_index != boost::none) {
    if (config.m_subaddress_indices.size() != 0) {
      indices[config.m_account_index.get()] = config.m_subaddress_indices;
    } else {
      std::vector<uint32_t> subaddress_indices;
      for (const monero_subaddress& subaddress : monero_wallet::get_subaddresses(config.m_account_index.get())) {
        // TODO wallet rpc sweep_all now supports req.subaddr_indices_all
        if (subaddress.m_unlocked_balance.get() > 0) subaddress_indices.push_back(subaddress.m_index.get());
      }
      indices[config.m_account_index.get()] = subaddress_indices;
    }
  } else {
    std::vector<monero_account> accounts = monero_wallet::get_accounts(true);
    for (const monero_account& account : accounts) {
      if (account.m_unlocked_balance.get() > 0) {
        std::vector<uint32_t> subaddress_indices;
        for (const monero_subaddress& subaddress : account.m_subaddresses) {
          if (subaddress.m_unlocked_balance.get() > 0) subaddress_indices.push_back(subaddress.m_index.get());
        }
        indices[account.m_index.get()] = subaddress_indices;
      }
    }
  }

  // sweep from each account and collect resulting txs
  std::vector<std::shared_ptr<monero_tx_wallet>> txs;
  for (std::pair<uint32_t, std::vector<uint32_t>> subaddress_indices_pair : indices) {

    // copy and modify the original config
    monero_tx_config copy = config.copy();
    copy.m_account_index = subaddress_indices_pair.first;
    copy.m_sweep_each_subaddress = false;

    // sweep all subaddresses together  // TODO monero-project: can this reveal outputs belong to the same wallet?
    if (copy.m_sweep_each_subaddress == boost::none || copy.m_sweep_each_subaddress.get() != true) {
      copy.m_subaddress_indices = subaddress_indices_pair.second;
      std::vector<std::shared_ptr<monero_tx_wallet>> account_txs = sweep_account(copy);
      txs.insert(std::end(txs), std::begin(account_txs), std::end(account_txs));
    }

    // otherwise sweep each subaddress individually
    else {
      for (uint32_t subaddress_index : subaddress_indices_pair.second) {
        std::vector<uint32_t> subaddress_indices;
        subaddress_indices.push_back(subaddress_index);
        copy.m_subaddress_indices = subaddress_indices;
        std::vector<std::shared_ptr<monero_tx_wallet>> account_txs = sweep_account(copy);
        txs.insert(std::end(txs), std::begin(account_txs), std::end(account_txs));
      }
    }
  }

  // notify listeners of spent funds
  if (config.m_relay != boost::none && config.m_relay.get()) poll();
  return txs;
}

std::shared_ptr<monero_tx_wallet> PyMoneroWalletRpc::sweep_output(const monero_tx_config& config) {
  // validate request
  std::vector<std::shared_ptr<monero_destination>> destinations = config.get_normalized_destinations();
  if (config.m_sweep_each_subaddress != boost::none) throw std::runtime_error("Cannot sweep each subaddress when sweeping single output");
  if (config.m_below_amount != boost::none) throw std::runtime_error("Cannot specifiy below_amount when sweeping single output");
  if (config.m_can_split != boost::none) throw std::runtime_error("Splitting is not applicable when sweeping output");
  // TODO check first destination address is not boost::none/empty
  if (destinations.size() != 1) throw std::runtime_error("Must provide exactly one destination address to sweep output to");
  if (destinations[0]->m_address == boost::none) throw std::runtime_error("Must specify destination address to sweep to");
  if (destinations[0]->m_amount != boost::none) throw std::runtime_error("Cannot specify amount to sweep");

  auto params = std::make_shared<PyMoneroSweepParams>(config);
  auto node = m_rpc->send_json_request("sweep_single", params);
  if (bool_equals_2(true, config.m_relay)) poll();
  auto set = std::make_shared<monero_tx_set>();
  auto tx = std::make_shared<monero::monero_tx_wallet>();
  PyMoneroTxWallet::init_sent(config, tx, true);
  PyMoneroTxSet::from_tx(node, set, tx, true, config);
  return tx;
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::sweep_dust(bool relay) {
  auto params = std::make_shared<PyMoneroSweepParams>(relay);
  auto node = m_rpc->send_json_request("sweep_dust", params);
  if (relay) poll();
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_sent_txs(node, set);
  return set->m_txs;
}

std::vector<std::string> PyMoneroWalletRpc::relay_txs(const std::vector<std::string>& tx_metadatas) {
  if (tx_metadatas.empty()) throw std::runtime_error("Must provide an array of tx metadata to relay");

  std::vector<std::string> tx_hashes;

  for (const auto &tx_metadata : tx_metadatas) {
    auto params = std::make_shared<PyMoneroWalletRelayTxParams>(tx_metadata);
    auto node = m_rpc->send_json_request("relay_tx", params);

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
  auto node = m_rpc->send_json_request("describe_transfer", params);
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_describe_transfer(node, set);
  return *set;
}

monero_tx_set PyMoneroWalletRpc::sign_txs(const std::string& unsigned_tx_hex) {
  auto params = std::make_shared<PyMoneroSignDescribeTransferParams>(unsigned_tx_hex);
  auto node = m_rpc->send_json_request("sign_transfer", params);
  auto set = std::make_shared<monero_tx_set>();
  PyMoneroTxSet::from_sent_txs(node, set);
  return *set;
}

std::vector<std::string> PyMoneroWalletRpc::submit_txs(const std::string& signed_tx_hex) {
  auto params = std::make_shared<PyMoneroSubmitTransferParams>(signed_tx_hex);
  auto node = m_rpc->send_json_request("submit_transfer", params);
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
  auto node = m_rpc->send_json_request("sign", params);
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

monero_message_signature_result PyMoneroWalletRpc::verify_message(const std::string& msg, const std::string& address, const std::string& signature) const {
  auto params = std::make_shared<PyMoneroVerifySignMessageParams>(msg, address, signature);
  auto sig_result = std::make_shared<monero::monero_message_signature_result>();
  sig_result->m_is_good = false;
  try {
    auto node = m_rpc->send_json_request("verify", params);
    PyMoneroMessageSignatureResult::from_property_tree(node, sig_result);
  } catch (const PyMoneroRpcError& ex) {
    if (ex.code != -2) throw;
  }

  return *sig_result;
}

std::string PyMoneroWalletRpc::get_tx_key(const std::string& tx_hash) const {
  try {
    auto params = std::make_shared<PyMoneroCheckTxKeyParams>(tx_hash);
    auto node = m_rpc->send_json_request("get_tx_key", params);

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("tx_key")) {
        return it->second.data();
      }
    }

    throw std::runtime_error("Could not get tx key");
  } catch (const PyMoneroRpcError& ex) {
    if (ex.code == -8 && ex.what() == std::string("TX ID has invalid format")) {
      // normalize error message
      throw PyMoneroRpcError(-8, "TX hash has invalid format");
    }
    throw;
  }
}

std::shared_ptr<monero_check_tx> PyMoneroWalletRpc::check_tx_key(const std::string& tx_hash, const std::string& tx_key, const std::string& address) const {
  try {
    auto params = std::make_shared<PyMoneroCheckTxKeyParams>(tx_hash, tx_key, address);
    auto node = m_rpc->send_json_request("check_tx_key", params);
    auto check = std::make_shared<monero::monero_check_tx>();
    check->m_is_good = true;
    PyMoneroCheckTxProof::from_property_tree(node, check);
    return check;
  } catch (const PyMoneroRpcError& ex) {
    if (ex.code == -8 && ex.what() == std::string("TX ID has invalid format")) {
      // normalize error message
      throw PyMoneroRpcError(-8, "TX hash has invalid format");
    }
    throw;
  }
}

std::string PyMoneroWalletRpc::get_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message) const {
  try {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
    params->m_address = address;
    auto node = m_rpc->send_json_request("get_tx_proof", params);
    return PyMoneroReserveProofSignature::from_property_tree(node);
  } catch (const PyMoneroRpcError& ex) {
    if (ex.code == -8 && ex.what() == std::string("TX ID has invalid format")) {
      // normalize error message
      throw PyMoneroRpcError(-8, "TX hash has invalid format");
    }
    throw;
  }
}

std::shared_ptr<monero_check_tx> PyMoneroWalletRpc::check_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) const {
  try {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, address, message, signature);
    auto node = m_rpc->send_json_request("check_tx_proof", params);
    auto check = std::make_shared<monero::monero_check_tx>();
    PyMoneroCheckTxProof::from_property_tree(node, check);
    return check;
  } catch (const PyMoneroRpcError& ex) {
    // normalize error message
    if (ex.code == -1 && std::string(ex.what()).find("basic_string") != std::string::npos) {
      throw PyMoneroRpcError(-1, "Must provide signature to check tx proof");
    }
    if (ex.code == -8 && ex.what() == std::string("TX ID has invalid format")) {
      throw PyMoneroRpcError(-8, "TX hash has invalid format");
    }
    throw;
  }
}

std::string PyMoneroWalletRpc::get_spend_proof(const std::string& tx_hash, const std::string& message) const {
  try {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
    auto node = m_rpc->send_json_request("get_spend_proof", params);
    return PyMoneroReserveProofSignature::from_property_tree(node);
  } catch (const PyMoneroRpcError& ex) {
    if (ex.code == -8 && ex.what() == std::string("TX ID has invalid format")) {
      // normalize error message
      throw PyMoneroRpcError(-8, "TX hash has invalid format");
    }
    throw;
  }
}

bool PyMoneroWalletRpc::check_spend_proof(const std::string& tx_hash, const std::string& message, const std::string& signature) const {
  try {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
    params->m_signature = signature;
    auto node = m_rpc->send_json_request("check_spend_proof", params);
    auto proof = std::make_shared<monero::monero_check_reserve>();
    PyMoneroCheckReserve::from_property_tree(node, proof);
    return proof->m_is_good;
  } catch (const PyMoneroRpcError& ex) {
    if (ex.code == -8 && ex.what() == std::string("TX ID has invalid format")) {
      // normalize error message
      throw PyMoneroRpcError(-8, "TX hash has invalid format");
    }
    throw;
  }
}

std::string PyMoneroWalletRpc::get_reserve_proof_wallet(const std::string& message) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(message);
  auto node = m_rpc->send_json_request("get_reserve_proof", params);
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

std::string PyMoneroWalletRpc::get_reserve_proof_account(uint32_t account_idx, uint64_t amount, const std::string& message) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(account_idx, amount, message);
  auto node = m_rpc->send_json_request("get_reserve_proof", params);
  return PyMoneroReserveProofSignature::from_property_tree(node);
}

std::shared_ptr<monero_check_reserve> PyMoneroWalletRpc::check_reserve_proof(const std::string& address, const std::string& message, const std::string& signature) const {
  auto params = std::make_shared<PyMoneroReserveProofParams>(address, message, signature);
  auto node = m_rpc->send_json_request("check_reserve_proof", params);
  auto proof = std::make_shared<monero::monero_check_reserve>();
  PyMoneroCheckReserve::from_property_tree(node, proof);
  return proof;
}

std::string PyMoneroWalletRpc::get_tx_note(const std::string& tx_hash) const {
  std::vector<std::string> tx_hashes;
  tx_hashes.push_back(tx_hash);
  auto notes = get_tx_notes(tx_hashes);
  if (notes.size() != 1) throw std::runtime_error("Expected one tx note");
  return notes[0];
}

std::vector<std::string> PyMoneroWalletRpc::get_tx_notes(const std::vector<std::string>& tx_hashes) const {
  auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes);
  auto node = m_rpc->send_json_request("get_tx_notes", params);
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

void PyMoneroWalletRpc::set_tx_note(const std::string& tx_hash, const std::string& note) {
  std::vector<std::string> tx_hashes;
  std::vector<std::string> notes;
  tx_hashes.push_back(tx_hash);
  notes.push_back(note);

  set_tx_notes(tx_hashes, notes);
}

void PyMoneroWalletRpc::set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
  auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes, notes);
  m_rpc->send_json_request("set_tx_notes", params);
}

std::vector<monero_address_book_entry> PyMoneroWalletRpc::get_address_book_entries(const std::vector<uint64_t>& indices) const {
  auto params = std::make_shared<PyMoneroAddressBookEntryParams>(indices);
  auto node = m_rpc->send_json_request("get_address_book", params);
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
  auto node = m_rpc->send_json_request("add_address_book", params);

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
  m_rpc->send_json_request("edit_address_book", params);
}

void PyMoneroWalletRpc::delete_address_book_entry(uint64_t index) {
  auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index);
  m_rpc->send_json_request("delete_address_book", params);
}

void PyMoneroWalletRpc::tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) {
  auto params = std::make_shared<PyMoneroTagAccountsParams>(tag, account_indices);
  m_rpc->send_json_request("tag_accounts", params);
}

void PyMoneroWalletRpc::untag_accounts(const std::vector<uint32_t>& account_indices) {
  auto params = std::make_shared<PyMoneroTagAccountsParams>(account_indices);
  m_rpc->send_json_request("untag_accounts", params);
}

std::vector<std::shared_ptr<PyMoneroAccountTag>> PyMoneroWalletRpc::get_account_tags() {
  auto res = m_rpc->send_json_request("get_account_tags");
  std::vector<std::shared_ptr<PyMoneroAccountTag>> account_tags;
  PyMoneroAccountTag::from_property_tree(res, account_tags);
  return account_tags;
}

void PyMoneroWalletRpc::set_account_tag_label(const std::string& tag, const std::string& label) {
  auto params = std::make_shared<PyMoneroSetAccountTagDescriptionParams>(tag, label);
  m_rpc->send_json_request("set_account_tag_description", params);
}

std::string PyMoneroWalletRpc::get_payment_uri(const monero_tx_config& config) const {
  auto params = std::make_shared<PyMoneroGetPaymentUriParams>(config);
  auto res = m_rpc->send_json_request("make_uri", params);
  return PyMoneroGetPaymentUriResponse::from_property_tree(res);
}

std::shared_ptr<monero_tx_config> PyMoneroWalletRpc::parse_payment_uri(const std::string& uri) const {
  auto params = std::make_shared<PyMoneroParsePaymentUriParams>(uri);
  auto res = m_rpc->send_json_request("parse_uri", params);
  auto uri_response = std::make_shared<PyMoneroParsePaymentUriResponse>();
  PyMoneroParsePaymentUriResponse::from_property_tree(res, uri_response);
  return uri_response->to_tx_config();
}

void PyMoneroWalletRpc::set_attribute(const std::string& key, const std::string& val) {
  auto params = std::make_shared<PyMoneroWalletAttributeParams>(key, val);
  m_rpc->send_json_request("set_attribute", params);
}

bool PyMoneroWalletRpc::get_attribute(const std::string& key, std::string& value) const {
  try {
    auto params = std::make_shared<PyMoneroWalletAttributeParams>(key);
    auto res = m_rpc->send_json_request("get_attribute", params);
    PyMoneroWalletAttributeParams::from_property_tree(res, params);
    if (params->m_value == boost::none) return false;
    value = params->m_value.get();
    return true;
  }
  catch (const PyMoneroRpcError& ex) {
    if (ex.code == -45) { // attribute not found
      value = std::string("");
      return true;
    }
  }

  return false;
}

void PyMoneroWalletRpc::start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) {
  auto params = std::make_shared<PyMoneroWalletStartMiningParams>(num_threads.value_or(0), background_mining.value_or(false), ignore_battery.value_or(false));
  auto response = m_rpc->send_json_request("start_mining", params);
  // TODO PyMoneroDaemonRpc::check_response_status(response);
}

void PyMoneroWalletRpc::stop_mining() {
  m_rpc->send_json_request("stop_mining");
}

bool PyMoneroWalletRpc::is_multisig_import_needed() const {
  auto res = m_rpc->send_json_request("get_balance");
  auto balance = std::make_shared<PyMoneroGetBalanceResponse>();
  PyMoneroGetBalanceResponse::from_property_tree(res, balance);
  return bool_equals_2(true, balance->m_multisig_import_needed);
}

monero_multisig_info PyMoneroWalletRpc::get_multisig_info() const {
  auto res = m_rpc->send_json_request("is_multisig");
  auto info = std::make_shared<monero::monero_multisig_info>();
  PyMoneroMultisigInfo::from_property_tree(res, info);
  return *info;
}

std::string PyMoneroWalletRpc::prepare_multisig() {
  auto params = std::make_shared<PyMoneroPrepareMultisigParams>();
  auto res = m_rpc->send_json_request("prepare_multisig", params);
  clear_address_cache();
  return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
}

std::string PyMoneroWalletRpc::make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) {
  auto params = std::make_shared<PyMoneroMakeMultisigParams>(multisig_hexes, threshold, password);
  auto res = m_rpc->send_json_request("make_multisig", params);
  clear_address_cache();
  return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
}

monero_multisig_init_result PyMoneroWalletRpc::exchange_multisig_keys(const std::vector<std::string>& multisig_hexes, const std::string& password) {
  auto params = std::make_shared<PyMoneroMakeMultisigParams>(multisig_hexes, password);
  auto res = m_rpc->send_json_request("exchange_multisig_keys", params);
  clear_address_cache();
  auto multisig_init = std::make_shared<monero_multisig_init_result>();
  PyMoneroMultisigInitResult::from_property_tree(res, multisig_init);
  return *multisig_init;
}

std::string PyMoneroWalletRpc::export_multisig_hex() {
  auto res = m_rpc->send_json_request("export_multisig_info");
  return PyMoneroExportMultisigHexResponse::from_property_tree(res);
}

int PyMoneroWalletRpc::import_multisig_hex(const std::vector<std::string>& multisig_hexes) {
  auto params = std::make_shared<PyMoneroImportMultisigHexParams>(multisig_hexes);
  auto res = m_rpc->send_json_request("import_multisig_info", params);
  return PyMoneroImportMultisigHexResponse::from_property_tree(res);
}

monero_multisig_sign_result PyMoneroWalletRpc::sign_multisig_tx_hex(const std::string& multisig_tx_hex) {
  auto params = std::make_shared<PyMoneroMultisigTxDataParams>(multisig_tx_hex);
  auto res = m_rpc->send_json_request("sign_multisig", params);
  auto multisig_result = std::make_shared<monero::monero_multisig_sign_result>();
  PyMoneroMultisigSignResult::from_property_tree(res, multisig_result);
  return *multisig_result;
}

std::vector<std::string> PyMoneroWalletRpc::submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex) {
  auto params = std::make_shared<PyMoneroMultisigTxDataParams>(signed_multisig_tx_hex);
  auto res = m_rpc->send_json_request("submit_multisig", params);
  return PyMoneroSubmitMultisigTxHexResponse::from_property_tree(res);
}

void PyMoneroWalletRpc::change_password(const std::string& old_password, const std::string& new_password) {
  auto params = std::make_shared<PyMoneroChangeWalletPasswordParams>(old_password, new_password);
  m_rpc->send_json_request("change_wallet_password", params);
}

void PyMoneroWalletRpc::save() {
  m_rpc->send_json_request("store");
}

bool PyMoneroWalletRpc::is_closed() const {
  try {
    get_primary_address();
  } catch (const PyMoneroRpcError& ex) {
    return ex.code == -8 && ex.what() == std::string("No wallet file");
  }

  return false;
}

void PyMoneroWalletRpc::close(bool save) {
  MTRACE("PyMoneroWalletRpc::close()");
  clear();
  auto params = std::make_shared<PyMoneroCloseWalletParams>(save);
  m_rpc->send_json_request("close_wallet", params);
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
    auto res = m_rpc->send_json_request("get_balance", params);
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
  try { m_rpc->send_json_request("create_wallet", params); }
  catch (const PyMoneroRpcError& ex) { handle_create_wallet_error(ex, filename); }
  clear();
  m_path = config.m_path.get();
  return this;
}

PyMoneroWalletRpc* PyMoneroWalletRpc::create_wallet_from_seed(const std::shared_ptr<PyMoneroWalletConfig> &conf) {
  auto config = conf->copy();
  if (config.m_language == boost::none || config.m_language->empty()) config.m_language = "English";
  auto filename = config.m_path.get();
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
  try { m_rpc->send_json_request("restore_deterministic_wallet", params); }
  catch (const PyMoneroRpcError& ex) { handle_create_wallet_error(ex, filename); }
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
  try { m_rpc->send_json_request("generate_from_keys", params); }
  catch (const PyMoneroRpcError& ex) { handle_create_wallet_error(ex, filename); }
  clear();
  m_path = config->m_path.get();
  return this;
}

std::string PyMoneroWalletRpc::query_key(const std::string& key_type) const {
  auto params = std::make_shared<PyMoneroQueryKeyParams>(key_type);
  auto node = m_rpc->send_json_request("query_key", params);

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("key")) return it->second.data();
  }

  throw std::runtime_error(std::string("Cloud not query key: ") + key_type);
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::sweep_account(const monero_tx_config &conf) {
  auto config = conf.copy();
  // validate config
  if (config.m_account_index == boost::none) throw std::runtime_error("Must specify an account index to sweep from");
  std::vector<std::shared_ptr<monero_destination>> destinations = config.get_normalized_destinations();
  if (destinations.size() != 1) throw std::runtime_error("Must provide exactly one destination address to sweep output to");
  if (destinations[0]->m_address == boost::none) throw std::runtime_error("Must specify destination address to sweep to");
  if (destinations[0]->m_amount != boost::none) throw std::runtime_error("Cannot specify destination amount to sweep");
  if (config.m_key_image != boost::none) throw std::runtime_error("Cannot define key image in sweep_account(); use sweep_output() to sweep an output by its key image");
  if (bool_equals_2(true, config.m_sweep_each_subaddress)) throw std::runtime_error("Cannot sweep each subaddress with RPC `sweep_all`");
  if (config.m_subtract_fee_from.size() > 0) throw std::runtime_error("Sweep transactions do not support subtracting fees from destinations");

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
  params->m_get_tx_key = boost::none;
  params->m_get_tx_keys = true;
  auto node = m_rpc->send_json_request("sweep_all", params);
  if (bool_equals_2(true, config.m_relay)) poll();
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
    if (tx->m_outgoing_transfer == boost::none) throw std::runtime_error("Tx outgoing transfer is none");
    auto transfer = tx->m_outgoing_transfer.get();
    transfer->m_account_index = config.m_account_index;
    if (config.m_subaddress_indices.size() == 1) {
      transfer->m_subaddress_indices = config.m_subaddress_indices;
    }
    auto destination = std::make_shared<monero::monero_destination>();
    destination->m_address = destinations[0]->m_address;
    destination->m_amount = transfer->m_amount;
    transfer->m_destinations.clear();
    transfer->m_destinations.push_back(destination);
    tx->m_payment_id = config.m_payment_id;
    if (tx->m_unlock_time == boost::none) tx->m_unlock_time = 0;
    if (relay) {
      if (tx->m_last_relayed_timestamp == boost::none) {
        // TODO (monero-wallet-rpc): provide timestamp on response; unconfirmed timestamps vary
        tx->m_last_relayed_timestamp = static_cast<uint64_t>(time(NULL));
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
  if (m_poller == nullptr && !m_listeners.empty()) {
    m_poller = std::make_unique<PyMoneroWalletPoller>(this);
    if (m_sync_period_in_ms != boost::none) m_poller->set_period_in_ms(m_sync_period_in_ms.get());
  }
  if (m_poller != nullptr) {
    m_poller->set_is_polling(!m_listeners.empty());
  }
}

void PyMoneroWalletRpc::poll() {
  if (m_poller != nullptr && m_poller->is_polling()) {
    m_poller->poll();
  }
}

void PyMoneroWalletRpc::clear() {
  m_listeners.clear();
  refresh_listening();
  clear_address_cache();
  m_path = "";
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::get_txs() const {
  return get_txs(monero_tx_query());
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroWalletRpc::get_txs(const monero_tx_query& query) const {
  MTRACE("get_txs(query)");

  // copy query
  std::shared_ptr<monero_tx_query> query_sp = std::make_shared<monero_tx_query>(query); // convert to shared pointer
  std::shared_ptr<monero_tx_query> _query = query_sp->copy(query_sp, std::make_shared<monero_tx_query>()); // deep copy

  // temporarily disable transfer and output queries in order to collect all tx context
  boost::optional<std::shared_ptr<monero_transfer_query>> transfer_query = _query->m_transfer_query;
  boost::optional<std::shared_ptr<monero_output_query>> input_query = _query->m_input_query;
  boost::optional<std::shared_ptr<monero_output_query>> output_query = _query->m_output_query;
  _query->m_transfer_query = boost::none;
  _query->m_input_query = boost::none;
  _query->m_output_query = boost::none;

  // fetch all transfers that meet tx query
  std::shared_ptr<monero_transfer_query> temp_transfer_query = std::make_shared<monero_transfer_query>();
  temp_transfer_query->m_tx_query = PyMoneroTxQuery::decontextualize(_query->copy(_query, std::make_shared<monero_tx_query>()));
  temp_transfer_query->m_tx_query.get()->m_transfer_query = temp_transfer_query;
  std::vector<std::shared_ptr<monero_transfer>> transfers = get_transfers_aux(*temp_transfer_query);
  monero_utils::free(temp_transfer_query->m_tx_query.get());

  // collect unique txs from transfers while retaining order
  std::vector<std::shared_ptr<monero_tx_wallet>> txs = std::vector<std::shared_ptr<monero_tx_wallet>>();
  std::unordered_set<std::shared_ptr<monero_tx_wallet>> txsSet;
  for (const std::shared_ptr<monero_transfer>& transfer : transfers) {
    if (txsSet.find(transfer->m_tx) == txsSet.end()) {
      txs.push_back(transfer->m_tx);
      txsSet.insert(transfer->m_tx);
    }
  }

  // cache types into maps for merging and lookup
  std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>> tx_map;
  std::unordered_map<uint64_t, std::shared_ptr<monero_block>> block_map;
  for (const std::shared_ptr<monero_tx_wallet>& tx : txs) {
    PyMoneroTxWallet::merge_tx(tx, tx_map, block_map);
  }

  // fetch and merge outputs if requested
  if ((_query->m_include_outputs != boost::none && *_query->m_include_outputs) || output_query != boost::none) {
    std::shared_ptr<monero_output_query> temp_output_query = std::make_shared<monero_output_query>();
    temp_output_query->m_tx_query = PyMoneroTxQuery::decontextualize(_query->copy(_query, std::make_shared<monero_tx_query>()));
    temp_output_query->m_tx_query.get()->m_output_query = temp_output_query;
    std::vector<std::shared_ptr<monero_output_wallet>> outputs = get_outputs_aux(*temp_output_query);
    monero_utils::free(temp_output_query->m_tx_query.get());

    // merge output txs one time while retaining order
    std::unordered_set<std::shared_ptr<monero_tx_wallet>> output_txs;
    for (const std::shared_ptr<monero_output_wallet>& output : outputs) {
      std::shared_ptr<monero_tx_wallet> tx = std::static_pointer_cast<monero_tx_wallet>(output->m_tx);
      if (output_txs.find(tx) == output_txs.end()) {
        PyMoneroTxWallet::merge_tx(tx, tx_map, block_map);
        output_txs.insert(tx);
      }
    }
  }

  // restore transfer and output queries
  _query->m_transfer_query = transfer_query;
  _query->m_input_query = input_query;
  _query->m_output_query = output_query;

  // filter txs that don't meet transfer query
  std::vector<std::shared_ptr<monero_tx_wallet>> queried_txs;
  std::vector<std::shared_ptr<monero_tx_wallet>>::iterator tx_iter = txs.begin();
  while (tx_iter != txs.end()) {
    std::shared_ptr<monero_tx_wallet> tx = *tx_iter;
    if (_query->meets_criteria(tx.get())) {
      queried_txs.push_back(tx);
      ++tx_iter;
    } else {
      tx_map.erase(tx->m_hash.get());
      tx_iter = txs.erase(tx_iter);
      if (tx->m_block != boost::none) tx->m_block.get()->m_txs.erase(std::remove(tx->m_block.get()->m_txs.begin(), tx->m_block.get()->m_txs.end(), tx), tx->m_block.get()->m_txs.end()); // TODO, no way to use tx_iter?
    }
  }
  txs = queried_txs;

  // special case: re-fetch txs if inconsistency caused by needing to make multiple wallet calls
  // TODO monero-project: offer wallet.get_txs(...)
  for (const std::shared_ptr<monero_tx_wallet>& tx : txs) {
    if ((*tx->m_is_confirmed && tx->m_block == boost::none) || (!*tx->m_is_confirmed && tx->m_block != boost::none)) {
      std::cout << "WARNING: Inconsistency detected building txs from multiple wallet2 calls, re-fetching" << std::endl;
      monero_utils::free(txs);
      txs.clear();
      txs = get_txs(*_query);
      monero_utils::free(_query);
      return txs;
    }
  }

  // if tx hashes requested, order txs
  if (!_query->m_hashes.empty()) {
    txs.clear();
    for (const std::string& tx_hash : _query->m_hashes) {
      std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>::const_iterator tx_iter = tx_map.find(tx_hash);
      if (tx_iter != tx_map.end()) txs.push_back(tx_iter->second);
    }
  }

  // free query and return
  monero_utils::free(_query);
  return txs;
}

std::vector<std::shared_ptr<monero_transfer>> PyMoneroWalletRpc::get_transfers(const monero_transfer_query& query) const {
  // get transfers directly if query does not require tx context (e.g. other transfers, outputs)
  if (!PyMoneroTransferQuery::is_contextual(query)) return get_transfers_aux(query);

  // otherwise get txs with full models to fulfill query
  std::vector<std::shared_ptr<monero_transfer>> transfers;
  for (const std::shared_ptr<monero_tx_wallet>& tx : get_txs(*(query.m_tx_query.get()))) {
    for (const std::shared_ptr<monero_transfer>& transfer : tx->filter_transfers(query)) { // collect queried transfers, erase if excluded
      transfers.push_back(transfer);
    }
  }
  return transfers;
}

std::vector<std::shared_ptr<monero_output_wallet>> PyMoneroWalletRpc::get_outputs(const monero_output_query& query) const {
  // get outputs directly if query does not require tx context (e.g. other outputs, transfers)
  if (!PyMoneroOutputQuery::is_contextual(query)) return get_outputs_aux(query);

  // otherwise get txs with full models to fulfill query
  std::vector<std::shared_ptr<monero_output_wallet>> outputs;
  for (const std::shared_ptr<monero_tx_wallet>& tx : get_txs(*(query.m_tx_query.get()))) {
    for (const std::shared_ptr<monero_output_wallet>& output : tx->filter_outputs_wallet(query)) { // collect queried outputs, erase if excluded
      outputs.push_back(output);
    }
  }
  return outputs;
}

std::map<uint32_t, std::vector<uint32_t>> PyMoneroWalletRpc::get_account_indices(bool get_subaddr_indices) const {
  std::map<uint32_t, std::vector<uint32_t>> indices;
  for (const auto& account : monero::monero_wallet::get_accounts()) {
    uint32_t account_idx = account.m_index.get();
    if (get_subaddr_indices) {
      indices[account_idx] = get_subaddress_indices(account_idx);
    }
    else indices[account_idx] = std::vector<uint32_t>();
  }
  return indices;
}

std::vector<uint32_t> PyMoneroWalletRpc::get_subaddress_indices(uint32_t account_idx) const {
  // fetch subaddresses
  auto params = std::make_shared<PyMoneroGetAddressParams>(account_idx);
  auto node = m_rpc->send_json_request("get_address", params);
  std::vector<uint32_t> subadress_indices;
  // TODO refactory
  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("addresses")) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto subaddress = std::make_shared<monero::monero_subaddress>();
        PyMoneroSubaddress::from_rpc_property_tree(it2->second, subaddress);
        subadress_indices.push_back(subaddress->m_index.get());
      }
      break;
    }
  }
  return subadress_indices;
}

std::vector<std::shared_ptr<monero_transfer>> PyMoneroWalletRpc::get_transfers_aux(const monero_transfer_query& query) const {
  MTRACE("PyMoneroWalletRpc::get_transfers(query)");
//    // log query
//    if (query.m_tx_query != boost::none) {
//      if ((*query.m_tx_query)->m_block == boost::none) std::cout << "Transfer query's tx query rooted at [tx]:" << (*query.m_tx_query)->serialize() << std::endl;
//      else std::cout << "Transfer query's tx query rooted at [block]: " << (*(*query.m_tx_query)->m_block)->serialize() << std::endl;
//    } else std::cout << "Transfer query: " << query.serialize() << std::endl;

  // copy and normalize query
  std::shared_ptr<monero_transfer_query> _query;
  if (query.m_tx_query == boost::none) {
    std::shared_ptr<monero_transfer_query> query_ptr = std::make_shared<monero_transfer_query>(query); // convert to shared pointer for copy  // TODO: does this copy unecessarily? copy constructor is not defined
    _query = query_ptr->copy(query_ptr, std::make_shared<monero_transfer_query>());
    _query->m_tx_query = std::make_shared<monero_tx_query>();
    _query->m_tx_query.get()->m_transfer_query = _query;
  } else {
    std::shared_ptr<monero_tx_query> tx_query = query.m_tx_query.get()->copy(query.m_tx_query.get(), std::make_shared<monero_tx_query>());
    _query = tx_query->m_transfer_query.get();
  }
  std::shared_ptr<monero_tx_query> tx_query = _query->m_tx_query.get();

  boost::optional<uint32_t> account_index = boost::none;
  if (_query->m_account_index != boost::none) account_index = *_query->m_account_index;
  std::set<uint32_t> subaddress_indices;
  for (int i = 0; i < _query->m_subaddress_indices.size(); i++) {
    subaddress_indices.insert(_query->m_subaddress_indices[i]);
  }

  // translate from monero_tx_query to in, out, pending, pool, failed terminology used by monero-wallet-rpc
  bool can_be_confirmed = !bool_equals_2(false, tx_query->m_is_confirmed) && !bool_equals_2(true, tx_query->m_in_tx_pool) && !bool_equals_2(true, tx_query->m_is_failed) && !bool_equals_2(false, tx_query->m_is_relayed);
  bool can_be_in_tx_pool = !bool_equals_2(true, tx_query->m_is_confirmed) && !bool_equals_2(false, tx_query->m_in_tx_pool) && !bool_equals_2(true, tx_query->m_is_failed) && tx_query->get_height() == boost::none && tx_query->m_min_height == boost::none && !bool_equals_2(false, tx_query->m_is_locked);
  bool can_be_incoming = !bool_equals_2(false, _query->m_is_incoming) && !bool_equals_2(true, _query->is_outgoing()) && !bool_equals_2(true, _query->m_has_destinations);
  bool can_be_outgoing = !bool_equals_2(false, _query->is_outgoing()) && !bool_equals_2(true, _query->m_is_incoming);
  bool is_in = can_be_incoming && can_be_confirmed;
  bool is_out = can_be_outgoing && can_be_confirmed;
  bool is_pending = can_be_outgoing && can_be_in_tx_pool;
  bool is_pool = can_be_incoming && can_be_in_tx_pool;
  bool is_failed = !bool_equals_2(false, tx_query->m_is_failed) && !bool_equals_2(true, tx_query->m_is_confirmed) && !bool_equals_2(true, tx_query->m_in_tx_pool) && !bool_equals_2(false, tx_query->m_is_locked);

  // check if fetching pool txs contradicted by configuration
  if (tx_query->m_in_tx_pool != boost::none && tx_query->m_in_tx_pool.get() && !can_be_in_tx_pool) {
    monero_utils::free(tx_query);
    throw std::runtime_error("Cannot fetch pool transactions because it contradicts configuration");
  }

  // cache unique txs and blocks
  std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>> tx_map;
  std::unordered_map<uint64_t, std::shared_ptr<monero_block>> block_map;

  auto params = std::make_shared<PyMoneroGetTransfersParams>();
  params->m_in = is_in;
  params->m_out = is_out;
  params->m_pool = is_pool;
  params->m_pending = is_pending;
  params->m_failed = is_failed;
  params->m_max_height = tx_query->m_max_height;

  if (tx_query->m_min_height != boost::none) {
    uint64_t min_height = tx_query->m_min_height.get();
    // TODO monero-project: wallet2::get_payments() min_height is exclusive, so manually offset to match intended range (issues #5751, #5598)
    if (min_height > 0) params->m_min_height = min_height - 1;
    else params->m_min_height = min_height;
  }

  if (_query->m_account_index == boost::none) {
    if (_query->m_subaddress_index != boost::none || !_query->m_subaddress_indices.empty()) throw std::runtime_error("Filter specifies a subaddress index but not an account index");
    params->m_all_accounts = true;
  } else {
    params->m_account_index = _query->m_account_index;

    // set subaddress indices param
    params->m_subaddr_indices = _query->m_subaddress_indices;
    if (_query->m_subaddress_index != boost::none && std::find(_query->m_subaddress_indices.end(), _query->m_subaddress_indices.end(), _query->m_subaddress_index.get()) != _query->m_subaddress_indices.end()) {
      params->m_subaddr_indices.push_back(_query->m_subaddress_index.get());
    }
  }

  // build txs using `get_transfers`
  auto node = m_rpc->send_json_request("get_transfers", params);

  PyMoneroTxWallet::from_property_tree_with_transfer_and_merge(node, tx_map, block_map);

  // sort txs by block height
  std::vector<std::shared_ptr<monero_tx_wallet>> txs;
  for (std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>::const_iterator tx_iter = tx_map.begin(); tx_iter != tx_map.end(); tx_iter++) {
    txs.push_back(tx_iter->second);
  }
  sort(txs.begin(), txs.end(), tx_height_less_than);

  // filter transfers
  std::vector<std::shared_ptr<monero_transfer>> transfers;
  for (const std::shared_ptr<monero_tx_wallet>& tx : txs) {

    // tx is not incoming/outgoing unless already set
    if (tx->m_is_incoming == boost::none) tx->m_is_incoming = false;
    if (tx->m_is_outgoing == boost::none) tx->m_is_outgoing = false;

    // sort incoming transfers
    sort(tx->m_incoming_transfers.begin(), tx->m_incoming_transfers.end(), incoming_transfer_before);

    // collect queried transfers, erase if excluded
    for (const std::shared_ptr<monero_transfer>& transfer : tx->filter_transfers(*_query)) transfers.push_back(transfer);

    // remove excluded txs from block
    if (tx->m_block != boost::none && tx->m_outgoing_transfer == boost::none && tx->m_incoming_transfers.empty()) {
      tx->m_block.get()->m_txs.erase(std::remove(tx->m_block.get()->m_txs.begin(), tx->m_block.get()->m_txs.end(), tx), tx->m_block.get()->m_txs.end()); // TODO, no way to use const_iterator?
    }
  }
  MTRACE("PyMoneroWalletRpc::get_transfers() returning " << transfers.size() << " transfers");

  // free query and return transfers
  monero_utils::free(tx_query);
  return transfers;
}

std::vector<std::shared_ptr<monero_output_wallet>> PyMoneroWalletRpc::get_outputs_aux(const monero_output_query& query) const {
  MTRACE("PyMoneroWalletRpc::get_outputs_aux(query)");

//    // log query
//    if (query.m_tx_query != boost::none) {
//      if ((*query.m_tx_query)->m_block == boost::none) std::cout << "Output query's tx query rooted at [tx]:" << (*query.m_tx_query)->serialize() << std::endl;
//      else std::cout << "Output query's tx query rooted at [block]: " << (*(*query.m_tx_query)->m_block)->serialize() << std::endl;
//    } else std::cout << "Output query: " << query.serialize() << std::endl;

  // copy and normalize query
  std::shared_ptr<monero_output_query> _query;
  if (query.m_tx_query == boost::none) {
    std::shared_ptr<monero_output_query> query_ptr = std::make_shared<monero_output_query>(query); // convert to shared pointer for copy
    _query = query_ptr->copy(query_ptr, std::make_shared<monero_output_query>());
  } else {
    std::shared_ptr<monero_tx_query> tx_query = query.m_tx_query.get()->copy(query.m_tx_query.get(), std::make_shared<monero_tx_query>());
    if (query.m_tx_query.get()->m_output_query != boost::none && query.m_tx_query.get()->m_output_query.get().get() == &query) {
      _query = tx_query->m_output_query.get();
    } else {
      if (query.m_tx_query.get()->m_output_query != boost::none) throw std::runtime_error("Output query's tx query must be a circular reference or null");
      std::shared_ptr<monero_output_query> query_ptr = std::make_shared<monero_output_query>(query);  // convert query to shared pointer for copy
      _query = query_ptr->copy(query_ptr, std::make_shared<monero_output_query>());
      _query->m_tx_query = tx_query;
    }
  }
  if (_query->m_tx_query == boost::none) _query->m_tx_query = std::make_shared<monero_tx_query>();
  std::shared_ptr<monero_tx_query> tx_query = _query->m_tx_query.get();

  // determine account and subaddress indices to be queried
  std::map<uint32_t, std::vector<uint32_t>> indices;
  if (_query->m_account_index != boost::none) {
    std::vector<uint32_t> subaddress_indices;
    if (_query->m_subaddress_index != boost::none) {
      subaddress_indices.push_back(_query->m_subaddress_index.get());
    }
    for (const auto& subaddress_idx : _query->m_subaddress_indices) {
      subaddress_indices.push_back(subaddress_idx);
    }
    // null will fetch from all subaddresses
    indices[_query->m_account_index.get()] = subaddress_indices;
  }
  else {
    if (_query->m_subaddress_index != boost::none) throw std::runtime_error("Request specifies a subaddress index but not an account index");
    if (!_query->m_subaddress_indices.empty()) throw std::runtime_error("Request specifies subaddress indices but not an account index");
    // fetch all account indices without subaddresses
    indices = get_account_indices(false);
  }

  // cache unique txs and blocks
  std::unordered_map<std::string, std::shared_ptr<monero::monero_tx_wallet>> tx_map;
  std::unordered_map<uint64_t, std::shared_ptr<monero::monero_block>> block_map;

  // collect txs with outputs for each indicated account using `incoming_transfers` rpc call
  std::string transfer_type = "all";
  if (_query->m_is_spent != boost::none) {
    if (_query->m_is_spent.value() == true) transfer_type = "unavailable";
    else transfer_type = "available";
  }

  auto params = std::make_shared<PyMoneroGetIncomingTransfersParams>(transfer_type);

  for(const auto& kv : indices) {
    uint32_t account_idx = kv.first;
    params->m_account_index = account_idx;
    params->m_subaddr_indices = kv.second;
    // send request
    auto node = m_rpc->send_json_request("incoming_transfers", params);

    // convert response to txs with outputs and merge
    PyMoneroTxWallet::from_property_tree_with_output_and_merge(node, tx_map, block_map);
  }

  // sort txs by block height
  std::vector<std::shared_ptr<monero_tx_wallet>> txs ;
  for (std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>::const_iterator tx_iter = tx_map.begin(); tx_iter != tx_map.end(); tx_iter++) {
    txs.push_back(tx_iter->second);
  }
  sort(txs.begin(), txs.end(), tx_height_less_than);

  // filter and return outputs
  std::vector<std::shared_ptr<monero_output_wallet>> outputs;
  for (const std::shared_ptr<monero_tx_wallet>& tx : txs) {

    // sort outputs
    sort(tx->m_outputs.begin(), tx->m_outputs.end(), vout_before);

    // collect queried outputs, erase if excluded
    for (const std::shared_ptr<monero_output_wallet>& output : tx->filter_outputs_wallet(*_query)) outputs.push_back(output);

    // remove txs without outputs
    if (tx->m_outputs.empty() && tx->m_block != boost::none) tx->m_block.get()->m_txs.erase(std::remove(tx->m_block.get()->m_txs.begin(), tx->m_block.get()->m_txs.end(), tx), tx->m_block.get()->m_txs.end()); // TODO, no way to use const_iterator?
  }

  // free query and return outputs
  monero_utils::free(tx_query);
  return outputs;
}