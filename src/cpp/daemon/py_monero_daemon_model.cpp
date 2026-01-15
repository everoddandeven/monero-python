#include "py_monero_daemon_model.h"


std::string PyMoneroBinaryRequest::to_binary_val() const {
  auto json_val = serialize();
  std::string binary_val;
  monero_utils::json_to_binary(json_val, binary_val);
  return binary_val;
}

std::string PyMoneroRequestParams::serialize() const {
  if (m_py_params == boost::none) return PySerializableStruct::serialize();
  auto node = PyGenUtils::pyobject_to_ptree(m_py_params.get());
  return monero_utils::serialize(node);
}

std::optional<py::object> PyMoneroJsonResponse::get_result() const {
  std::optional<py::object> res;
  if (m_result != boost::none) res = PyGenUtils::ptree_to_pyobject(m_result.get());
  return res;
}

std::shared_ptr<PyMoneroJsonResponse> PyMoneroJsonResponse::deserialize(const std::string& response_json) {
  // deserialize json to property node
  std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
  boost::property_tree::ptree node;
  boost::property_tree::read_json(iss, node);

  auto response = std::make_shared<PyMoneroJsonResponse>();

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("error")) {
      std::string err_message = "Unknown error";
      int err_code = -1;
      for (auto it_err = it->second.begin(); it_err != it->second.end(); ++it_err) {
        std::string key_err = it_err->first;
        if (key_err == std::string("message")) {
          err_message = it_err->second.data();
        }
        else if (key_err == std::string("code")) {
          err_code = it_err->second.get_value<int>();
        }
      }

      throw PyMoneroRpcError(err_code, err_message);
    }
    else if (key == std::string("jsonrpc")) {
      response->m_jsonrpc = it->second.data();
    }
    else if (key == std::string("id")) {
      response->m_id = it->second.data();
    }
    else if (key == std::string("result")) {
      response->m_result = it->second;   
    }
    else std::cout << std::string("WARNING MoneroJsonResponse::deserialize() unrecognized key: ") << key << std::endl;
  }

  return response;
}

std::optional<py::object> PyMoneroPathResponse::get_response() const {
  std::optional<py::object> res;
  if (m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(m_response.get());
  return res;
}

std::shared_ptr<PyMoneroPathResponse> PyMoneroPathResponse::deserialize(const std::string& response_json) {
  // deserialize json to property node
  std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
  boost::property_tree::ptree node;
  boost::property_tree::read_json(iss, node);
  auto response = std::make_shared<PyMoneroPathResponse>();
  response->m_response = node;
  return response;
}

std::shared_ptr<PyMoneroBinaryResponse> PyMoneroBinaryResponse::deserialize(const std::string& response_binary) {
  auto response = std::make_shared<PyMoneroBinaryResponse>();
  response->m_binary = response_binary;
  return response;
}

std::optional<py::object> PyMoneroBinaryResponse::get_response() const {
  std::optional<py::object> res;
  if (m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(m_response.get());
  return res;
}

int PyMoneroRpcConnection::compare(std::shared_ptr<PyMoneroRpcConnection> c1, std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection) {
  // current connection is first
  if (c1 == current_connection) return -1;
  if (c2 == current_connection) return 1;
  
  // order by availability then priority then by name
  if (c1->is_online() == c2->is_online()) {
    if (c1->m_priority == c2->m_priority) {
      if (c1->m_uri == c2->m_uri) return 1;
      else return -1;
    }
    return PyMoneroConnectionPriorityComparator::compare(c1->m_priority, c2->m_priority) * -1; // order by priority in descending order
  } else {
    if (c1->is_online()) return -1;
    else if (c2->is_online()) return 1;
    else if (!c1->is_online()) return -1;
    else return 1; // c1 is offline
  }
}

bool PyMoneroRpcConnection::is_onion() const {
  if (m_uri == boost::none) return false;
  if (m_uri && m_uri->size() >= 6 && m_uri->compare(m_uri->size() - 6, 6, ".onion") == 0) {
    return true;
  }
  return false;
}

bool PyMoneroRpcConnection::is_i2p() const {
  if (m_uri == boost::none) return false;
  if (m_uri && m_uri->size() >= 8 && m_uri->compare(m_uri->size() - 8, 8, ".b32.i2p") == 0) {
    return true;
  }
  return false;
}

void PyMoneroRpcConnection::set_credentials(const std::string& username, const std::string& password) {
  if (m_http_client != nullptr) {
    if (m_http_client->is_connected()) {
      m_http_client->disconnect();
    }
  }
  else {
    auto factory = new net::http::client_factory();
    m_http_client = factory->create();
  }

  if (username.empty()) {
    m_username = boost::none;
  }

  if (password.empty()) {
    m_password = boost::none;
  }

  if (!password.empty() || !username.empty()) {
    if (password.empty()) {
      throw PyMoneroError("username cannot be empty because password is not empty");
    }

    if (username.empty()) {
      throw PyMoneroError("password cannot be empty because username is not empty");
    }
  }

  if (m_username != username || m_password != password) {
    m_is_online = boost::none;
    m_is_authenticated = boost::none;
  }

  m_username = username;
  m_password = password;
}

void PyMoneroRpcConnection::set_attribute(const std::string& key, const std::string& val) {
  m_attributes[key] = val;
}

std::string PyMoneroRpcConnection::get_attribute(const std::string& key) {
  std::unordered_map<std::string, std::string>::const_iterator i = m_attributes.find(key);
  if (i == m_attributes.end())
    return std::string("");
  return i->second;
}

bool PyMoneroRpcConnection::is_online() const {
  return m_is_online.value_or(false);
}

bool PyMoneroRpcConnection::is_authenticated() const {
  return m_is_authenticated.value_or(false);
}

bool PyMoneroRpcConnection::is_connected() const {
  if (!is_online()) return false;
  if (m_is_authenticated != boost::none) {
    return is_authenticated();
  }
  return true;
}

bool PyMoneroRpcConnection::check_connection(int timeout_ms) {
  boost::optional<bool> is_online_before = m_is_online;
  boost::optional<bool> is_authenticated_before = m_is_authenticated;
  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  try {
    if (!m_http_client) throw std::runtime_error("http client not set");
    if (m_http_client->is_connected()) {
      m_http_client->disconnect();
    }

    if (m_proxy_uri != boost::none) {
      if(!m_http_client->set_proxy(m_proxy_uri.get())) {
        throw std::runtime_error("Could not set proxy");
      }
    }

    if(m_username != boost::none && !m_username->empty() && m_password != boost::none && !m_password->empty()) {
      auto credentials = std::make_shared<epee::net_utils::http::login>();

      credentials->username = *m_username;
      credentials->password = *m_password;
  
      m_credentials = *credentials;
    }
    
    if (!m_http_client->set_server(m_uri.get(), m_credentials)) {
      throw std::runtime_error("Could not set rpc connection: " + m_uri.get());
    }

    m_http_client->connect(std::chrono::milliseconds(timeout_ms));
    auto start = std::chrono::high_resolution_clock::now();
    PyMoneroJsonRequest request("get_version");
    auto response = send_json_request(request);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    if (response->m_result == boost::none) {
      throw PyMoneroRpcError(-1, "Invalid JSON RPC response");
    }

    m_is_online = true;
    m_is_authenticated = true;
    m_response_time = duration.count();

    return is_online_before != m_is_online || is_authenticated_before != m_is_authenticated;
  }
  catch (const PyMoneroRpcError& ex) {
    m_is_online = false;
    m_is_authenticated = boost::none;
    m_response_time = boost::none;

    if (ex.code == 401) {
      m_is_online = true;
      m_is_authenticated = false;
    }
    else if (ex.code == 404) {
      m_is_online = true;
      m_is_authenticated = true;
    }

    return false;
  }
  catch (const std::exception& ex) {
    m_is_online = false;
    m_is_authenticated = boost::none;
    m_response_time = boost::none;
    return false;
  }
}

void PyMoneroBlockHeader::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block_header>& header) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("block_header")) {
      PyMoneroBlockHeader::from_property_tree(it->second, header);
      return;
    }
    else if (key == std::string("hash")) header->m_hash = it->second.data();
    else if (key == std::string("height")) header->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("timestamp")) header->m_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("block_size")) header->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("block_weight")) header->m_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("long_term_weight")) header->m_long_term_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("depth")) header->m_depth = it->second.get_value<uint64_t>();
    else if (key == std::string("difficulty")) header->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("cumulative_difficulty")) header->m_cumulative_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("major_version")) header->m_major_version = it->second.get_value<uint32_t>();
    else if (key == std::string("minor_version")) header->m_minor_version = it->second.get_value<uint32_t>();
    else if (key == std::string("nonce")) header->m_nonce = it->second.get_value<uint32_t>();
    else if (key == std::string("miner_tx_hash")) header->m_miner_tx_hash = it->second.data();
    else if (key == std::string("num_txes")) header->m_num_txs = it->second.get_value<uint32_t>();
    else if (key == std::string("orphan_status")) header->m_orphan_status = it->second.get_value<bool>();
    else if (key == std::string("prev_hash") || key == std::string("prev_id")) header->m_prev_hash = it->second.data();
    else if (key == std::string("reward")) header->m_reward = it->second.get_value<uint64_t>();
    else if (key == std::string("pow_hash")) {
      std::string pow_hash = it->second.data();
      if (!pow_hash.empty()) header->m_pow_hash = pow_hash;
    }
  }
}

