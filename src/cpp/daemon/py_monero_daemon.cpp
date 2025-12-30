#include "py_monero_daemon.h"


void PyMoneroDaemonDefault::add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.push_back(listener);
  refresh_listening();
}

void PyMoneroDaemonDefault::remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<PyMoneroDaemonListener> iter){ return iter == listener; }), m_listeners.end());
  refresh_listening();
}

void PyMoneroDaemonDefault::remove_listeners() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.clear();
  refresh_listening();
}

std::optional<std::shared_ptr<monero::monero_tx>> PyMoneroDaemonDefault::get_tx(const std::string& tx_hash, bool prune) { 
  std::vector<std::string> hashes;
  hashes.push_back(tx_hash);
  auto txs = get_txs(hashes, prune);
  std::optional<std::shared_ptr<monero::monero_tx>> tx;

  if (txs.size() > 0) {
    tx = txs[0];
  }

  return tx;
}

void PyMoneroDaemonDefault::relay_tx_by_hash(std::string& tx_hash) { 
  std::vector<std::string> tx_hashes;
  tx_hashes.push_back(tx_hash);
  relay_txs_by_hash(tx_hashes);
}

PyMoneroKeyImageSpentStatus PyMoneroDaemonDefault::get_key_image_spent_status(std::string& key_image) { 
  std::vector<std::string> key_images;
  key_images.push_back(key_image);
  auto statuses = get_key_image_spent_statuses(key_images);
  if (statuses.empty()) throw std::runtime_error("Could not get key image spent status");
  return statuses[0];
}

std::optional<std::string> PyMoneroDaemonDefault::get_tx_hex(const std::string& tx_hash, bool prune) { 
  std::vector<std::string> hashes;
  hashes.push_back(tx_hash);
  auto hexes = get_tx_hexes(hashes, prune);
  std::optional<std::string> hex;
  if (hexes.size() > 0) {
    hex = hexes[0];
  }

  return hex;
}

void PyMoneroDaemonDefault::submit_block(const std::string& block_blob) { 
  std::vector<std::string> block_blobs;
  block_blobs.push_back(block_blob);
  return submit_blocks(block_blobs);
}

PyMoneroDaemonPoller::~PyMoneroDaemonPoller() {
  set_is_polling(false);
}