void PyMoneroBlockHeader::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_block_header>>& headers) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("headers")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto header = std::make_shared<monero::monero_block_header>();
        PyMoneroBlockHeader::from_property_tree(it2->second, header);
        headers.push_back(header);
      }
    }
  }
}

void PyMoneroBlock::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block>& block) {
  PyMoneroBlockHeader::from_property_tree(node, block);

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("blob")) block->m_hex = it->second.data();
    else if (key == std::string("tx_hashes")) {
      for(const auto &hex : it->second) block->m_tx_hashes.push_back(hex.second.data());
    }
    else if (key == std::string("txs")) {
      for (const auto &tx_node : it->second) {
        auto tx = std::make_shared<monero::monero_tx>();
        PyMoneroTx::from_property_tree(tx_node.second, tx);
        block->m_txs.push_back(tx);
      }
    }
    else if (key == std::string("miner_tx")) {
      auto tx = std::make_shared<monero::monero_tx>();
      PyMoneroTx::from_property_tree(it->second, tx);
      tx->m_is_miner_tx = true;
      block->m_miner_tx = tx;
    }
    else if (key == std::string("json")) {
      auto json = it->second.data();
      std::istringstream iss = json.empty() ? std::istringstream() : std::istringstream(json);
      boost::property_tree::ptree json_node;
      boost::property_tree::read_json(iss, json_node);
      PyMoneroBlock::from_property_tree(json_node, block);
    }
  }
}

void PyMoneroBlock::from_property_tree(const boost::property_tree::ptree& node, const std::vector<uint64_t>& heights, std::vector<std::shared_ptr<monero::monero_block>>& blocks) {
  const auto& rpc_blocks = node.get_child("blocks");
  const auto& rpc_txs    = node.get_child("txs");
  if (rpc_blocks.size() != rpc_txs.size()) {
    throw std::runtime_error("blocks and txs size mismatch");
  }

  auto it_block = rpc_blocks.begin();
  auto it_txs   = rpc_txs.begin();
  size_t idx = 0;

  for (; it_block != rpc_blocks.end(); ++it_block, ++it_txs, ++idx) {
    // build block
    auto block = std::make_shared<monero::monero_block>();
    boost::property_tree::ptree block_n;
    std::istringstream block_iis = std::istringstream(it_block->second.get_value<std::string>());
    boost::property_tree::read_json(block_iis, block_n);
    PyMoneroBlock::from_property_tree(block_n, block);
    block->m_height = heights.at(idx);
    blocks.push_back(block);
    std::vector<std::string> tx_hashes;
    if (auto hashes = it_block->second.get_child_optional("tx_hashes")) {
      for (const auto& h : *hashes) tx_hashes.push_back(h.second.get_value<std::string>());
    }

    // build transactions
    std::vector<std::shared_ptr<monero::monero_tx>> txs;
    size_t tx_idx = 0;
    for (const auto& tx_node : it_txs->second) {
      auto tx = std::make_shared<monero::monero_tx>();
      tx->m_hash = tx_hashes.at(tx_idx++);
      tx->m_is_confirmed = true;
      tx->m_in_tx_pool = false;
      tx->m_is_miner_tx = false;
      tx->m_relay = true;
      tx->m_is_relayed = true;
      tx->m_is_failed = false;
      tx->m_is_double_spend_seen = false;
      boost::property_tree::ptree tx_n;
      std::istringstream tx_iis = std::istringstream(tx_node.second.get_value<std::string>());
      boost::property_tree::read_json(tx_iis, tx_n);
      PyMoneroTx::from_property_tree(tx_n, tx);
      txs.push_back(tx);
    }

    // merge into one block
    block->m_txs.clear();
    for (auto& tx : txs) {
      if (tx->m_block != boost::none) block->merge(block, tx->m_block.get());
      else {
        tx->m_block = block;
        block->m_txs.push_back(tx);
      }
    }
  }
}

void PyMoneroOutput::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output>& output) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("gen")) throw std::runtime_error("Output with 'gen' from daemon rpc is miner tx which we ignore (i.e. each miner input is null)");
    else if (key == std::string("key")) {
      auto key_node = it->second;
      for (auto it2 = key_node.begin(); it2 != key_node.end(); ++it2) {
        std::string key_key = it2->first;

        if (key_key == std::string("amount")) output->m_amount = it2->second.get_value<uint64_t>();
        else if (key_key == std::string("k_image")) {
          if (!output->m_key_image) output->m_key_image = std::make_shared<monero::monero_key_image>();
          output->m_key_image.get()->m_hex = it2->second.data();
        }
        else if (key_key == std::string("key_offsets")) {
          auto offsets_node = it->second;

          for (auto it2 = offsets_node.begin(); it2 != offsets_node.end(); ++it2) {
            output->m_ring_output_indices.push_back(it2->second.get_value<uint64_t>());
          }
        }
      }
    }
    else if (key == std::string("amount")) output->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("target")) {
      auto target_node = it->second;

      for(auto it2 = target_node.begin(); it2 != target_node.end(); ++it2) {
        std::string target_key = it2->first;

        if (target_key == std::string("key")) {
          output->m_stealth_public_key = it2->second.data();
        }
        else if (target_key == std::string("tagged_key")) {
          auto tagged_key_node = it2->second;

          for (auto it3 = tagged_key_node.begin(); it3 != tagged_key_node.end(); ++it3) {
            std::string tagged_key_key = it3->first;

            if (tagged_key_key == std::string("key")) {
              output->m_stealth_public_key = it3->second.data();
            }
          }
        }
      }
    }
  }
}

void PyMoneroTx::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx>& tx) {  
  std::shared_ptr<monero_block> block = nullptr;
  
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("tx_hash") || key == std::string("id_hash")) {
      std::string tx_hash = it->second.data();
      if (!tx_hash.empty()) tx->m_hash = tx_hash;
    }
    else if (key == std::string("block_timestamp")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      block->m_timestamp = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("block_height")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      block->m_height = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("last_relayed_time")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_last_relayed_timestamp = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("receive_time") || key == std::string("received_timestamp")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_received_timestamp = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("confirmations")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_num_confirmations = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("in_pool")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      bool in_pool = it->second.get_value<bool>();
      tx->m_is_confirmed = !in_pool;
      tx->m_in_tx_pool = in_pool;
    }
    else if (key == std::string("double_spend_seen")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_is_double_spend_seen = it->second.get_value<bool>();
    }
    else if (key == std::string("version")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_version = it->second.get_value<uint32_t>();
    }
    else if (key == std::string("vin") && it->second.size() != 1) {
      auto node2 = it->second;
      std::vector<std::shared_ptr<monero_output>> inputs;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto output = std::make_shared<monero::monero_output>();
        PyMoneroOutput::from_property_tree(it2->second, output);
        inputs.push_back(output);
      }
      if (inputs.size() != 1) tx->m_inputs = inputs;
    }
    else if (key == std::string("vout")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto output = std::make_shared<monero::monero_output>();
        PyMoneroOutput::from_property_tree(it2->second, output);
        tx->m_outputs.push_back(output);
      }
    }
    else if (key == std::string("rct_signatures")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        std::string _key = it2->first;

        if (_key == std::string("txnfee")) {
          tx->m_fee = it2->second.get_value<uint64_t>();
        }
      }
    }
    else if (key == std::string("rctsig_prunable")) {
      // TODO: implement
    }
    else if (key == std::string("unlock_time")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_unlock_time = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("as_hex") || key == std::string("tx_blob")) tx->m_full_hex = it->second.data();
    else if (key == std::string("blob_size")) tx->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("weight")) tx->m_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("fee")) tx->m_fee = it->second.get_value<uint64_t>();
    else if (key == std::string("relayed")) tx->m_is_relayed = it->second.get_value<bool>();
    else if (key == std::string("output_indices")) {
      auto node2 = it->second;
      std::vector<uint64_t> output_indices;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        output_indices.push_back(it2->second.get_value<uint64_t>());
      }
      tx->m_output_indices = output_indices;
    }
    else if (key == std::string("do_not_relay")) tx->m_relay = !it->second.get_value<bool>();
    else if (key == std::string("kept_by_block")) tx->m_is_kept_by_block = it->second.get_value<bool>();
    else if (key == std::string("signatures")) {
      auto node2 = it->second;
      std::vector<std::string> signatures;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        signatures.push_back(it2->second.data());
      }
      tx->m_signatures = signatures;
    }
    else if (key == std::string("last_failed_height")) {
      uint64_t last_failed_height = it->second.get_value<uint64_t>();
      if (last_failed_height == 0) tx->m_is_failed = false;
      else {
        tx->m_is_failed = true;
        tx->m_last_failed_height = last_failed_height;
      }
    }
    else if (key == std::string("last_failed_hash")) {
      std::string hash = it->second.data();
      if (hash == DEFAULT_ID) tx->m_is_failed = false;
      else {
        tx->m_is_failed = true;
        tx->m_last_failed_hash = hash;
      }
    }
    else if (key == std::string("extra")) {
      auto extra_node = it->second;
      for(auto it_extra = extra_node.begin(); it_extra != extra_node.end(); ++it_extra) {
        tx->m_extra.push_back(it_extra->second.get_value<uint8_t>());
      }
    }
    else if (key == std::string("max_used_block_height")) tx->m_max_used_block_height = it->second.get_value<uint64_t>();
    else if (key == std::string("max_used_block_id_hash")) tx->m_max_used_block_hash = it->second.data();
    else if (key == std::string("prunable_hash")) tx->m_prunable_hash = it->second.data();
    else if (key == std::string("prunable_as_hex")) tx->m_prunable_hex = it->second.data();
    else if (key == std::string("pruned_as_hex")) tx->m_pruned_hex = it->second.data();
  }

  if (block != nullptr) {
    block->m_txs.push_back(tx);
    tx->m_block = block;
  }

  // initialize remaining known fields
  if (tx->m_is_confirmed) {
    tx->m_relay = true;
    tx->m_is_relayed = true;
    tx->m_is_failed = false;
  } else {
    tx->m_num_confirmations = 0;
  }

  if (tx->m_is_failed == boost::none) tx->m_is_failed = false;
  if (!tx->m_output_indices.empty() && !tx->m_outputs.empty())  {
    if (tx->m_output_indices.size() != tx->m_outputs.size()) throw std::runtime_error("Expected outputs count equal to indices count");
    int i = 0;
    for (const auto &output : tx->m_outputs) {
      output->m_index = tx->m_output_indices[i++];
    }
  }
  //if (rpcTx.containsKey("as_json") && !"".equals(rpcTx.get("as_json"))) convertRpcTx(JsonUtils.deserialize(MoneroRpcConnection.MAPPER, (String) rpcTx.get("as_json"), new TypeReference<Map<String, Object>>(){}), tx);
  //if (rpcTx.containsKey("tx_json") && !"".equals(rpcTx.get("tx_json"))) convertRpcTx(JsonUtils.deserialize(MoneroRpcConnection.MAPPER, (String) rpcTx.get("tx_json"), new TypeReference<Map<String, Object>>(){}), tx);
  if (tx->m_is_relayed != true) tx->m_last_relayed_timestamp = boost::none;
}

void PyMoneroTx::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_tx>>& txs) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("transactions")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;
        auto tx = std::make_shared<monero::monero_tx>();
        tx->m_is_confirmed = false;
        tx->m_is_miner_tx = false;
        tx->m_in_tx_pool = true;
        tx->m_num_confirmations = 0;
        from_property_tree(node3, tx);
        txs.push_back(tx);
      }

      return;
    }
    else if (key == std::string("txs")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;
        auto tx = std::make_shared<monero::monero_tx>();
        tx->m_is_miner_tx = false;
        from_property_tree(node3, tx);
        txs.push_back(tx);
      }

      return;
    }
  }
}

void PyMoneroVersion::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroVersion>& version) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("version")) version->m_number = it->second.get_value<uint32_t>();
    else if (key == std::string("release")) version->m_is_release = it->second.get_value<bool>();
  }
}