void PyMoneroDaemonPoller::set_is_polling(bool is_polling) {
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

void PyMoneroDaemonPoller::loop() {
  while (m_is_polling) {
    try {
      poll();
    } catch (const std::exception& e) {
      std::cout << "ERROR " << e.what() << std::endl;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(m_poll_period_ms));
  }
}

void PyMoneroDaemonPoller::poll() {
  if (!m_last_header) {
    m_last_header = m_daemon->get_last_block_header();
    return;
  }

  auto header = m_daemon->get_last_block_header();
  if (header->m_hash != m_last_header->m_hash) {
    m_last_header = header;
    announce_block_header(header);
  }
}

void PyMoneroDaemonPoller::announce_block_header(const std::shared_ptr<monero::monero_block_header>& header) {
  const auto& listeners = m_daemon->get_listeners();
  for (const auto& listener : listeners) {
    try {
      listener->on_block_header(header);

    } catch (const std::exception& e) {
      std::cout << "Error calling listener on new block header: " << e.what() << std::endl;
    }
  }
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroDaemonRpc::get_rpc_connection() const {
  return m_rpc;
}

bool PyMoneroDaemonRpc::is_connected() {
  try {
    get_version();
    return true;
  }
  catch (...) {
    return false;
  }
}

monero::monero_version PyMoneroDaemonRpc::get_version() { 
  PyMoneroJsonRequest request("get_version");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroVersion> info = std::make_shared<PyMoneroVersion>();
  PyMoneroVersion::from_property_tree(res, info);
  return *info;
}

bool PyMoneroDaemonRpc::is_trusted() {
  PyMoneroPathRequest request("get_height");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);

  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_response.get();
  auto _res = std::make_shared<PyMoneroGetHeightResponse>();
  PyMoneroGetHeightResponse::from_property_tree(res, _res);
  return !_res->m_untrusted.get();
}

uint64_t PyMoneroDaemonRpc::get_height() { 
  PyMoneroJsonRequest request("get_block_count");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroGetBlockCountResult> result = std::make_shared<PyMoneroGetBlockCountResult>();
  PyMoneroGetBlockCountResult::from_property_tree(res, result);

  if (result->m_count == boost::none) throw std::runtime_error("Could not get height");

  return result->m_count.get();
}

std::string PyMoneroDaemonRpc::get_block_hash(uint64_t height) { 
  std::shared_ptr<PyMoneroGetBlockHashParams> params = std::make_shared<PyMoneroGetBlockHashParams>(height);

  PyMoneroJsonRequest request("on_get_block_hash", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  return res.data();
}

std::shared_ptr<PyMoneroBlockTemplate> PyMoneroDaemonRpc::get_block_template(std::string& wallet_address, int reserve_size) {
  auto params = std::make_shared<PyMoneroGetBlockParams>(wallet_address, reserve_size);
  PyMoneroJsonRequest request("get_block_template", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroBlockTemplate> tmplt = std::make_shared<PyMoneroBlockTemplate>();
  PyMoneroBlockTemplate::from_property_tree(res, tmplt);
  return tmplt;
}

std::shared_ptr<PyMoneroBlockTemplate> PyMoneroDaemonRpc::get_block_template(std::string& wallet_address) {
  auto params = std::make_shared<PyMoneroGetBlockParams>(wallet_address);
  PyMoneroJsonRequest request("get_block_template", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroBlockTemplate> tmplt = std::make_shared<PyMoneroBlockTemplate>();
  PyMoneroBlockTemplate::from_property_tree(res, tmplt);
  return tmplt;
}

std::shared_ptr<monero::monero_block_header> PyMoneroDaemonRpc::get_last_block_header() {
  PyMoneroJsonRequest request("get_last_block_header");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
  PyMoneroBlockHeader::from_property_tree(res, header);
  return header;
}

std::shared_ptr<monero::monero_block_header> PyMoneroDaemonRpc::get_block_header_by_hash(const std::string& hash) {
  std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(hash);

  PyMoneroJsonRequest request("/get_block_header_by_hash", params);

  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
  PyMoneroBlockHeader::from_property_tree(res, header);
  return header;
}

std::shared_ptr<monero::monero_block_header> PyMoneroDaemonRpc::get_block_header_by_height(uint64_t height) {
  std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(height);

  PyMoneroJsonRequest request("/get_block_header_by_height", params);

  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
  PyMoneroBlockHeader::from_property_tree(res, header);
  return header;
}

std::vector<std::shared_ptr<monero::monero_block_header>> PyMoneroDaemonRpc::get_block_headers_by_range(uint64_t start_height, uint64_t end_height) { 
  auto params = std::make_shared<PyMoneroGetBlockRangeParams>();
  PyMoneroJsonRequest request("get_block_headers_range", params);

  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::vector<std::shared_ptr<monero::monero_block_header>> headers;
  PyMoneroBlockHeader::from_property_tree(res, headers);
  return headers;
}

std::shared_ptr<monero::monero_block> PyMoneroDaemonRpc::get_block_by_hash(const std::string& hash) {
  std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(hash);

  PyMoneroJsonRequest request("/get_block", params);

  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto block = std::make_shared<monero::monero_block>();
  PyMoneroBlock::from_property_tree(res, block);
  return block;
}

std::vector<std::shared_ptr<monero::monero_block>> PyMoneroDaemonRpc::get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) { 
  throw std::runtime_error("PyMoneroDaemonRpc::get_blocks_by_hash(): not implemented"); 
}

std::shared_ptr<monero::monero_block> PyMoneroDaemonRpc::get_block_by_height(uint64_t height) {
  std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(height);

  PyMoneroJsonRequest request("/get_block", params);

  auto response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto block = std::make_shared<monero::monero_block>();
  PyMoneroBlock::from_property_tree(res, block);
  return block;
}

std::vector<std::shared_ptr<monero::monero_block>> PyMoneroDaemonRpc::get_blocks_by_height(std::vector<uint64_t> heights) { 
  // TODO Binary Request
  throw std::runtime_error("PyMoneroDaemonRpc::get_blocks_by_height(): not implemented"); 
}

std::vector<std::shared_ptr<monero::monero_block>> PyMoneroDaemonRpc::get_blocks_by_range(std::optional<uint64_t> start_height, std::optional<uint64_t> end_height) {
  if (!start_height.has_value()) {
    start_height = 0;
  }
  if (!end_height.has_value()) {
    end_height = get_height() - 1;
  }
  
  std::vector<uint64_t> heights;
  for (uint64_t height = start_height.value(); height <= end_height.value(); height++) heights.push_back(height);

  return get_blocks_by_height(heights); 
}

std::vector<std::string> PyMoneroDaemonRpc::get_block_hashes(std::vector<std::string> block_hashes, uint64_t start_height) { 
  throw std::runtime_error("PyMoneroDaemonRpc::get_block_hashes(): not implemented"); 
}

std::vector<std::shared_ptr<monero::monero_tx>> PyMoneroDaemonRpc::get_txs(const std::vector<std::string>& tx_hashes, bool prune) { 
  if (tx_hashes.empty()) throw std::runtime_error("Must provide an array of transaction hashes"); 
  auto params = std::make_shared<PyMoneroGetTxsParams>(tx_hashes, prune);
  PyMoneroPathRequest request("get_transactions", params);
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto res = response->m_response.get();
  std::vector<std::shared_ptr<monero::monero_tx>> txs;
  PyMoneroTx::from_property_tree(res, txs);
  return txs;
}

std::vector<std::string> PyMoneroDaemonRpc::get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune) { 
  throw std::runtime_error("PyMoneroDaemon: not implemented"); 
}

std::shared_ptr<PyMoneroMinerTxSum> PyMoneroDaemonRpc::get_miner_tx_sum(uint64_t height, uint64_t num_blocks) {
  auto params = std::make_shared<PyMoneroGetMinerTxSumParams>();
  PyMoneroJsonRequest request("get_coinbase_tx_sum", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto sum = std::make_shared<PyMoneroMinerTxSum>();
  PyMoneroMinerTxSum::from_property_tree(res, sum);
  return sum;
}

std::shared_ptr<PyMoneroFeeEstimate> PyMoneroDaemonRpc::get_fee_estimate(uint64_t grace_blocks) { 
  auto params = std::make_shared<PyMoneroGetFeeEstimateParams>(grace_blocks);
  PyMoneroJsonRequest request("get_fee_estimate", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  auto estimate = std::make_shared<PyMoneroFeeEstimate>();
  PyMoneroFeeEstimate::from_property_tree(res, estimate);
  return estimate;
}

std::shared_ptr<PyMoneroSubmitTxResult> PyMoneroDaemonRpc::submit_tx_hex(std::string& tx_hex, bool do_not_relay) { 
  auto params = std::make_shared<PyMoneroSubmitTxParams>(tx_hex, do_not_relay);
  PyMoneroPathRequest request("send_raw_transaction", params);
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_response.get();
  auto sum = std::make_shared<PyMoneroSubmitTxResult>();
  PyMoneroSubmitTxResult::from_property_tree(res, sum);
  return sum;
}

void PyMoneroDaemonRpc::relay_txs_by_hash(std::vector<std::string>& tx_hashes) { 
  auto params = std::make_shared<PyMoneroRelayTxParams>(tx_hashes);
  PyMoneroJsonRequest request("relay_tx", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  check_response_status(response);
}

std::shared_ptr<PyMoneroTxPoolStats> PyMoneroDaemonRpc::get_tx_pool_stats() { 
  PyMoneroPathRequest request("get_transaction_pool_stats");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_response.get();
  auto stats = std::make_shared<PyMoneroTxPoolStats>();
  PyMoneroTxPoolStats::from_property_tree(res, stats);
  return stats;
}

std::vector<std::shared_ptr<monero::monero_tx>> PyMoneroDaemonRpc::get_tx_pool() {
  PyMoneroPathRequest request("get_transaction_pool");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_response.get();
  std::vector<std::shared_ptr<monero::monero_tx>> pool;
  PyMoneroTx::from_property_tree(res, pool);
  return pool;
}

std::vector<std::string> PyMoneroDaemonRpc::get_tx_pool_hashes() {
  PyMoneroPathRequest request("get_transaction_pool_hashes");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero RPC response");
  auto res = response->m_response.get();
  return PyMoneroTxHashes::from_property_tree(res);
}

void PyMoneroDaemonRpc::flush_tx_pool(const std::vector<std::string> &hashes) {
  auto params = std::make_shared<PyMoneroRelayTxParams>(hashes);
  PyMoneroJsonRequest request("flush_txpool", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  check_response_status(response);
}

void PyMoneroDaemonRpc::flush_tx_pool() { 
  std::vector<std::string> hashes;
  flush_tx_pool(hashes);
}

void PyMoneroDaemonRpc::flush_tx_pool(const std::string &hash) { 
  std::vector<std::string> hashes;
  hashes.push_back(hash);
  flush_tx_pool(hashes);
}

std::vector<PyMoneroKeyImageSpentStatus> PyMoneroDaemonRpc::get_key_image_spent_statuses(std::vector<std::string>& key_images) { 
  if (key_images.empty()) throw std::runtime_error("Must provide key images to check the status of"); 
  auto params = std::make_shared<PyMoneroIsKeyImageSpentParams>(key_images);
  PyMoneroPathRequest request("is_key_image_spent", params);
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto res = response->m_response.get();
  std::vector<PyMoneroKeyImageSpentStatus> statuses;
  for (auto it = res.begin(); it != res.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("spent_status")) {
      auto spent_status_node = it->second;
      for (auto it2 = spent_status_node.begin(); it2 != spent_status_node.end(); ++it2) {
        auto value = it2->second.get_value<uint8_t>();
        if (value == 0) {
          statuses.push_back(PyMoneroKeyImageSpentStatus::NOT_SPENT);
        }
        else if (value == 1) {
          statuses.push_back(PyMoneroKeyImageSpentStatus::CONFIRMED);
        }
        else if (value == 2) {
          statuses.push_back(PyMoneroKeyImageSpentStatus::TX_POOL);
        }
      }
    }
  }
  return statuses;
}

std::vector<std::shared_ptr<monero::monero_output>> PyMoneroDaemonRpc::get_outputs(std::vector<monero::monero_output>& outputs) { 
  throw std::runtime_error("PyMoneroDaemonRpc::get_outputs(): not implemented"); 
}

std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> PyMoneroDaemonRpc::get_output_histogram(std::vector<uint64_t> amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) { 
  auto params = std::make_shared<PyMoneroGetOutputHistrogramParams>(amounts, min_count, max_count, is_unlocked, recent_cutoff);
  PyMoneroJsonRequest request("get_output_histogram", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> entries;
  PyMoneroOutputHistogramEntry::from_property_tree(res, entries);
  return entries;
}

std::shared_ptr<PyMoneroDaemonInfo> PyMoneroDaemonRpc::get_info() { 
  PyMoneroJsonRequest request("get_info");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();
  std::shared_ptr<PyMoneroDaemonInfo> info = std::make_shared<PyMoneroDaemonInfo>();
  PyMoneroDaemonInfo::from_property_tree(res, info);
  return info;
}

std::shared_ptr<PyMoneroDaemonSyncInfo> PyMoneroDaemonRpc::get_sync_info() {
  PyMoneroJsonRequest request("get_sync_info");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroDaemonSyncInfo> info = std::make_shared<PyMoneroDaemonSyncInfo>();
  PyMoneroDaemonSyncInfo::from_property_tree(res, info);
  return info;
}

std::shared_ptr<PyMoneroHardForkInfo> PyMoneroDaemonRpc::get_hard_fork_info() {
  PyMoneroJsonRequest request("hard_fork_info");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroHardForkInfo> info = std::make_shared<PyMoneroHardForkInfo>();
  PyMoneroHardForkInfo::from_property_tree(res, info);
  return info;
}

std::vector<std::shared_ptr<PyMoneroAltChain>> PyMoneroDaemonRpc::get_alt_chains() { 
  std::vector<std::shared_ptr<PyMoneroAltChain>> result;
  
  PyMoneroJsonRequest request("/get_alternate_chains");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  for (boost::property_tree::ptree::const_iterator it = res.begin(); it != res.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("chains")) {
      boost::property_tree::ptree chains = it->second;
      for (boost::property_tree::ptree::const_iterator it2 = chains.begin(); it2 != chains.end(); ++it2) {
        std::shared_ptr<PyMoneroAltChain> alt_chain = std::make_shared<PyMoneroAltChain>();
        PyMoneroAltChain::from_property_tree(it2->second, alt_chain);
        result.push_back(alt_chain);
      }
    }
  }

  return result;
}

std::vector<std::string> PyMoneroDaemonRpc::get_alt_block_hashes() {
  PyMoneroPathRequest request("get_alt_blocks_hashes");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_response.get();
  std::vector<std::string> hashes;
  PyMoneroGetAltBlocksHashesResponse::from_property_tree(res, hashes);
  return hashes;
}

int PyMoneroDaemonRpc::get_download_limit() { 
  auto limits = get_bandwidth_limits();
  if (limits->m_down != boost::none) return limits->m_down.get();
  throw std::runtime_error("Could not get download limit");
}

int PyMoneroDaemonRpc::set_download_limit(int limit) {
  auto res = set_bandwidth_limits(0, limit);
  if (res->m_down != boost::none) return res->m_down.get();
  throw std::runtime_error("Could not set download limit");
}

int PyMoneroDaemonRpc::reset_download_limit() {
  auto res = set_bandwidth_limits(0, -1);
  if (res->m_down != boost::none) return res->m_down.get();
  throw std::runtime_error("Could not set download limit");
}

int PyMoneroDaemonRpc::get_upload_limit() { 
  auto limits = get_bandwidth_limits();
  if (limits->m_up != boost::none) return limits->m_up.get();
  throw std::runtime_error("Could not get upload limit");
}

int PyMoneroDaemonRpc::set_upload_limit(int limit) {
  auto res = set_bandwidth_limits(limit, 0);
  if (res->m_up != boost::none) return res->m_up.get();
  throw std::runtime_error("Could not set download limit");
}

int PyMoneroDaemonRpc::reset_upload_limit() {
  auto res = set_bandwidth_limits(-1, 0);
  if (res->m_up != boost::none) return res->m_up.get();
  throw std::runtime_error("Could not set download limit");
}

std::vector<std::shared_ptr<PyMoneroPeer>> PyMoneroDaemonRpc::get_peers() { 
  PyMoneroJsonRequest request("get_connections");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::vector<std::shared_ptr<PyMoneroPeer>> peers;
  PyMoneroPeer::from_property_tree(res, peers);
  return peers;
}

std::vector<std::shared_ptr<PyMoneroPeer>> PyMoneroDaemonRpc::get_known_peers() { 
  PyMoneroPathRequest request("get_peer_list");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);

  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_response.get();

  std::vector<std::shared_ptr<PyMoneroPeer>> peers;
  PyMoneroPeer::from_property_tree(res, peers);
  return peers;
}

void PyMoneroDaemonRpc::set_outgoing_peer_limit(int limit) {
  if (limit < 0) throw std::runtime_error("Outgoing peer limit must be >= 0");
  auto params = std::make_shared<PyMoneroPeerLimits>();
  params->m_out_peers = limit;
  PyMoneroPathRequest request("out_peers", params);
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  check_response_status(response);
}

void PyMoneroDaemonRpc::set_incoming_peer_limit(int limit) { 
  if (limit < 0) throw std::runtime_error("Incoming peer limit must be >= 0");
  auto params = std::make_shared<PyMoneroPeerLimits>();
  params->m_in_peers = limit;
  PyMoneroPathRequest request("in_peers", params);
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  check_response_status(response);
}

std::vector<std::shared_ptr<PyMoneroBan>> PyMoneroDaemonRpc::get_peer_bans() {
  PyMoneroJsonRequest request("get_bans");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::vector<std::shared_ptr<PyMoneroBan>> bans;
  PyMoneroBan::from_property_tree(res, bans);
  return bans;
}

void PyMoneroDaemonRpc::set_peer_bans(std::vector<std::shared_ptr<PyMoneroBan>> bans) {
  auto params = std::make_shared<PyMoneroSetBansParams>(bans);
  PyMoneroJsonRequest request("set_bans");
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  check_response_status(response);
}

void PyMoneroDaemonRpc::start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) { 
  if (address.empty()) throw std::runtime_error("Must provide address to mine to");
  if (num_threads <= 0) throw std::runtime_error("Number of threads must be an integer greater than 0");
  auto params = std::make_shared<PyMoneroStartMiningParams>(address, num_threads, is_background, ignore_battery);
  PyMoneroPathRequest request("start_mining", params);
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
}

void PyMoneroDaemonRpc::stop_mining() { 
  PyMoneroPathRequest request("stop_mining");
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
}

std::shared_ptr<PyMoneroMiningStatus> PyMoneroDaemonRpc::get_mining_status() { 
  PyMoneroPathRequest request("mining_status");
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto result = std::make_shared<PyMoneroMiningStatus>();
  auto res = response->m_response.get();
  PyMoneroMiningStatus::from_property_tree(res, result);
  return result;
}

void PyMoneroDaemonRpc::submit_blocks(const std::vector<std::string>& block_blobs) { 
  if (block_blobs.empty()) throw std::runtime_error("Must provide an array of mined block blobs to submit");
  auto params = std::make_shared<PyMoneroSubmitBlocksParams>(block_blobs);
  PyMoneroJsonRequest request("submit_block", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  check_response_status(response);
}

std::shared_ptr<PyMoneroPruneResult> PyMoneroDaemonRpc::prune_blockchain(bool check) { 
  auto params = std::make_shared<PyMoneroPruneBlockchainParams>(check);
  PyMoneroJsonRequest request("prune_blockchain", params);
  std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  auto res = response->m_result.get();

  std::shared_ptr<PyMoneroPruneResult> result = std::make_shared<PyMoneroPruneResult>();
  PyMoneroPruneResult::from_property_tree(res, result);
  return result;
}

std::shared_ptr<PyMoneroDaemonUpdateCheckResult> PyMoneroDaemonRpc::check_for_update() { 
  auto params = std::make_shared<PyMoneroCheckUpdateParams>();
  PyMoneroPathRequest request("update", params);
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto result = std::make_shared<PyMoneroDaemonUpdateCheckResult>();
  auto res = response->m_response.get();
  PyMoneroDaemonUpdateCheckResult::from_property_tree(res, result);
  return result;
}

std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> PyMoneroDaemonRpc::download_update(const std::string& path) { 
  auto params = std::make_shared<PyMoneroDownloadUpdateParams>(path);
  PyMoneroPathRequest request("update", params);
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto result = std::make_shared<PyMoneroDaemonUpdateDownloadResult>();
  auto res = response->m_response.get();
  PyMoneroDaemonUpdateDownloadResult::from_property_tree(res, result);
  return result;
}

std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> PyMoneroDaemonRpc::download_update() { 
  auto params = std::make_shared<PyMoneroDownloadUpdateParams>();
  PyMoneroPathRequest request("update", params);
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto result = std::make_shared<PyMoneroDaemonUpdateDownloadResult>();
  auto res = response->m_response.get();
  PyMoneroDaemonUpdateDownloadResult::from_property_tree(res, result);
  return result;
}

void PyMoneroDaemonRpc::stop() {
  PyMoneroPathRequest request("stop_daemon");
  std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
  check_response_status(response);
}

void PyMoneroDaemonRpc::stop_process() {
  if (m_child_process && m_child_process->running()) {
    m_child_process->terminate();
  }
  if (m_output_thread.joinable()) {
    m_output_thread.join();
  }
}

std::shared_ptr<monero::monero_block_header> PyMoneroDaemonRpc::wait_for_next_block_header() {
  // use mutex and condition variable to wait for block
  boost::mutex temp;
  boost::condition_variable cv;

  // create listener which notifies condition variable when block is added
  auto block_listener = std::make_shared<PyMoneroBlockNotifier>(&temp, &cv);

  // register the listener
  add_listener(block_listener);

  // wait until condition variable is notified
  boost::mutex::scoped_lock lock(temp);
  cv.wait(lock);

  // unregister the listener
  remove_listener(block_listener);

  // return last height
  return block_listener->m_last_header;
}

std::shared_ptr<PyMoneroBandwithLimits> PyMoneroDaemonRpc::get_bandwidth_limits() {
  PyMoneroPathRequest request("get_limit");
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto res = response->m_response.get();
  auto limits = std::make_shared<PyMoneroBandwithLimits>();
  PyMoneroBandwithLimits::from_property_tree(res, limits);
  return limits;
}

std::shared_ptr<PyMoneroBandwithLimits> PyMoneroDaemonRpc::set_bandwidth_limits(int up, int down) {
  auto limits = std::make_shared<PyMoneroBandwithLimits>(up, down);
  PyMoneroPathRequest request("set_limit", limits);
  auto response = m_rpc->send_path_request(request);
  check_response_status(response);
  auto res = response->m_response.get();
  PyMoneroBandwithLimits::from_property_tree(res, limits);
  return limits;
}

void PyMoneroDaemonRpc::refresh_listening() {
  if (!m_poller && m_listeners.size() > 0) {
    m_poller = std::make_shared<PyMoneroDaemonPoller>(this);
  }
  if (m_poller) m_poller->set_is_polling(m_listeners.size() > 0);
}

void PyMoneroDaemonRpc::check_response_status(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("status")) {
      auto status = it->second.data();

      if (status == std::string("OK")) {
        return;
      }
      else throw std::runtime_error(status);
    }
  }

  throw std::runtime_error("Could not get JSON RPC response status");
}

void PyMoneroDaemonRpc::check_response_status(std::shared_ptr<PyMoneroPathResponse> response) {
  if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero RPC response");
  auto node = response->m_response.get();
  check_response_status(node);
}

void PyMoneroDaemonRpc::check_response_status(std::shared_ptr<PyMoneroJsonResponse> response) {
  if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSON RPC response");
  auto node = response->m_result.get();
  check_response_status(node);
}

PyMoneroDaemonRpc::PyMoneroDaemonRpc(const std::vector<std::string>& cmd) {
  if (cmd.empty()) throw PyMoneroError("Must provide at least a path to monerod");
  boost::process::environment env = boost::this_process::environment();
  env["LANG"] = "en_US.UTF-8";

  m_child_process = std::make_unique<boost::process::child>(
    boost::process::exe = cmd[0],
    boost::process::args = std::vector<std::string>(cmd.begin() + 1, cmd.end()),
    boost::process::std_out > m_out_pipe,
    boost::process::std_err > m_err_pipe,
    env
  );

  std::istream& out_stream = m_out_pipe;
  std::istream& err_straem = m_err_pipe;
  std::ostringstream captured_output;
  std::string line;
  std::string uri_;
  std::string username_;
  std::string password_;
  std::string zmq_uri_;
  bool started = false;

  while (std::getline(out_stream, line)) {
    std::cerr << "[monero-rpc] " << line << std::endl;
    captured_output << line << "\n";

    std::string uri;
    std::regex re("Binding on ([0-9.]+).*:(\\d+)");
    std::smatch match;
    if (std::regex_search(line, match, re) && match.size() >= 3) {
      std::string host = match[1];
      std::string port = match[2];
      bool ssl = false;

      auto it = std::find(cmd.begin(), cmd.end(), "--rpc-ssl");
      if (it != cmd.end() && it + 1 != cmd.end()) {
        ssl = (it[1] == "enabled");
      }

      uri_ = (ssl ? "https://" : "http://") + host + ":" + port;
    }

    if (line.find("Starting p2p net loop") != std::string::npos) {
      m_output_thread = std::thread([this]() {
        std::istream& out_stream_bg = m_out_pipe;
        std::string line_bg;
        while (std::getline(out_stream_bg, line_bg)) {
          std::cerr << "[monero-rpc] " << line_bg << std::endl;
        }
      });
      started = true;
      break;
    }
  }

  if (!started) {
    if (std::getline(err_straem, line)) {
      captured_output << line << "\n";
    }
    
    throw PyMoneroError("Failed to start monerod:\n" + captured_output.str());
  }

  auto it = std::find(cmd.begin(), cmd.end(), "--rpc-login");
  if (it != cmd.end() && it + 1 != cmd.end()) {
    std::string login = *(it + 1);
    auto sep = login.find(':');
    if (sep != std::string::npos) {
      username_ = login.substr(0, sep);
      password_ = login.substr(sep + 1);
    }
  }

  it = std::find(cmd.begin(), cmd.end(), "--zmq-pub");
  if (it != cmd.end() && it + 1 != cmd.end()) {
    zmq_uri_ = *(it + 1);
  }

  m_rpc = std::make_shared<PyMoneroRpcConnection>(uri_, username_, password_, zmq_uri_);
  if (!m_rpc->m_uri->empty()) m_rpc->check_connection();
}

PyMoneroDaemonRpc::~PyMoneroDaemonRpc() {
  stop_process();
}