void PyMoneroAltChain::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAltChain>& alt_chain) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("difficulty")) alt_chain->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("block_hashes")) {
      for (const auto& child : it->second) alt_chain->m_block_hashes.push_back(child.second.data());
    }
    else if (key == std::string("height")) alt_chain->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("length")) alt_chain->m_length = it->second.get_value<uint64_t>();
    else if (key == std::string("main_chain_parent_block")) alt_chain->m_main_chain_parent_block_hash = it->second.data();
  }
}

void PyMoneroGetBlockCountResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBlockCountResult>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("count")) result->m_count = it->second.get_value<uint64_t>();
  }
}

void PyMoneroBan::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBan>& ban) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("host")) ban->m_host = it->second.data();
    else if (key == std::string("ip")) ban->m_ip = it->second.get_value<int>();
    else if (key == std::string("ban")) ban->m_is_banned = it->second.get_value<bool>();
    else if (key == std::string("seconds")) ban->m_seconds = it->second.get_value<uint64_t>();
  }
}

void PyMoneroBan::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroBan>>& bans) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("bans")) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto ban = std::make_shared<PyMoneroBan>();
        PyMoneroBan::from_property_tree(it2->second, ban);
        bans.push_back(ban);
      }
    }
  }
}

void PyMoneroPruneResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPruneResult>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("pruned")) result->m_is_pruned = it->second.get_value<bool>();
    else if (key == std::string("pruning_seed")) result->m_pruning_seed = it->second.get_value<int>();
  }
}

void PyMoneroMiningStatus::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMiningStatus>& status) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("active")) status->m_is_active = it->second.get_value<bool>();
    else if (key == std::string("is_background_mining_enabled")) status->m_is_background = it->second.get_value<bool>();
    else if (key == std::string("address") && !it->second.data().empty()) status->m_address = it->second.data();
    else if (key == std::string("speed")) status->m_speed = it->second.get_value<uint64_t>();
    else if (key == std::string("threads_count")) status->m_num_threads = it->second.get_value<int>();
  }

  if (status->m_is_active != boost::none && *status->m_is_active == false) {
    status->m_is_background = boost::none;
    status->m_address = boost::none;
  }
}

std::vector<std::string> PyMoneroTxHashes::from_property_tree(const boost::property_tree::ptree& node) {
  std::vector<std::string> result;
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("tx_hashes")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        result.push_back(it2->second.data());
      }
    }
  }
  return result;
}

void PyMoneroMinerTxSum::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMinerTxSum>& sum) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("emission_amount")) sum->m_emission_sum = it->second.get_value<uint64_t>();
    else if (key == std::string("fee_amount")) sum->m_fee_sum = it->second.get_value<uint64_t>();
  }
}

void PyMoneroBlockTemplate::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBlockTemplate>& tmplt) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("blocktemplate_blob")) tmplt->m_block_template_blob = it->second.data();
    else if (key == std::string("blockhashing_blob")) tmplt->m_block_hashing_blob = it->second.data();
    else if (key == std::string("difficulty")) tmplt->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("expected_reward")) tmplt->m_expected_reward = it->second.get_value<uint64_t>();
    else if (key == std::string("height")) tmplt->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("prev_hash")) tmplt->m_prev_hash = it->second.data();
    else if (key == std::string("reserved_offset")) tmplt->m_reserved_offset = it->second.get_value<uint64_t>();
    else if (key == std::string("seed_height")) tmplt->m_seed_height = it->second.get_value<uint64_t>();
    else if (key == std::string("seed_hash")) tmplt->m_seed_hash = it->second.data();
    else if (key == std::string("next_seed_hash")) tmplt->m_next_seed_hash = it->second.data();
  }
}

void PyMoneroConnectionSpan::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroConnectionSpan>& span) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("connection_id")) span->m_connection_id = it->second.data();
    else if (key == std::string("nblocks")) span->m_num_blocks = it->second.get_value<uint64_t>();
    else if (key == std::string("remote_address")) span->m_remote_address = it->second.data();
    else if (key == std::string("rate")) span->m_rate = it->second.get_value<uint64_t>();
    else if (key == std::string("speed")) span->m_speed = it->second.get_value<uint64_t>();
    else if (key == std::string("size")) span->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("start_block_height")) span->m_start_height = it->second.get_value<uint64_t>();
  }
}

void PyMoneroPeer::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPeer>& peer) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("host")) peer->m_host = it->second.data();
    else if (key == std::string("address")) peer->m_address = it->second.data();
    else if (key == std::string("current_download")) peer->m_current_download = it->second.get_value<uint64_t>();
    else if (key == std::string("current_upload")) peer->m_current_upload = it->second.get_value<uint64_t>();
    else if (key == std::string("avg_download")) peer->m_avg_download = it->second.get_value<uint64_t>();
    else if (key == std::string("avg_upload")) peer->m_avg_upload = it->second.get_value<uint64_t>();
    else if (key == std::string("connection_id")) peer->m_hash = it->second.data();
    else if (key == std::string("height")) peer->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("incoming")) peer->m_is_incoming = it->second.get_value<bool>();
    else if (key == std::string("live_time")) peer->m_live_time = it->second.get_value<uint64_t>();
    else if (key == std::string("local_ip")) peer->m_is_local_ip = it->second.get_value<bool>();
    else if (key == std::string("localhost")) peer->m_is_local_host = it->second.get_value<bool>();
    else if (key == std::string("recv_count")) peer->m_num_receives = it->second.get_value<int>();
    else if (key == std::string("send_count")) peer->m_num_sends = it->second.get_value<int>();
    else if (key == std::string("recv_idle_time")) peer->m_receive_idle_time = it->second.get_value<uint64_t>();
    else if (key == std::string("send_idle_time")) peer->m_send_idle_time = it->second.get_value<uint64_t>();
    else if (key == std::string("state")) peer->m_state = it->second.data();
    else if (key == std::string("support_flags")) peer->m_num_support_flags = it->second.get_value<int>();
    else if (key == std::string("id") || key == std::string("peer_id")) peer->m_id = it->second.data();
    else if (key == std::string("last_seen")) peer->m_last_seen_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("port")) peer->m_port = it->second.get_value<int>();
    else if (key == std::string("rpc_port")) peer->m_rpc_port = it->second.get_value<int>();
    else if (key == std::string("pruning_seed")) peer->m_pruning_seed = it->second.get_value<int>();
    else if (key == std::string("rpc_credits_per_hash")) peer->m_rpc_credits_per_hash = it->second.get_value<uint64_t>();
    else if (key == std::string("address_type")) {
      int rpc_type = it->second.get_value<int>();
      if (rpc_type == 0) {
        peer->m_connection_type = PyMoneroConnectionType::INVALID;
      }
      else if (rpc_type == 1) {
        peer->m_connection_type = PyMoneroConnectionType::IPV4;
      }
      else if (rpc_type == 2) {
        peer->m_connection_type = PyMoneroConnectionType::IPV6;
      }
      else if (rpc_type == 3) {
        peer->m_connection_type = PyMoneroConnectionType::TOR;
      }
      else if (rpc_type == 4) {
        peer->m_connection_type = PyMoneroConnectionType::I2P;
      }
      else throw std::runtime_error("Invalid RPC peer type, expected 0-4: " + std::to_string(rpc_type));
    }
  }
}

void PyMoneroPeer::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroPeer>>& peers) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    bool is_online = key == std::string("white_list");
    if (key == std::string("connections") || is_online || key == std::string("gray_list") ) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto peer = std::make_shared<PyMoneroPeer>();
        PyMoneroPeer::from_property_tree(it2->second, peer);
        peer->m_is_online = is_online;
        peers.push_back(peer);
      }
    }
  }
}

void PyMoneroSubmitTxResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroSubmitTxResult>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("double_spend")) result->m_is_double_spend = it->second.get_value<bool>();
    else if (key == std::string("fee_too_low")) result->m_is_fee_too_low = it->second.get_value<bool>();
    else if (key == std::string("invalid_input")) result->m_has_invalid_input = it->second.get_value<bool>();
    else if (key == std::string("invalid_output")) result->m_has_invalid_output = it->second.get_value<bool>();
    else if (key == std::string("too_few_outputs")) result->m_has_too_few_outputs = it->second.get_value<bool>();
    else if (key == std::string("low_mixin")) result->m_is_mixin_too_low = it->second.get_value<bool>();
    else if (key == std::string("not_relayed")) result->m_is_relayed = !it->second.get_value<bool>();
    else if (key == std::string("overspend")) result->m_is_overspend = it->second.get_value<bool>();
    else if (key == std::string("reason")) result->m_reason = it->second.data();
    else if (key == std::string("too_big")) result->m_is_too_big = it->second.get_value<bool>();
    else if (key == std::string("sanity_check_failed")) result->m_sanity_check_failed = it->second.get_value<bool>();
    else if (key == std::string("credits")) result->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) result->m_top_block_hash = top_hash;
    }
    else if (key == std::string("tx_extra_too_big")) result->m_is_tx_extra_too_big = it->second.get_value<bool>();
    else if (key == std::string("nonzero_unlock_time")) result->m_is_nonzero_unlock_time = it->second.get_value<bool>();
  }
}

void PyMoneroOutputDistributionEntry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputDistributionEntry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("amount")) entry->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("base")) entry->m_base = it->second.get_value<int>();
    else if (key == std::string("distribution")) {
      auto node2 = it->second;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        entry->m_distribution.push_back(it2->second.get_value<int>());
      }
    }
    else if (key == std::string("start_height")) entry->m_start_height = it->second.get_value<uint64_t>();
  }
}

void PyMoneroOutputHistogramEntry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputHistogramEntry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("amount")) entry->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("total_instances")) entry->m_num_instances = it->second.get_value<uint64_t>();
    else if (key == std::string("unlocked_instances")) entry->m_unlocked_instances = it->second.get_value<uint64_t>();
    else if (key == std::string("recent_instances")) entry->m_recent_instances = it->second.get_value<uint64_t>();
  }
}

void PyMoneroOutputHistogramEntry::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>>& entries) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("histogram")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto entry = std::make_shared<PyMoneroOutputHistogramEntry>();
        from_property_tree(node2, entry);
        entries.push_back(entry);
      }
    }
  }
}

void PyMoneroTxPoolStats::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroTxPoolStats>& stats) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("txs_total")) stats->m_num_txs = it->second.get_value<int>();
    else if (key == std::string("num_not_relayed")) stats->m_num_not_relayed = it->second.get_value<int>();
    else if (key == std::string("num_failing")) stats->m_num_failing = it->second.get_value<int>();
    else if (key == std::string("num_double_spends")) stats->m_num_double_spends = it->second.get_value<int>();
    else if (key == std::string("num10m")) stats->m_num10m = it->second.get_value<int>();
    else if (key == std::string("fee_total")) stats->m_fee_total = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_max")) stats->m_bytes_max = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_med")) stats->m_bytes_med = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_min")) stats->m_bytes_min = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_total")) stats->m_bytes_total = it->second.get_value<uint64_t>();
    else if (key == std::string("histo_98pc")) stats->m_histo98pc = it->second.get_value<uint64_t>();
    else if (key == std::string("oldest")) stats->m_oldest_timestamp = it->second.get_value<uint64_t>();
  }
}

void PyMoneroDaemonUpdateCheckResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateCheckResult>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("update")) check->m_is_update_available = it->second.get_value<bool>();
    else if (key == std::string("version") && !it->second.data().empty()) check->m_version = it->second.data();
    else if (key == std::string("hash") && !it->second.data().empty()) check->m_hash = it->second.data();
    else if (key == std::string("auto_uri") && !it->second.data().empty()) check->m_auto_uri = it->second.data();
    else if (key == std::string("user_uri") && !it->second.data().empty()) check->m_user_uri = it->second.data();
  }
}

void PyMoneroDaemonUpdateDownloadResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateDownloadResult>& check) {
  PyMoneroDaemonUpdateCheckResult::from_property_tree(node, check);
  
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("download_path") && !it->second.data().empty()) check->m_download_path = it->second.data();
  }
}

void PyMoneroFeeEstimate::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroFeeEstimate>& estimate) {    
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("fee")) estimate->m_fee = it->second.get_value<uint64_t>();
    else if (key == std::string("quantization_mask")) estimate->m_quantization_mask = it->second.get_value<uint64_t>();
    else if (key == std::string("fees")) {
      auto node2 = it->second;
      for (boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        uint64_t fee = it2->second.get_value<uint64_t>();
        estimate->m_fees.push_back(fee);
      }
    }
  }
}

void PyMoneroDaemonInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonInfo>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("version")) info->m_version = it->second.data();
    else if (key == std::string("alt_blocks_count")) info->m_num_alt_blocks = it->second.get_value<uint64_t>();
    else if (key == std::string("block_size_limit")) info->m_block_size_limit = it->second.get_value<uint64_t>();
    else if (key == std::string("block_size_median")) info->m_block_size_median = it->second.get_value<uint64_t>();
    else if (key == std::string("block_weight_limit")) info->m_block_weight_limit = it->second.get_value<uint64_t>();
    else if (key == std::string("block_weight_median")) info->m_block_weight_median = it->second.get_value<uint64_t>();
    else if (key == std::string("bootstrap_daemon_address") && !it->second.data().empty()) info->m_bootstrap_daemon_address = it->second.data();
    else if (key == std::string("difficulty")) info->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("cumulative_difficulty")) info->m_cumulative_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("free_space")) info->m_free_space = it->second.get_value<uint64_t>();
    else if (key == std::string("grey_peerlist_size")) info->m_num_offline_peers = it->second.get_value<int>();
    else if (key == std::string("white_peerlist_size")) info->m_num_online_peers = it->second.get_value<int>();
    else if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("height_without_bootstrap")) info->m_height_without_bootstrap = it->second.get_value<uint64_t>();
    else if (key == std::string("nettype")) {
      std::string nettype = it->second.data();
      if (nettype == std::string("mainnet") || nettype == std::string("fakechain")) info->m_network_type = monero::monero_network_type::MAINNET;
      else if (nettype == std::string("testnet")) info->m_network_type = monero::monero_network_type::TESTNET;
      else if (nettype == std::string("stagenet")) info->m_network_type = monero::monero_network_type::STAGENET;
    }
    else if (key == std::string("offline")) info->m_is_offline = it->second.get_value<bool>();
    else if (key == std::string("incoming_connections_count")) info->m_num_incoming_connections = it->second.get_value<int>();
    else if (key == std::string("outgoing_connections_count")) info->m_num_outgoing_connections = it->second.get_value<int>();
    else if (key == std::string("rpc_connections_count")) info->m_num_rpc_connections = it->second.get_value<int>();
    else if (key == std::string("start_time")) info->m_start_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("adjusted_time")) info->m_adjusted_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("target")) info->m_target = it->second.get_value<uint64_t>();
    else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
    else if (key == std::string("top_block_hash") || key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) info->m_top_block_hash = top_hash;
    }
    else if (key == std::string("tx_count")) info->m_num_txs = it->second.get_value<int>();
    else if (key == std::string("tx_pool_size")) info->m_num_txs_pool = it->second.get_value<int>();
    else if (key == std::string("was_bootstrap_ever_used")) info->m_was_bootstrap_ever_used = it->second.get_value<bool>();
    else if (key == std::string("database_size")) info->m_database_size = it->second.get_value<uint64_t>();
    else if (key == std::string("update_available")) info->m_update_available = it->second.get_value<bool>();
    else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("busy_syncing")) info->m_is_busy_syncing = it->second.get_value<bool>();
    else if (key == std::string("synchronized")) info->m_is_synchronized = it->second.get_value<bool>();
    else if (key == std::string("restricted")) info->m_is_restricted = it->second.get_value<bool>();
  }
}

void PyMoneroDaemonSyncInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonSyncInfo>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
    else if (key == std::string("next_needed_pruning_seed")) info->m_next_needed_pruning_seed = it->second.get_value<int>();
    // TODO implement overview field
    //else if (key == std::string("overview") && !it->second.data().empty()) info->m_overview = it->second.data();
    else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) info->m_top_block_hash = top_hash;
    }
  }
}

void PyMoneroHardForkInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroHardForkInfo>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("earliest_height")) info->m_earliest_height = it->second.get_value<uint64_t>();
    else if (key == std::string("enabled")) info->m_is_enabled = it->second.get_value<bool>();
    else if (key == std::string("state")) info->m_state = it->second.get_value<int>();
    else if (key == std::string("threshold")) info->m_threshold = it->second.get_value<int>();
    else if (key == std::string("version")) info->m_version = it->second.get_value<int>();
    else if (key == std::string("votes")) info->m_num_votes = it->second.get_value<int>();
    else if (key == std::string("window")) info->m_window = it->second.get_value<int>();
    else if (key == std::string("voting")) info->m_voting = it->second.get_value<int>();
    else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) info->m_top_block_hash = top_hash;
    }
  }
}

void PyMoneroGetAltBlocksHashesResponse::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("blks_hashes")) {
      auto node2 = it->second;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        block_hashes.push_back(it2->second.data());
      }
    }
  }
}

void PyMoneroBandwithLimits::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBandwithLimits>& limits) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("limit_up")) limits->m_up = it->second.get_value<int>();
    else if (key == std::string("limit_down")) limits->m_down = it->second.get_value<int>();
  }
}

void PyMoneroGetHeightResponse::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetHeightResponse>& response) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) response->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("untrusted")) response->m_untrusted = it->second.get_value<bool>();
  }
}

rapidjson::Value PyMoneroDownloadUpdateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);

  if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
  if (m_path != boost::none) monero_utils::add_json_member("path", m_path.get(), allocator, root, value_str);

  return root;
}

rapidjson::Value PyMoneroCheckUpdateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
  return root;
}

rapidjson::Value PyMoneroStartMiningParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_address != boost::none) monero_utils::add_json_member("miner_address", m_address.get(), allocator, root, value_str);
  if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);
  if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
  if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);
  return root;
}

rapidjson::Value PyMoneroPathRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  if (m_params != boost::none) return m_params.get()->to_rapidjson_val(allocator);
  throw std::runtime_error("No params provided");
}

rapidjson::Value PyMoneroJsonRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);

  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
  if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
  if (m_method != boost::none) monero_utils::add_json_member("method", m_method.get(), allocator, root, value_str);
  if (m_params != boost::none) root.AddMember("params", m_params.get()->to_rapidjson_val(allocator), allocator);

  return root;
}

rapidjson::Value PyMoneroPruneBlockchainParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (m_check != boost::none) monero_utils::add_json_member("check", m_check.get(), allocator, root);
  return root;
}

rapidjson::Value PyMoneroSubmitBlocksParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  return monero_utils::to_rapidjson_val(allocator, m_block_blobs);
}

rapidjson::Value PyMoneroGetBlockParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_fill_pow_hash != boost::none) monero_utils::add_json_member("fill_pow_hash", m_fill_pow_hash.get(), allocator, root);

  return root; 
}

rapidjson::Value PyMoneroGetBlockRangeParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);
  if (m_end_height != boost::none) monero_utils::add_json_member("end_height", m_end_height.get(), allocator, root, value_num);

  return root;
}

rapidjson::Value PyMoneroGetBlockHashParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  std::vector<uint64_t> params;
  if (m_height != boost::none) params.push_back(m_height.get());
  return monero_utils::to_rapidjson_val(allocator, params);
}

rapidjson::Value PyMoneroGetBlockTemplateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_wallet_address != boost::none) monero_utils::add_json_member("wallet_address", m_wallet_address.get(), allocator, root, value_str);
  if (m_reserve_size != boost::none) monero_utils::add_json_member("reserve_size", m_reserve_size.get(), allocator, root, value_num);

  return root; 
}

rapidjson::Value PyMoneroGetBlocksByHeightRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  rapidjson::Value root(rapidjson::kObjectType);
  if (!m_heights.empty()) root.AddMember("heights", monero_utils::to_rapidjson_val(allocator, m_heights), allocator);
  return root;
}

rapidjson::Value PyMoneroBan::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_host != boost::none) monero_utils::add_json_member("host", m_host.get(), allocator, root, value_str);
  if (m_ip != boost::none) monero_utils::add_json_member("ip", m_ip.get(), allocator, root, value_num);
  if (m_is_banned != boost::none) monero_utils::add_json_member("ban", m_is_banned.get(), allocator, root);
  if (m_seconds != boost::none) monero_utils::add_json_member("seconds", m_seconds.get(), allocator, root, value_num);
  return root;
}

rapidjson::Value PyMoneroSubmitTxParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tx_hex != boost::none) monero_utils::add_json_member("tx_as_hex", m_tx_hex.get(), allocator, root, value_str);
  if (m_do_not_relay != boost::none) monero_utils::add_json_member("do_not_relay", m_do_not_relay.get(), allocator, root);
  return root; 
}

rapidjson::Value PyMoneroRelayTxParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  return root; 
}

rapidjson::Value PyMoneroBandwithLimits::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_up != boost::none) monero_utils::add_json_member("limit_up", m_up.get(), allocator, root, value_num);
  if (m_down != boost::none) monero_utils::add_json_member("limit_down", m_down.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroPeerLimits::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_in_peers != boost::none) monero_utils::add_json_member("in_peers", m_in_peers.get(), allocator, root, value_num);
  if (m_out_peers != boost::none) monero_utils::add_json_member("out_peers", m_out_peers.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroGetMinerTxSumParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_count != boost::none) monero_utils::add_json_member("count", m_count.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroGetFeeEstimateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_grace_blocks != boost::none) monero_utils::add_json_member("grace_blocks", m_grace_blocks.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroSetBansParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_bans.empty()) root.AddMember("bans", monero_utils::to_rapidjson_val(allocator, m_bans), allocator);
  return root; 
}

rapidjson::Value PyMoneroGetTxsParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_tx_hashes.empty()) root.AddMember("txs_hashes", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  if (m_prune != boost::none) monero_utils::add_json_member("prune", m_prune.get(), allocator, root);
  if (m_decode_as_json != boost::none) monero_utils::add_json_member("decode_as_json", m_decode_as_json.get(), allocator, root);
  return root; 
}

rapidjson::Value PyMoneroGetOutputHistrogramParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (!m_amounts.empty()) root.AddMember("amounts", monero_utils::to_rapidjson_val(allocator, m_amounts), allocator);
  if (m_min_count != boost::none) monero_utils::add_json_member("min_count", m_min_count.get(), allocator, root, value_num);
  if (m_max_count != boost::none) monero_utils::add_json_member("max_count", m_max_count.get(), allocator, root, value_num);
  if (m_is_unlocked != boost::none) monero_utils::add_json_member("is_unlocked", m_is_unlocked.get(), allocator, root);
  if (m_recent_cutoff != boost::none) monero_utils::add_json_member("recent_cutoff", m_recent_cutoff.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroIsKeyImageSpentParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_key_images.empty()) root.AddMember("key_images", monero_utils::to_rapidjson_val(allocator, m_key_images), allocator);
  return root; 
}

void PyMoneroConnectionManager::add_listener(const std::shared_ptr<monero_connection_manager_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.push_back(listener);
}

void PyMoneroConnectionManager::remove_listener(const std::shared_ptr<monero_connection_manager_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<monero_connection_manager_listener> iter){ return iter == listener; }), m_listeners.end());
}

void PyMoneroConnectionManager::remove_listeners() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.clear();
}

std::vector<std::shared_ptr<monero_connection_manager_listener>> PyMoneroConnectionManager::get_listeners() const {
  return m_listeners;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_connection_by_uri(const std::string &uri) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  for(const auto &m_connection : m_connections) {
    if (m_connection->m_uri == uri) return m_connection;
  }

  return nullptr;
}

void PyMoneroConnectionManager::add_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
  if (connection->m_uri == boost::none) throw std::runtime_error("Invalid connection uri");
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  for(const auto &m_connection : m_connections) {
    if (m_connection->m_uri == connection->m_uri) throw std::runtime_error("Connection URI already exists with connection manager: " + connection->m_uri.get());
  }

  m_connections.push_back(connection);
}

void PyMoneroConnectionManager::add_connection(const std::string &uri) {
  std::shared_ptr<PyMoneroRpcConnection> connection = std::make_shared<PyMoneroRpcConnection>();
  connection->m_uri = uri;
  add_connection(connection);
}

void PyMoneroConnectionManager::remove_connection(const std::string &uri) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  std::shared_ptr<PyMoneroRpcConnection> connection = get_connection_by_uri(uri);

  if (connection == nullptr) throw std::runtime_error("Connection not found");
  
  m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == connection; }), m_connections.end());

  if (connection == m_current_connection) {
    m_current_connection = nullptr;
    on_connection_changed(m_current_connection);
  }
}

void PyMoneroConnectionManager::set_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
  if (connection == m_current_connection) return;

  if (connection == nullptr) {
    m_current_connection = nullptr;
    on_connection_changed(nullptr);
    return;
  }

  if (connection->m_uri == boost::none || connection->m_uri->empty()) throw std::runtime_error("Connection is missing URI");

  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  auto prev_connection = get_connection_by_uri(connection->m_uri.get());
  if (prev_connection != nullptr) m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&prev_connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == prev_connection; }), m_connections.end());
  add_connection(connection);
  m_current_connection = connection;
  on_connection_changed(connection);
}

void PyMoneroConnectionManager::set_connection(const std::string& uri) {
  if (uri.empty()) {
    set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr));
    return;
  }

  auto found = get_connection_by_uri(uri);

  if (found != nullptr) {
    set_connection(found);
  }
  else {
    auto connection = std::make_shared<PyMoneroRpcConnection>();
    connection->m_uri = uri;
    set_connection(connection);
  }
}

bool PyMoneroConnectionManager::has_connection(const std::string& uri) {
  auto connection = get_connection_by_uri(uri);

  if (connection != nullptr) return true;
  return false;
}

bool PyMoneroConnectionManager::is_connected() const {
  if (m_current_connection == nullptr) return false;
  return m_current_connection->is_connected();
}

void PyMoneroConnectionManager::check_connection() {
  bool connection_changed = false;
  std::shared_ptr<PyMoneroRpcConnection> connection = get_connection();
  if (connection != nullptr) {
    if (connection->check_connection(m_timeout)) connection_changed = true;
    std::vector<std::shared_ptr<PyMoneroRpcConnection>> cons;
    cons.push_back(connection);
    process_responses(cons);
  }
  if (m_auto_switch && !is_connected()) {
    std::shared_ptr<PyMoneroRpcConnection> best_connection = get_best_available_connection(connection);
    if (best_connection != nullptr) {
      set_connection(best_connection);
      return;
    }
  }
  if (connection_changed) on_connection_changed(connection);
}

void PyMoneroConnectionManager::set_auto_switch(bool auto_switch) {
  m_auto_switch = auto_switch;
}

void PyMoneroConnectionManager::stop_polling() {
  if (m_is_polling) {
    m_is_polling = false;
    if (m_thread.joinable()) m_thread.join();
  }
}

void PyMoneroConnectionManager::start_polling(std::optional<uint64_t> period_ms, std::optional<bool> auto_switch, std::optional<uint64_t> timeout_ms, std::optional<PyMoneroConnectionPollType> poll_type, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> &excluded_connections) {
  // apply defaults
  if (!period_ms.has_value()) period_ms = DEFAULT_POLL_PERIOD;
  if (auto_switch.has_value()) set_auto_switch(auto_switch.value());
  if (timeout_ms.has_value()) set_timeout(timeout_ms.value());
  if (!poll_type.has_value()) poll_type = PyMoneroConnectionPollType::PRIORITIZED;

  // stop polling
  stop_polling();

  // start polling
  switch (poll_type.value()) {
    case PyMoneroConnectionPollType::CURRENT:
      start_polling_connection(period_ms.value());
      break;
    case PyMoneroConnectionPollType::ALL:
      start_polling_connections(period_ms.value());
      break;
    case PyMoneroConnectionPollType::UNDEFINED:
    case PyMoneroConnectionPollType::PRIORITIZED:
      start_polling_prioritized_connections(period_ms.value(), excluded_connections);
      break;
  }
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
  auto cons = get_connections_in_ascending_priority();
  for (const auto& prioritizedConnections : cons) {
    try {
      std::vector<std::thread*> futures;
      for (const auto& connection : prioritizedConnections) {
        if (!connection) throw std::runtime_error("connection is nullptr");
        if (excluded_connections.count(connection)) continue;
        std::thread thread = std::thread([this, connection]() {
          connection->check_connection(m_timeout);
        });
        thread.detach();
        futures.push_back(&thread);
      }

      for (auto& fut : futures) {
        if (fut->joinable()) fut->join();
      }

      std::shared_ptr<PyMoneroRpcConnection> best_connection = nullptr;

      for (const auto& conn : prioritizedConnections) {
        try {
          if (!conn) throw std::runtime_error("connection is nullptr");
          if (conn->is_connected()) {
            if (best_connection == nullptr || best_connection->m_response_time == boost::none || best_connection->m_response_time < conn->m_response_time) best_connection = conn;
          }
        } catch (...) {
          std::cout << "MoneroRpcConnection::get_best_available_connection(): error" << std::endl;
        }
      }

      if (best_connection != nullptr) return best_connection;
    } catch (const std::exception& e) {
      throw std::runtime_error(std::string("Connection check error: ") + e.what());
    }
  }

  return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_available_connection(std::shared_ptr<PyMoneroRpcConnection>& excluded_connection) {
  const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = { excluded_connection };

  return get_best_available_connection(excluded_connections);
}

void PyMoneroConnectionManager::check_connections() {
  check_connections(get_connections());
}

void PyMoneroConnectionManager::disconnect() { 
  set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr)); 
}

void PyMoneroConnectionManager::clear() {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  m_connections.clear();

  if (m_current_connection != nullptr) {
    m_current_connection = nullptr;
    on_connection_changed(m_current_connection);
  }
}

void PyMoneroConnectionManager::reset() {
  remove_listeners();
  stop_polling();
  clear();
  m_timeout = DEFAULT_TIMEOUT;
  m_auto_switch = DEFAULT_AUTO_SWITCH;
}

void PyMoneroConnectionManager::on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);

  for (const auto &listener : m_listeners) {
    listener->on_connection_changed(connection);
  }
}

std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> PyMoneroConnectionManager::get_connections_in_ascending_priority() {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  std::map<int, std::vector<std::shared_ptr<PyMoneroRpcConnection>>> connection_priorities;

  for (const auto& connection : m_connections) {
    int priority = connection->m_priority;
    connection_priorities[priority].push_back(connection);
  }

  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> prioritized_connections;

  for (auto& [priority, group] : connection_priorities) {
    prioritized_connections.push_back(group);
  }

  if (!prioritized_connections.empty() && connection_priorities.count(0)) {
    auto it = std::find_if(prioritized_connections.begin(), prioritized_connections.end(),
                            [](const auto& group) {
                              return !group.empty() && group[0]->m_priority == 0;
                            });

    if (it != prioritized_connections.end()) {
      auto zero_priority_group = *it;
      prioritized_connections.erase(it);
      prioritized_connections.push_back(zero_priority_group);
    }
  }

  return prioritized_connections;
}

void PyMoneroConnectionManager::start_polling_connection(uint64_t period_ms) {
  m_is_polling = true;

  m_thread = std::thread([this, period_ms]() {
    while (m_is_polling) {
      try {
        check_connection();
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
  });
  m_thread.detach();
}

void PyMoneroConnectionManager::start_polling_connections(uint64_t period_ms) {
  m_is_polling = true;

  m_thread = std::thread([this, period_ms]() {
    while (m_is_polling) {
      try {
        check_connections();
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
  });
  m_thread.detach();
}

void PyMoneroConnectionManager::start_polling_prioritized_connections(uint64_t period_ms, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
  m_is_polling = true;
  m_thread = std::thread([this, period_ms, &excluded_connections]() {
    while (m_is_polling) {
      try {
        check_prioritized_connections(excluded_connections);
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
  });
  m_thread.detach();
}

bool PyMoneroConnectionManager::check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  try {
    auto timeout_ms = m_timeout;

    bool has_connection = false;

    for (const auto& connection : connections) {
      if (excluded_connections.count(connection)) continue;

      bool changed = connection->check_connection(timeout_ms);
      if (changed && connection == get_connection()) {
        on_connection_changed(connection);
      }
      if (connection->is_connected() && !has_connection) {
        has_connection = true;
        if (!is_connected() && m_auto_switch) {
          set_connection(connection);
        }
      }
    }

    process_responses(connections);
    return has_connection;
  } 
  catch (const std::exception& e) {
    throw std::runtime_error(std::string("check_connections failed: ") + e.what());
  }
}

void PyMoneroConnectionManager::check_prioritized_connections(std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
  for (const auto &prioritized_connections : get_connections_in_ascending_priority()) {
    if (excluded_connections.has_value()) {
      std::set<std::shared_ptr<PyMoneroRpcConnection>> ex(excluded_connections.value().begin(), excluded_connections.value().end());
      check_connections(prioritized_connections, ex);
    }
    else { check_connections(prioritized_connections, {}); }
  }
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
  for (const auto& conn : responses) {
    if (m_response_times.find(conn) == m_response_times.end()) {
      m_response_times[conn] = {};
    }
  }

  for (auto& [conn, times] : m_response_times) {
    if (std::find(responses.begin(), responses.end(), conn) != responses.end()) {
      times.insert(times.begin(), conn->m_response_time);
    } else {
      times.insert(times.begin(), boost::none);
    }

    if (times.size() > MIN_BETTER_RESPONSES) {
      times.pop_back();
    }
  }

  return update_best_connection_in_priority();
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
  std::shared_ptr<PyMoneroRpcConnection> best_response = std::shared_ptr<PyMoneroRpcConnection>(nullptr);

  for (const auto& conn : responses) {
    if (conn->is_connected()) {
      if (!best_response || conn->m_response_time < best_response->m_response_time) {
        best_response = conn;
      }
    }
  }

  if (!best_response) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);

  auto best_connection = get_connection();
  if (!best_connection || !best_connection->is_connected()) {
    return best_response;
  }

  if (PyMoneroConnectionPriorityComparator::compare(best_response->m_priority, best_connection->m_priority) != 0) {
    return best_response;
  }

  if (m_response_times.find(best_connection) == m_response_times.end()) {
    return best_connection;
  }

  for (const auto& conn : responses) {
    if (conn == best_connection) continue;

    auto it_best = m_response_times.find(best_connection);
    auto it_curr = m_response_times.find(conn);
    if (it_curr == m_response_times.end()) continue;
    if (it_curr->second.size() < MIN_BETTER_RESPONSES || it_best->second.size() < MIN_BETTER_RESPONSES) continue;

    bool consistently_better = true;
    for (int i = 0; i < MIN_BETTER_RESPONSES; ++i) {
      auto curr_time = it_curr->second[i];
      auto best_time = it_best->second[i];
      if (!curr_time.has_value() || !best_time.has_value() || curr_time.value() > best_time.value()) {
        consistently_better = false;
        break;
      }
    }

    if (consistently_better) {
      best_connection = conn;
    }
  }

  return best_connection;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::update_best_connection_in_priority() {
  if (!m_auto_switch) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);

  for (const auto& prioritized_connections : get_connections_in_ascending_priority()) {
    auto best_conn = get_best_connection_from_prioritized_responses(prioritized_connections);
    if (best_conn != nullptr) {
      set_connection(best_conn);
      return best_conn;
    }
  }

  return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
}
