#include "common/py_monero_common.h"

enum PyMoneroKeyImageSpentStatus : uint8_t {
  NOT_SPENT = 0,
  CONFIRMED,
  TX_POOL
};

class PyMoneroBlockHeader : public monero::monero_block_header {
public:
  
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block_header>& header) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("block_header")) {
        from_property_tree(it->second, header);
      }
      else if (key == std::string("hash")) header->m_hash = it->second.data();
      else if (key == std::string("height")) header->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("timestamp")) header->m_timestamp = it->second.get_value<uint64_t>();
      else if (key == std::string("size")) header->m_size = it->second.get_value<uint64_t>();
      else if (key == std::string("weight")) header->m_weight = it->second.get_value<uint64_t>();
      else if (key == std::string("long_term_weight")) header->m_long_term_weight = it->second.get_value<uint64_t>();
      else if (key == std::string("depth")) header->m_depth = it->second.get_value<uint64_t>();
      else if (key == std::string("difficulty")) header->m_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("cumulative_difficulty")) header->m_cumulative_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("major_version")) header->m_major_version = it->second.get_value<uint32_t>();
      else if (key == std::string("minor_version")) header->m_minor_version = it->second.get_value<uint32_t>();
      else if (key == std::string("nonce")) header->m_nonce = it->second.get_value<uint32_t>();
      else if (key == std::string("miner_tx_hash")) header->m_miner_tx_hash = it->second.data();
      else if (key == std::string("num_txes")) header->m_orphan_status = it->second.get_value<uint32_t>();
      else if (key == std::string("orphan_status")) header->m_orphan_status = it->second.get_value<bool>();
      else if (key == std::string("prev_hash")) header->m_prev_hash = it->second.data();
      else if (key == std::string("reward")) header->m_reward = it->second.get_value<uint64_t>();
      else if (key == std::string("pow_hash")) header->m_pow_hash = it->second.data();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_block_header>>& headers) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      
      if (key == std::string("headers")) {
        auto node2 = it->second;

        for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto header = std::make_shared<monero::monero_block_header>();
          PyMoneroBlockHeader::from_property_tree(node2, header);
          headers.push_back(header);
        }
      }
    }
  }
};

class PyMoneroBlock : public PyMoneroBlockHeader {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block>& block) {
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
          monero::monero_tx::from_property_tree(tx_node.second, tx);
          block->m_txs.push_back(tx);
        }
      }
      else if (key == std::string("miner_tx")) {
        auto tx = std::make_shared<monero::monero_tx>();
        monero::monero_tx::from_property_tree(it->second, tx);
        block->m_miner_tx = tx;
      }
    }
  }
};

class PyMoneroTx : public monero::monero_tx {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx>& tx) {
    throw std::runtime_error("PyMoneroTx::from_property_tree(): not implemented");
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_tx>>& txs) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      
      if (key == std::string("txs")) {
        auto node2 = it->second;

        for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = std::make_shared<monero::monero_tx>();
          from_property_tree(node2, tx);
          txs.push_back(tx);
        }
      }
    }
  }
};

class PyMoneroTxHashes {
public:
  
  static std::vector<std::string> from_property_tree(const boost::property_tree::ptree& node) {
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
};

class PyMoneroOutput : public monero::monero_output {
public:

  void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output>& output) {
    throw std::runtime_error("PyMoneroOutput::from_property_tree(): not implemented");
  }
};

// #region JSON-RPC

class PyMoneroRequestParams : public PySerializableStruct {
public:
  PyMoneroRequestParams() { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroRequestEmptyParams : public PyMoneroRequestParams {
  public:
    PyMoneroRequestEmptyParams() {}
  
    rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
  };

class PyMoneroDownloadUpdateParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_command;
  boost::optional<std::string> m_path;

  PyMoneroDownloadUpdateParams() {
    m_command = "download";
  }

  PyMoneroDownloadUpdateParams(std::string path) {
    m_command = "download";
    m_path = m_path;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);

    if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
    if (m_path != boost::none) monero_utils::add_json_member("path", m_path.get(), allocator, root, value_str);

    return root;
  };

};

class PyMoneroCheckUpdateParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_command;

  PyMoneroCheckUpdateParams() {
    m_command = "check";
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
    return root;
  };

};

class PyMoneroStartMiningParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<int> m_num_threads;
  boost::optional<bool> m_is_background;
  boost::optional<bool> m_ignore_battery;

  PyMoneroStartMiningParams() {}
  PyMoneroStartMiningParams(std::string address, int num_threads, bool is_background, bool ignore_battery) {
    m_address = address;
    m_num_threads = num_threads;
    m_is_background = is_background;
    m_ignore_battery = ignore_battery;
  }
  PyMoneroStartMiningParams(int num_threads, bool is_background, bool ignore_battery) {
    m_num_threads = num_threads;
    m_is_background = is_background;
    m_ignore_battery = ignore_battery;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_address != boost::none) monero_utils::add_json_member("miner_address", m_address.get(), allocator, root, value_str);
    if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);
    if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
    if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);
    return root;
  };
};

class PyMoneroJsonRequestParams : public PyMoneroRequestParams {
public:
  PyMoneroJsonRequestParams() { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroJsonRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroJsonRequestEmptyParams : public PyMoneroJsonRequestParams {
public:
  PyMoneroJsonRequestEmptyParams() {}

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
};

class PyMoneroRequest : public PySerializableStruct {
public:
  boost::optional<std::string> m_method;

  PyMoneroRequest() { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroRequest::to_rapid_json_value(): not implemented"); };
};

class PyMoneroPathRequest : public PyMoneroRequest {
public:
  boost::optional<std::shared_ptr<PyMoneroRequestParams>> m_params;

  PyMoneroPathRequest() { }
  
  PyMoneroPathRequest(std::string method) {
    m_method = method;
    m_params = std::make_shared<PyMoneroRequestEmptyParams>();
  }

  PyMoneroPathRequest(std::string method, std::shared_ptr<PyMoneroRequestParams> params) {
    m_method = method;
    m_params = params;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    if (m_params != boost::none) return m_params.get()->to_rapidjson_val(allocator);
    throw std::runtime_error("No params provided");
  };
};

class PyMoneroJsonRequest : public PyMoneroRequest {
public:
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_id;
  boost::optional<std::shared_ptr<PyMoneroJsonRequestParams>> m_params;

  PyMoneroJsonRequest() {
    m_version = "2.0";
    m_id = "0";
    m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
  }

  PyMoneroJsonRequest(const PyMoneroJsonRequest& request) {
    m_version = request.m_version;
    m_id = request.m_id;
    m_method = request.m_method;
    m_params = request.m_params;
  }

  PyMoneroJsonRequest(std::string method) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
  }

  PyMoneroJsonRequest(std::string method, std::shared_ptr<PyMoneroJsonRequestParams> params) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    m_params = params;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);

    if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
    if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
    if (m_method != boost::none) monero_utils::add_json_member("method", m_method.get(), allocator, root, value_str);
    if (m_params != boost::none) root.AddMember("params", m_params.get()->to_rapidjson_val(allocator), allocator);

    return root;
  };
};

class PyMoneroPruneBlockchainParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_check;

  PyMoneroPruneBlockchainParams(bool check = true) {
    m_check = check;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_check != boost::none) monero_utils::add_json_member("check", m_check.get(), allocator, root);
    return root;
  };
};

class PyMoneroSubmitBlocksParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_block_blobs;

  PyMoneroSubmitBlocksParams() { }
  PyMoneroSubmitBlocksParams(const std::vector<std::string>& block_blobs) {
    m_block_blobs = block_blobs;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override {
    return monero_utils::to_rapidjson_val(allocator, m_block_blobs);
  }
};

class PyMoneroGetBlockParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_hash;
  boost::optional<bool> m_fill_pow_hash;

  PyMoneroGetBlockParams(uint64_t height, bool fill_pow_hash = false) {
    m_height = height;
    m_fill_pow_hash = fill_pow_hash;
  }

  PyMoneroGetBlockParams(std::string hash, bool fill_pow_hash = false) {
    m_hash = hash;
    m_fill_pow_hash = fill_pow_hash;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
  
    if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
    if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
    if (m_fill_pow_hash != boost::none) monero_utils::add_json_member("fill_pow_hash", m_fill_pow_hash.get(), allocator, root);

    return root; 
  }
};

class PyMoneroGetBlockRangeParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_start_height;
  boost::optional<uint64_t> m_end_height;

  PyMoneroGetBlockRangeParams() { }

  PyMoneroGetBlockRangeParams(uint64_t start_height, uint64_t end_height) {
    m_start_height = start_height;
    m_end_height = end_height;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
  
    if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);
    if (m_end_height != boost::none) monero_utils::add_json_member("end_height", m_end_height.get(), allocator, root, value_num);

    return root;
  }
};

class PyMoneroGetBlockHashParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_height;

  PyMoneroGetBlockHashParams() {}

  PyMoneroGetBlockHashParams(uint64_t height) {
    m_height = height;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override {
    std::vector<uint64_t> params;
    if (m_height != boost::none) params.push_back(m_height.get());
    return monero_utils::to_rapidjson_val(allocator, params);
  }
};

class PyMoneroGetBlockTemplateParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_wallet_address;
  boost::optional<int> m_reserve_size;

  PyMoneroGetBlockTemplateParams() { }
  
  PyMoneroGetBlockTemplateParams(std::string wallet_address) {
    m_wallet_address = wallet_address;
  }

  PyMoneroGetBlockTemplateParams(std::string wallet_address, int reserve_size) {
    m_wallet_address = wallet_address;
    m_reserve_size = reserve_size;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
  
    if (m_wallet_address != boost::none) monero_utils::add_json_member("wallet_address", m_wallet_address.get(), allocator, root, value_str);
    if (m_reserve_size != boost::none) monero_utils::add_json_member("reserve_size", m_reserve_size.get(), allocator, root, value_num);

    return root; 
  }

};

class PyMoneroJsonResponse {
public:
  boost::optional<std::string> m_jsonrpc;
  boost::optional<std::string> m_id;
  boost::optional<boost::property_tree::ptree> m_result;

  static std::shared_ptr<PyMoneroJsonResponse> deserialize(const std::string& response_json) {
    // deserialize json to property node
    std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
    boost::property_tree::ptree node;
    boost::property_tree::read_json(iss, node);

    auto response = std::make_shared<PyMoneroJsonResponse>();

    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("error")) {
        for (auto it_err = it->second.begin(); it_err != it->second.end(); ++it_err) {
          std::string key_err = it_err->first;
          if (key_err == std::string("message")) {
            throw std::runtime_error(it_err->second.data());
          }
        }
        throw std::runtime_error("Unkown JSON RPC error");
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
      else py::print(std::string("WARNING MoneroJsonResponse::deserialize() unrecognized key: ") + key);
    }

    return response;
  }
  
  PyMoneroJsonResponse() {
    m_jsonrpc = "2.0";
    m_id = "0";
  }

  PyMoneroJsonResponse(const PyMoneroJsonResponse& response) {
    m_jsonrpc = response.m_jsonrpc;
    m_id = response.m_id;
    m_result = response.m_result;
  }

  PyMoneroJsonResponse(boost::optional<boost::property_tree::ptree> &result) {
    m_jsonrpc = "2.0";
    m_id = "0";
    m_result = result;
  }

  std::optional<py::object> get_result() const {
    std::optional<py::object> res;
    if (m_result != boost::none) res = PyGenUtils::ptree_to_pyobject(m_result.get());
    return res;
  }

};

class PyMoneroPathResponse {
public:
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroPathResponse() { }

  PyMoneroPathResponse(const PyMoneroPathResponse& response) {
    m_response = response.m_response;
  }

  std::optional<py::object> get_response() const {
    std::optional<py::object> res;
    if (m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(m_response.get());
    return res;
  }
};

class PyMoneroVersion : public monero::monero_version {
public:
  PyMoneroVersion() {}
  PyMoneroVersion(uint32_t number, bool is_release) {
    m_number = number;
    m_is_release = is_release;
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroVersion>& version) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("version")) version->m_number = it->second.get_value<uint32_t>();
      else if (key == std::string("release")) version->m_is_release = it->second.get_value<bool>();
    }
  }
};

class PyMoneroAltChain {
public:
  std::vector<std::string> m_block_hashes;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_length;
  boost::optional<std::string> m_main_chain_parent_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAltChain>& alt_chain) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("difficulty")) alt_chain->m_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("block_hashes")) {
        for (const auto& child : it->second) alt_chain->m_block_hashes.push_back(child.second.data());
      }
      else if (key == std::string("height")) alt_chain->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("length")) alt_chain->m_length = it->second.get_value<uint64_t>();
      else if (key == std::string("main_chain_parent_block_hash")) alt_chain->m_main_chain_parent_block_hash = it->second.data();
    }
  }
};

class PyMoneroGetBlockCountResult {
public:
  boost::optional<uint64_t> m_count;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBlockCountResult>& result) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("count")) result->m_count = it->second.get_value<uint64_t>();
    }
  }
};

class PyMoneroBan : public PySerializableStruct {
public:
  boost::optional<std::string> m_host;
  boost::optional<int> m_ip;
  boost::optional<bool> m_is_banned;
  boost::optional<uint64_t> m_seconds;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_host != boost::none) monero_utils::add_json_member("host", m_host.get(), allocator, root, value_str);
    if (m_ip != boost::none) monero_utils::add_json_member("ip", m_ip.get(), allocator, root, value_num);
    if (m_is_banned != boost::none) monero_utils::add_json_member("ban", m_is_banned.get(), allocator, root);
    if (m_seconds != boost::none) monero_utils::add_json_member("seconds", m_seconds.get(), allocator, root, value_num);
    return root;
  };

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBan>& ban) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("host")) ban->m_host = it->second.data();
      else if (key == std::string("ip")) ban->m_ip = it->second.get_value<int>();
      else if (key == std::string("ban")) ban->m_is_banned = it->second.get_value<bool>();
      else if (key == std::string("seconds")) ban->m_seconds = it->second.get_value<uint64_t>();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroBan>>& bans) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("bans")) {
        auto node2 = it->second;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto ban = std::make_shared<PyMoneroBan>();
          PyMoneroBan::from_property_tree(node2, ban);
          bans.push_back(ban);
        }
      }
    }
  }
};

class PyMoneroPruneResult {
public:
  boost::optional<bool> m_is_pruned;
  boost::optional<int> m_pruning_seed;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPruneResult>& result) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("pruned")) result->m_is_pruned = it->second.get_value<bool>();
      else if (key == std::string("pruning_seed")) result->m_pruning_seed = it->second.get_value<int>();
    }
  }
};

class PyMoneroMiningStatus {
public:
  boost::optional<bool> m_is_active;
  boost::optional<bool> m_is_background;
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_speed;
  boost::optional<int> m_num_threads;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMiningStatus>& status) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("active")) status->m_is_active = it->second.get_value<bool>();
      else if (key == std::string("is_background_mining_enabled")) status->m_is_background = it->second.get_value<bool>();
      else if (key == std::string("address")) status->m_address = it->second.data();
      else if (key == std::string("speed")) status->m_speed = it->second.get_value<uint64_t>();
      else if (key == std::string("threads_count")) status->m_num_threads = it->second.get_value<int>();
    }
  }
};

class PyMoneroMinerTxSum {
public:
  boost::optional<uint64_t> m_emission_sum;
  boost::optional<uint64_t> m_fee_sum;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMinerTxSum>& sum) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("emission_sum")) sum->m_emission_sum = it->second.get_value<uint64_t>();
      else if (key == std::string("fee_sum")) sum->m_fee_sum = it->second.get_value<uint64_t>();
    }
  }
};

class PyMoneroBlockTemplate {
public:
  boost::optional<std::string> m_block_template_blob;
  boost::optional<std::string> m_block_hashing_blob;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_expected_reward;
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_prev_hash;
  boost::optional<uint64_t> m_reserved_offset;
  boost::optional<uint64_t> m_seed_height;
  boost::optional<std::string> m_seed_hash;
  boost::optional<std::string> m_next_seed_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBlockTemplate>& tmplt) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("blocktemplate_blob")) tmplt->m_block_template_blob = it->second.data();
      else if (key == std::string("blockhashing_blob")) tmplt->m_block_hashing_blob = it->second.data();
      else if (key == std::string("difficulty")) tmplt->m_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("expected_reward")) tmplt->m_expected_reward = it->second.get_value<uint64_t>();
      else if (key == std::string("height")) tmplt->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("prev_hash")) tmplt->m_prev_hash = it->second.data();
      else if (key == std::string("reserved_offset")) tmplt->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("seed_height")) tmplt->m_seed_height = it->second.get_value<uint64_t>();
      else if (key == std::string("seed_hash")) tmplt->m_seed_hash = it->second.data();
      else if (key == std::string("next_seed_hash")) tmplt->m_next_seed_hash = it->second.data();
    }
  }
};

class PyMoneroConnectionSpan {
public:
  boost::optional<std::string> m_connection_id;
  boost::optional<uint64_t> m_num_blocks;
  boost::optional<std::string> m_remote_address;
  boost::optional<uint64_t> m_rate;
  boost::optional<uint64_t> m_speed;
  boost::optional<uint64_t> m_size;
  boost::optional<uint64_t> m_start_height;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroConnectionSpan>& span) {
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
};

class PyMoneroPeer {
public:
  boost::optional<std::string> m_id;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_host;
  boost::optional<int> m_port;
  boost::optional<bool> m_is_online;
  boost::optional<uint64_t> m_last_seen_timestamp;
  boost::optional<int> m_pruning_seed;
  boost::optional<int> m_rpc_port;
  boost::optional<uint64_t> m_rpc_credits_per_hash;
  boost::optional<std::string> m_hash;
  boost::optional<uint64_t> m_avg_download;
  boost::optional<uint64_t> m_avg_upload;
  boost::optional<uint64_t> m_current_download;
  boost::optional<uint64_t> m_current_upload;
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_is_incoming;
  boost::optional<uint64_t> m_live_time;
  boost::optional<bool> m_is_local_ip;
  boost::optional<bool> m_is_local_host;
  boost::optional<int> m_num_receives;
  boost::optional<int> m_num_sends;
  boost::optional<uint64_t> m_receive_idle_time;
  boost::optional<uint64_t> m_send_idle_time;
  boost::optional<std::string> m_state;
  boost::optional<int> m_num_support_flags;
  boost::optional<PyMoneroConnectionType> m_connection_type;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPeer>& peer) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("host")) peer->m_host = it->second.data();
      else if (key == std::string("id")) peer->m_id = it->second.data();
      else if (key == std::string("last_seen")) peer->m_last_seen_timestamp = it->second.get_value<uint64_t>();
      else if (key == std::string("port")) peer->m_port = it->second.get_value<int>();
      else if (key == std::string("rpc_port")) peer->m_rpc_port = it->second.get_value<int>();
      else if (key == std::string("pruning_seed")) peer->m_pruning_seed = it->second.get_value<int>();
      else if (key == std::string("rpc_credits_per_hash")) peer->m_rpc_credits_per_hash = it->second.get_value<uint64_t>();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroPeer>>& peers) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      bool is_online = key == std::string("white_list");
      if (key == std::string("connections") || is_online || key == std::string("gray_list") ) {
        auto node2 = it->second;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto peer = std::make_shared<PyMoneroPeer>();
          PyMoneroPeer::from_property_tree(node2, peer);
          peer->m_is_online = is_online;
          peers.push_back(peer);
        }
      }
    }
  }
};

class PyMoneroSubmitTxResult {
public:
  boost::optional<bool> m_is_good;
  boost::optional<bool> m_is_relayed;
  boost::optional<bool> m_is_double_spend;
  boost::optional<bool> m_is_fee_too_low;
  boost::optional<bool> m_is_mixin_too_low;
  boost::optional<bool> m_has_invalid_input;
  boost::optional<bool> m_has_invalid_output;
  boost::optional<bool> m_has_too_few_outputs;
  boost::optional<bool> m_is_overspend;
  boost::optional<bool> m_is_too_big;
  boost::optional<bool> m_sanity_check_failed;
  boost::optional<std::string> m_reason;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;
  boost::optional<bool> m_is_tx_extra_too_big;
  boost::optional<bool> m_is_nonzero_unlock_time;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroSubmitTxResult>& result) {
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
      else if (key == std::string("top_hash")) result->m_top_block_hash = it->second.data();
      else if (key == std::string("tx_extra_too_big")) result->m_is_tx_extra_too_big = it->second.get_value<bool>();
      else if (key == std::string("nonzero_unlock_time")) result->m_is_nonzero_unlock_time = it->second.get_value<bool>();
    }
  }

};

class PyMoneroSubmitTxParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_tx_hex;
  boost::optional<bool> m_do_not_relay;

  PyMoneroSubmitTxParams() {}
  PyMoneroSubmitTxParams(std::string tx_hex, bool do_not_relay) {
    m_tx_hex = tx_hex;
    m_do_not_relay = do_not_relay;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tx_hex != boost::none) monero_utils::add_json_member("tx_as_hex", m_tx_hex.get(), allocator, root, value_str);
    if (m_do_not_relay != boost::none) monero_utils::add_json_member("do_not_relay", m_do_not_relay.get(), allocator, root);
    return root; 
  }
};

class PyMoneroRelayTxParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;

  PyMoneroRelayTxParams() {}
  PyMoneroRelayTxParams(const std::vector<std::string> tx_hashes) {
    m_tx_hashes = tx_hashes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
    return root; 
  }
};

class PyMoneroTxBacklogEntry {
  // TODO
};

class PyMoneroOutputDistributionEntry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<int> m_base;
  std::vector<int> m_distribution;
  boost::optional<uint64_t> m_start_height;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputDistributionEntry>& entry) {
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
};

class PyMoneroOutputHistogramEntry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<uint64_t> m_num_instances;
  boost::optional<uint64_t> m_unlocked_instances;
  boost::optional<uint64_t> m_recent_instances;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputHistogramEntry>& entry) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("amount")) entry->m_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("total_instances")) entry->m_num_instances = it->second.get_value<uint64_t>();
      else if (key == std::string("unlocked_instances")) entry->m_unlocked_instances = it->second.get_value<uint64_t>();
      else if (key == std::string("recent_instances")) entry->m_recent_instances = it->second.get_value<uint64_t>();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>>& entries) {
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

};

class PyMoneroTxPoolStats {
public:
  boost::optional<int> m_num_txs;
  boost::optional<int> m_num_not_relayed;
  boost::optional<int> m_num_failing;
  boost::optional<int> m_num_double_spends;
  boost::optional<int> m_num10m;
  boost::optional<uint64_t> m_fee_total;
  boost::optional<uint64_t> m_bytes_max;
  boost::optional<uint64_t> m_bytes_med;
  boost::optional<uint64_t> m_bytes_min;
  boost::optional<uint64_t> m_bytes_total;
  //private Map<Long, Integer> histo;
  boost::optional<uint64_t> m_histo98pc;
  boost::optional<uint64_t> m_oldest_timestamp;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroTxPoolStats>& stats) {
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

};

class PyMoneroDaemonUpdateCheckResult {
public:
  boost::optional<bool> m_is_update_available;
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_hash;
  boost::optional<std::string> m_auto_uri;
  boost::optional<std::string> m_user_uri;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateCheckResult>& check) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("update")) check->m_is_update_available = it->second.get_value<bool>();
      else if (key == std::string("version")) check->m_version = it->second.data();
      else if (key == std::string("hash")) check->m_hash = it->second.data();
      else if (key == std::string("auto_uri")) check->m_auto_uri = it->second.data();
      else if (key == std::string("user_uri")) check->m_user_uri = it->second.data();
    }
  }
};

class PyMoneroDaemonUpdateDownloadResult : public PyMoneroDaemonUpdateCheckResult {
public:
  boost::optional<std::string> m_download_path;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateDownloadResult>& check) {
    PyMoneroDaemonUpdateCheckResult::from_property_tree(node, check);
    
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("download_path")) check->m_download_path = it->second.data();
    }
  }
};

class PyMoneroFeeEstimate {
public:
  boost::optional<uint64_t> m_fee;
  std::vector<uint64_t> m_fees;
  boost::optional<uint64_t> m_quantization_mask;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroFeeEstimate>& estimate) {    
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
};

class PyMoneroDaemonInfo {
public:
  boost::optional<std::string> m_version;
  boost::optional<uint64_t> m_num_alt_blocks;
  boost::optional<uint64_t> m_block_size_limit;
  boost::optional<uint64_t> m_block_size_median;
  boost::optional<uint64_t> m_block_weight_limit;
  boost::optional<uint64_t> m_block_weight_median;
  boost::optional<std::string> m_bootstrap_daemon_address;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_cumulative_difficulty;
  boost::optional<uint64_t> m_free_space;
  boost::optional<int> m_num_offline_peers;
  boost::optional<int> m_num_online_peers;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_height_without_bootstrap;
  boost::optional<monero::monero_network_type> m_network_type;
  boost::optional<bool> m_is_offline;
  boost::optional<int> m_num_incoming_connections;
  boost::optional<int> m_num_outgoing_connections;
  boost::optional<int> m_num_rpc_connections;
  boost::optional<uint64_t> m_start_timestamp;
  boost::optional<uint64_t> m_adjusted_timestamp;
  boost::optional<uint64_t> m_target;
  boost::optional<uint64_t> m_target_height;
  boost::optional<std::string> m_top_block_hash;
  boost::optional<int> m_num_txs;
  boost::optional<int> m_num_txs_pool;
  boost::optional<bool> m_was_bootstrap_ever_used;
  boost::optional<uint64_t> m_database_size;
  boost::optional<bool> m_update_available;
  boost::optional<uint64_t> m_credits;
  boost::optional<bool> m_is_busy_syncing;
  boost::optional<bool> m_is_synchronized;
  boost::optional<bool> m_is_restricted;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonInfo>& info) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("version")) info->m_version = it->second.data();
      else if (key == std::string("num_alt_blocks")) info->m_num_alt_blocks = it->second.get_value<uint64_t>();
      else if (key == std::string("block_size_limit")) info->m_block_size_limit = it->second.get_value<uint64_t>();
      else if (key == std::string("block_size_median")) info->m_block_size_median = it->second.get_value<uint64_t>();
      else if (key == std::string("block_weight_limit")) info->m_block_weight_limit = it->second.get_value<uint64_t>();
      else if (key == std::string("block_weight_median")) info->m_block_weight_median = it->second.get_value<uint64_t>();
      else if (key == std::string("bootstrap_daemon_address")) info->m_bootstrap_daemon_address = it->second.data();
      else if (key == std::string("difficulty")) info->m_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("cumulative_difficulty")) info->m_cumulative_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("free_space")) info->m_free_space = it->second.get_value<uint64_t>();
      else if (key == std::string("num_offline_peers")) info->m_num_offline_peers = it->second.get_value<int>();
      else if (key == std::string("num_online_peers")) info->m_num_online_peers = it->second.get_value<int>();
      else if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("height_without_bootstrap")) info->m_height_without_bootstrap = it->second.get_value<uint64_t>();
      else if (key == std::string("nettype")) {
        std::string nettype = it->second.data();
        if (nettype == std::string("mainnet")) {
          info->m_network_type = monero::monero_network_type::MAINNET;
        }
        else if (nettype == std::string("testnet")) {
          info->m_network_type = monero::monero_network_type::TESTNET;
        }
        else if (nettype == std::string("stagenet")) {
          info->m_network_type = monero::monero_network_type::STAGENET;
        }
      }
      else if (key == std::string("offline")) info->m_is_offline = it->second.get_value<bool>();
      else if (key == std::string("incoming_connections_count")) info->m_num_incoming_connections = it->second.get_value<int>();
      else if (key == std::string("outgoing_connections_count")) info->m_num_outgoing_connections = it->second.get_value<int>();
      else if (key == std::string("rpc_connections_count")) info->m_num_rpc_connections = it->second.get_value<int>();
      else if (key == std::string("start_time")) info->m_start_timestamp = it->second.get_value<uint64_t>();
      else if (key == std::string("adjusted_time")) info->m_adjusted_timestamp = it->second.get_value<uint64_t>();
      else if (key == std::string("target")) info->m_target = it->second.get_value<uint64_t>();
      else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
      else if (key == std::string("top_block_hash")) info->m_top_block_hash = it->second.data();
      else if (key == std::string("num_txs")) info->m_num_txs = it->second.get_value<int>();
      else if (key == std::string("num_txs_pool")) info->m_num_txs_pool = it->second.get_value<int>();
      else if (key == std::string("was_bootstrap_ever_used")) info->m_was_bootstrap_ever_used = it->second.get_value<bool>();
      else if (key == std::string("database_size")) info->m_database_size = it->second.get_value<uint64_t>();
      else if (key == std::string("update_available")) info->m_update_available = it->second.get_value<bool>();
      else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
      else if (key == std::string("busy_syncing")) info->m_is_busy_syncing = it->second.get_value<bool>();
      else if (key == std::string("synchronized")) info->m_is_synchronized = it->second.get_value<bool>();
      else if (key == std::string("restricted")) info->m_is_restricted = it->second.get_value<bool>();
    }
  }
};

class PyMoneroDaemonSyncInfo {
public:
  boost::optional<uint64_t> m_height;
  std::vector<PyMoneroPeer> m_peers;
  std::vector<PyMoneroConnectionSpan> m_spans;
  boost::optional<uint64_t> m_target_height;
  boost::optional<int> m_next_needed_pruning_seed;
  boost::optional<std::string> m_overview;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonSyncInfo>& info) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
      else if (key == std::string("next_needed_pruning_seed")) info->m_next_needed_pruning_seed = it->second.get_value<int>();
      else if (key == std::string("overview")) info->m_overview = it->second.data();
      else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
      else if (key == std::string("top_hash")) info->m_top_block_hash = it->second.data();
    }
  }
};

class PyMoneroHardForkInfo {
public:
  boost::optional<uint64_t> m_earliest_height;
  boost::optional<bool> m_is_enabled;
  boost::optional<int> m_state;
  boost::optional<int> m_threshold;
  boost::optional<int> m_version;
  boost::optional<int> m_num_votes;
  boost::optional<int> m_window;
  boost::optional<int> m_voting;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroHardForkInfo>& info) {
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
      else if (key == std::string("top_hash")) info->m_top_block_hash = it->second.data();
    }
  }
};

class PyMoneroGetAltBlocksHashesResponse {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes) {
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
};

class PyMoneroBandwithLimits : public PyMoneroRequestParams {
public:
  boost::optional<int> m_up;
  boost::optional<int> m_down;

  PyMoneroBandwithLimits() {}
  PyMoneroBandwithLimits(int up, int down) {
    m_up = up;
    m_down = down;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_up != boost::none) monero_utils::add_json_member("limit_up", m_up.get(), allocator, root, value_num);
    if (m_down != boost::none) monero_utils::add_json_member("limit_down", m_down.get(), allocator, root, value_num);
    return root; 
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBandwithLimits>& limits) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("limit_up")) limits->m_up = it->second.get_value<int>();
      else if (key == std::string("limit_down")) limits->m_down = it->second.get_value<int>();
    }
  }
};

class PyMoneroPeerLimits : public PyMoneroRequestParams {
public:
  boost::optional<int> m_in_peers;
  boost::optional<int> m_out_peers;

  PyMoneroPeerLimits() {}
  PyMoneroPeerLimits(int in, int out) {
    m_in_peers = in;
    m_out_peers = out;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_in_peers != boost::none) monero_utils::add_json_member("in_peers", m_in_peers.get(), allocator, root, value_num);
    if (m_out_peers != boost::none) monero_utils::add_json_member("out_peers", m_out_peers.get(), allocator, root, value_num);
    return root; 
  }
};

class PyMoneroGetHeightResponse {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_untrusted;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetHeightResponse>& response) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("height")) response->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("untrusted")) response->m_untrusted = it->second.get_value<bool>();
    }
  }
};

class PyMoneroGetMinerTxSumParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_count;
  
  PyMoneroGetMinerTxSumParams() {}
  PyMoneroGetMinerTxSumParams(uint64_t height, uint64_t count) {
    m_height = height;
    m_count = count;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
    if (m_count != boost::none) monero_utils::add_json_member("count", m_count.get(), allocator, root, value_num);
    return root; 
  }

};

class PyMoneroGetFeeEstimateParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_grace_blocks;
  
  PyMoneroGetFeeEstimateParams(uint64_t grace_blocks = 0) {
    m_grace_blocks = grace_blocks;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_grace_blocks != boost::none) monero_utils::add_json_member("grace_blocks", m_grace_blocks.get(), allocator, root, value_num);
    return root; 
  }
};

class PyMoneroSetBansParams : public PyMoneroRequestParams {
public:
  std::vector<std::shared_ptr<PyMoneroBan>> m_bans;

  PyMoneroSetBansParams() {}
  PyMoneroSetBansParams(const std::vector<std::shared_ptr<PyMoneroBan>>& bans) {
    m_bans = bans;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_bans.empty()) root.AddMember("bans", monero_utils::to_rapidjson_val(allocator, m_bans), allocator);
    return root; 
  }
};

class PyMoneroGetTxsParams : public PyMoneroRequestParams {
public:
  std::vector<std::string> m_tx_hashes;
  boost::optional<bool> m_decode_as_json;
  boost::optional<bool> m_prune;

  PyMoneroGetTxsParams(const std::vector<std::string> &tx_hashes, bool prune, bool decode_as_json = true) {
    m_tx_hashes = tx_hashes;
    m_prune = prune;
    m_decode_as_json = decode_as_json;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_tx_hashes.empty()) root.AddMember("txs_hashes", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
    if (m_prune != boost::none) monero_utils::add_json_member("prune", m_prune.get(), allocator, root);
    if (m_decode_as_json != boost::none) monero_utils::add_json_member("decode_as_json", m_decode_as_json.get(), allocator, root);
    return root; 
  }
};

class PyMoneroGetOutputHistrogramParams : public PyMoneroJsonRequestParams {
public:
  std::vector<uint64_t> m_amounts;
  boost::optional<int> m_min_count;
  boost::optional<int> m_max_count;
  boost::optional<bool> m_is_unlocked;
  boost::optional<int> m_recent_cutoff;

  PyMoneroGetOutputHistrogramParams(const std::vector<uint64_t> &amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) {
    m_amounts = amounts;
    m_min_count = min_count;
    m_max_count = max_count;
    m_is_unlocked = is_unlocked;
    m_recent_cutoff = recent_cutoff;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (!m_amounts.empty()) root.AddMember("amounts", monero_utils::to_rapidjson_val(allocator, m_amounts), allocator);
    if (m_min_count != boost::none) monero_utils::add_json_member("min_count", m_min_count.get(), allocator, root, value_num);
    if (m_max_count != boost::none) monero_utils::add_json_member("max_count", m_max_count.get(), allocator, root, value_num);
    if (m_is_unlocked != boost::none) monero_utils::add_json_member("is_unlocked", m_is_unlocked.get(), allocator, root);
    if (m_recent_cutoff != boost::none) monero_utils::add_json_member("recent_cutoff", m_recent_cutoff.get(), allocator, root, value_num);
    return root; 
  }
};

class PyMoneroIsKeyImageSpentParams : public PyMoneroRequestParams {
public:
  std::vector<std::string> m_key_images;
  PyMoneroIsKeyImageSpentParams(const std::vector<std::string> & key_images) {
    m_key_images = key_images;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_key_images.empty()) root.AddMember("key_images", monero_utils::to_rapidjson_val(allocator, m_key_images), allocator);
    return root; 
  }
};

class PyMoneroRpcConnection : public monero_rpc_connection {
public:
  boost::optional<std::string> m_zmq_uri;
  boost::optional<std::string> m_proxy;
  int m_priority;
  uint64_t m_timeout;
  boost::optional<long> m_response_time;

  static int compare(std::shared_ptr<PyMoneroRpcConnection> c1, std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection) {
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

  PyMoneroRpcConnection(const std::string& uri = "", const std::string& username = "", const std::string& password = "", const std::string& zmq_uri = "", int priority = 0, uint64_t timeout = 0) {
    m_uri = uri;
    m_username = username; 
    m_password = password;
    m_zmq_uri = zmq_uri;
    m_priority = priority;
    m_timeout = timeout;
    auto factory = new net::http::client_factory();
    m_http_client = factory->create();
  }

  PyMoneroRpcConnection(PyMoneroRpcConnection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_zmq_uri = rpc.m_zmq_uri;
    m_priority = rpc.m_priority;
    m_timeout = rpc.m_timeout;
    auto factory = new net::http::client_factory();
    m_http_client = factory->create();
  }

  PyMoneroRpcConnection(monero::monero_rpc_connection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_zmq_uri = "";
    m_priority = 0;
    m_timeout = 500;
    auto factory = new net::http::client_factory();
    m_http_client = factory->create();
  }

  bool is_onion() const {
    if (m_uri == boost::none) return false;

    if (m_uri && m_uri->size() >= 6 && m_uri->compare(m_uri->size() - 6, 6, ".onion") == 0) {
      return true;
    }

    return false;
  }

  bool is_i2p() const {
    if (m_uri == boost::none) return false;

    if (m_uri && m_uri->size() >= 8 && m_uri->compare(m_uri->size() - 8, 8, ".b32.i2p") == 0) {
      return true;
    }

    return false;
  }

  void set_credentials(const std::string& username, const std::string& password) {
    m_username = username;
    m_password = password;
  }

  void set_attribute(const std::string& key, const std::string& val) {
    m_attributes[key] = val;
  }

  std::string get_attribute(const std::string& key) {
    std::unordered_map<std::string, std::string>::const_iterator i = m_attributes.find(key);
    if (i == m_attributes.end())
      return std::string("");
    return i->second;
  }

  bool is_online() const {
    return m_is_online.value_or(false);
  }

  bool is_authenticated() const {
    return m_is_authenticated.value_or(false);
  }

  bool is_connected() const {
    if (!is_online()) return false;

    if (m_is_authenticated != boost::none) {
      return is_authenticated();
    }

    return true;
  }

  bool check_connection(int timeout_ms = 2000) {
    py::print("PyMoneroRpcConnection::check_connection()");
    bool is_online_before = is_online();
    bool is_authenticated_before = is_authenticated();
    boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
    try {
      if (m_http_client->is_connected()) {
        py::print("PyMoneroRpcConnection::check_connection(): disconnecting previous connection...");
        m_http_client->disconnect();
        py::print("PyMoneroRpcConnection::check_connection(): disconnetected previous connection");
      }

      if (m_proxy != boost::none) {
        py::print("PyMoneroRpcConnection::check_connection(): setting proxy...");
        if(!m_http_client->set_proxy(m_proxy.get())) {
          py::print("PyMoneroRpcConnection::check_connection(): could not set proxy");
          throw std::runtime_error("Could not set proxy");
        }
      }

      if(m_username != boost::none && !m_username->empty() && m_password != boost::none && !m_password->empty()) {
        py::print("PyMoneroRpcConnection::check_connection(): setting credentials");
        auto credentials = std::make_shared<epee::net_utils::http::login>();

        credentials->username = *m_username;
        credentials->password = *m_password;
    
        m_credentials = *credentials;
      }
      
      py::print(std::string("PyMoneroRpcConnection::check_connection(): setting server uri ") + m_uri.get());
      if (!m_http_client->set_server(m_uri.get(), m_credentials)) {
        py::print("PyMoneroRpcConnection::check_connection(): could not set rpc connection: " + m_uri.get());
        throw std::runtime_error("Could not set rpc connection: " + m_uri.get());
      }
      py::print("PyMoneroRpcConnection::check_connection(): connecting...");
      m_http_client->connect(std::chrono::seconds(timeout_ms));
      py::print("PyMoneroRpcConnection::check_connection(): connected");

      auto response = invoke_post("/get_info", "{}", std::chrono::milliseconds(timeout_ms));
      py::print("PyMoneroRpcConnection::check_connection(): got response");
      if (response->m_response_code != 200) {
        py::print("PyMoneroRpcConnection::check_connection(): request error");
        throw std::runtime_error("Request error");
      }

      m_is_online = true;
      m_is_authenticated = true;
      py::print("PyMoneroRpcConnection::check_connection(): NOW ONLINE");

      return is_online_before != is_online() || is_authenticated_before != is_authenticated();
    }
    catch (const std::exception& ex) {
      py::print(std::string("PyMoneroRpcConnection::check_connection(): AN ERROR OCCURED: ") + ex.what());
      m_is_online = false;
      m_is_authenticated = boost::none;
      return false;
    }
  }

  template<class t_request, class t_response>
  inline int invoke_post(const boost::string_ref uri, const t_request& request, t_response& res, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    if (!m_http_client) throw std::runtime_error("http client not set");

    rapidjson::Document document(rapidjson::Type::kObjectType);
    rapidjson::Value req = request.to_rapidjson_val(document.GetAllocator());
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    req.Accept(writer);
    std::string body = sb.GetString();

    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);

    int status_code = response->m_response_code;

    if (status_code == 200) {
    res = *t_response::deserialize(response->m_body);
    }

    return status_code;
  }

  inline const epee::net_utils::http::http_response_info* invoke_post(const boost::string_ref uri, const std::string& body, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    if (!m_http_client) throw std::runtime_error("http client not set");

    std::shared_ptr<epee::net_utils::http::http_response_info> _res = std::make_shared<epee::net_utils::http::http_response_info>();
    const epee::net_utils::http::http_response_info* response = _res.get();
    boost::lock_guard<boost::recursive_mutex> lock(m_mutex);

    if (!m_http_client->invoke_post(uri, body, timeout, &response)) {
    throw std::runtime_error("Network error");
    }

    return response;
  }

  inline const std::shared_ptr<PyMoneroJsonResponse> send_json_request(const PyMoneroJsonRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroJsonResponse response;

    int result = invoke_post("/json_rpc", request, response, timeout);

    if (result != 200) throw std::runtime_error("Network error");

    return std::make_shared<PyMoneroJsonResponse>(response);
  }

  inline const std::shared_ptr<PyMoneroPathResponse> send_path_request(const PyMoneroPathRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroPathResponse response;

    throw std::runtime_error("PyMoneroRpcConnection::send_path_request(): not implemented");

    return std::make_shared<PyMoneroPathResponse>(response);
  }

protected:
  mutable boost::recursive_mutex m_mutex;
  std::string m_server;
  boost::optional<epee::net_utils::http::login> m_credentials;
  std::unique_ptr<epee::net_utils::http::abstract_http_client> m_http_client;
  serializable_unordered_map<std::string, std::string> m_attributes;
  boost::optional<bool> m_is_online;
  boost::optional<bool> m_is_authenticated;
};

class PyMoneroConnectionManagerListener {
public:
  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection) {
    throw std::runtime_error("PyMoneroConnectionManagerListener::on_connection_changed(): not implemented");
  }
};

class PyMoneroConnectionManager {
public:
  PyMoneroConnectionManager(): m_timer(m_io_context) { }

  void add_listener(std::shared_ptr<PyMoneroConnectionManagerListener> &listener) {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.push_back(listener);
  }

  void remove_listener(std::shared_ptr<PyMoneroConnectionManagerListener> &listener) {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<PyMoneroConnectionManagerListener> iter){ return iter == listener; }), m_listeners.end());
  }

  void remove_listeners() {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.clear();
  }

  std::vector<std::shared_ptr<PyMoneroConnectionManagerListener>> get_listeners() {
    return m_listeners;
  }

  std::shared_ptr<PyMoneroRpcConnection> get_connection_by_uri(const std::string &uri) {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
    for(const auto &m_connection : m_connections) {
      if (m_connection->m_uri == uri) return m_connection;
    }

    return nullptr;
  }

  void add_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
    if (connection->m_uri == boost::none) throw std::runtime_error("Invalid connection uri");
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
    for(const auto &m_connection : m_connections) {
      if (m_connection->m_uri == connection->m_uri) throw std::runtime_error("Connection URI already exists with connection manager: " + connection->m_uri.get());
    }

    m_connections.push_back(connection);
  }

  void add_connection(const std::string &uri) {
    std::shared_ptr<PyMoneroRpcConnection> connection = std::make_shared<PyMoneroRpcConnection>();
    connection->m_uri = uri;
    add_connection(connection);
  }

  void remove_connection(const std::string &uri) {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

    std::shared_ptr<PyMoneroRpcConnection> connection = get_connection_by_uri(uri);

    if (connection == nullptr) throw std::runtime_error("Connection not found");
    
    m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == connection; }), m_connections.end());

    if (connection == m_current_connection) {
      m_current_connection = nullptr;
      on_connection_changed(m_current_connection);
    }
  }

  void set_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
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

  void set_connection(const std::string& uri) {
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

  std::shared_ptr<PyMoneroRpcConnection> get_connection() { return m_current_connection; }

  bool has_connection(const std::string& uri) {
    auto connection = get_connection_by_uri(uri);

    if (connection != nullptr) return true;
    return false;
  }

  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_connections() { return m_connections; }

  bool is_connected() {
    if (m_current_connection == nullptr) return false;
    return m_current_connection->is_connected();
  }

  void check_connection() {
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

  void set_auto_switch(bool auto_switch) {
    m_auto_switch = auto_switch;
  }

  void stop_polling() {
    throw std::runtime_error("PyMoneroDaemonConnectionManager::stop_polling(): not implemented");
  }

  void start_polling(std::optional<uint64_t> period_ms, std::optional<bool> auto_switch, std::optional<uint64_t> timeout_ms, std::optional<PyMoneroConnectionPollType> poll_type, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
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

  bool get_auto_switch() { return m_auto_switch; }

  void set_timeout(uint64_t timeout_ms) { m_timeout = timeout_ms; }

  uint64_t get_timeout() { return m_timeout; }

  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_peer_connections() { throw std::runtime_error("PyMoneroConnectionManagerListener::get_peer_connections(): not implemented"); }

  void disconnect() { set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr)); }

  void clear() {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

    m_connections.clear();

    if (m_current_connection != nullptr) {
      m_current_connection = nullptr;
      on_connection_changed(m_current_connection);
    }
  }

  void reset() {
    remove_listeners();
    stop_polling();
    clear();
    m_timeout = DEFAULT_TIMEOUT;
    m_auto_switch = DEFAULT_AUTO_SWITCH;
  }

  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {}) {
    int m_timeout = 2000;

    for (const auto& prioritizedConnections : get_connections_in_ascending_priority()) {
      try {
        std::vector<std::future<std::shared_ptr<PyMoneroRpcConnection>>> futures;

        for (const auto& connection : prioritizedConnections) {
          if (excluded_connections.count(connection)) continue;

          futures.push_back(std::async(std::launch::async, [connection, m_timeout]() {
            connection->check_connection(m_timeout);
            return connection;
          }));
        }

        for (auto& fut : futures) {
          try {
            auto conn = fut.get();
            if (conn->is_connected()) return conn;
          } catch (...) {
            
          }
        }

      } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Connection check error: ") + e.what());
      }
    }

    return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
  }

  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(std::shared_ptr<PyMoneroRpcConnection>& excluded_connection) {
    const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = { excluded_connection };
  
    return get_best_available_connection(excluded_connections);
  }

  void check_connections() {
    check_connections(get_connections());
  }

private:
  // static variables
  static const uint64_t DEFAULT_TIMEOUT = 5000;
  static const uint64_t DEFAULT_POLL_PERIOD = 20000;
  static const bool DEFAULT_AUTO_SWITCH = true;
  static const int MIN_BETTER_RESPONSES = 3;
  mutable boost::recursive_mutex m_listeners_mutex;
  mutable boost::recursive_mutex m_connections_mutex;
  std::vector<std::shared_ptr<PyMoneroConnectionManagerListener>> m_listeners;
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> m_connections;
  std::shared_ptr<PyMoneroRpcConnection> m_current_connection;
  bool m_auto_switch = true;
  uint64_t m_timeout;
  boost::asio::io_context m_io_context;
  boost::asio::steady_timer m_timer;
  std::map<std::shared_ptr<PyMoneroRpcConnection>, std::vector<boost::optional<long>>> m_response_times;

  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection) {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);

    for (const auto &listener : m_listeners) {
      listener->on_connection_changed(connection);
    }
  }

  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> get_connections_in_ascending_priority() {
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

  void start_polling_connection(uint64_t period_ms) {
    m_timer.expires_after(std::chrono::milliseconds(period_ms));
    m_timer.async_wait([this, period_ms](const boost::system::error_code& ec) {
      if (!ec) {
        try {
          check_connection();
        } catch (const std::exception& e) {
          std::cerr << "Error in check_connection: " << e.what() << std::endl;
        }
        start_polling_connection(period_ms);  // schedule next call
      }
    });
  }

  void start_polling_connections(uint64_t period_ms) {
    m_timer.expires_after(std::chrono::milliseconds(period_ms));
    m_timer.async_wait([this, period_ms](const boost::system::error_code& ec) {
      if (!ec) {
        try {
          check_connections();
        } catch (const std::exception& e) {
          std::cerr << "Error in check_connections: " << e.what() << std::endl;
        }
        start_polling_connections(period_ms);  // schedule next call
      }
    });
  }

  void start_polling_prioritized_connections(uint64_t period_ms, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
    throw std::runtime_error("not implmented");
  }

  bool check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {}) {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
    try {
      auto timeout_ms = m_timeout; // Impostabile come parametro o membro

      // Rimuoviamo il futures vector e usiamo post per task asincroni
      bool has_connection = false;
      boost::asio::io_context& io_context = m_io_context; // Assicurati di avere un io_context

      for (const auto& connection : connections) {
        if (excluded_connections.count(connection)) continue;

        boost::asio::post(io_context, [this, connection, timeout_ms, &has_connection]() {
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
        });
      }

    // Esegui il contesto asincrono
    io_context.run();

    // Processa le risposte
    process_responses(connections);
    return has_connection;
    } 
    catch (const std::exception& e) {
      throw std::runtime_error(std::string("check_connections failed: ") + e.what());
    }
  }

  std::shared_ptr<PyMoneroRpcConnection> process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
    // Aggiungi nuove connessioni a response_times
    for (const auto& conn : responses) {
      if (m_response_times.find(conn) == m_response_times.end()) {
        m_response_times[conn] = {};
      }
    }
  
    // Inserisci tempi di risposta o null
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

  std::shared_ptr<PyMoneroRpcConnection> get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
    std::shared_ptr<PyMoneroRpcConnection> best_response = std::shared_ptr<PyMoneroRpcConnection>(nullptr);

    for (const auto& conn : responses) {
      if (conn->is_connected()) {
        if (!best_response || conn->m_response_time < best_response->m_response_time) {
          best_response = conn;
        }
      }
    }

    if (!best_response) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);

    // Se la connessione attuale non esiste o è disconnessa, usa la nuova
    auto best_connection = get_connection();
    if (!best_connection || !best_connection->is_connected()) {
      return best_response;
    }

    // Confronta priorità: se sono diverse, usa la nuova
    if (PyMoneroConnectionPriorityComparator::compare(best_response->m_priority, best_connection->m_priority) != 0) {
      return best_response;
    }

    // Se non abbiamo dati per la connessione attuale, mantienila
    if (m_response_times.find(best_connection) == m_response_times.end()) {
      return best_connection;
    }

    // Controlla se un'altra connessione ha prestazioni consistentemente migliori
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

  std::shared_ptr<PyMoneroRpcConnection> update_best_connection_in_priority() {
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

};

class PyMoneroDaemonListener {
public:
  virtual void on_new_block(const std::shared_ptr<monero::monero_block_header> &header) {
    m_last_header = header;
  }

  std::shared_ptr<monero::monero_block_header> m_last_header;
};

class PyMoneroBlockNotifier : public PyMoneroDaemonListener {
public:
  boost::mutex* temp;
  boost::condition_variable* cv;
  PyMoneroBlockNotifier(boost::mutex* temp, boost::condition_variable* cv) { this->temp = temp; this->cv = cv; }
  void on_new_block(const std::shared_ptr<monero::monero_block_header> &header) override {
    m_last_header = header;
    cv->notify_one();
  }
};

class PyMoneroDaemon {

public:
  PyMoneroDaemon() {}
  virtual void add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroDaemonListener>> get_listeners() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void remove_listeners() { throw std::runtime_error("PyMoneroDaemon::remove_listeners(): not implemented"); };
  virtual monero::monero_version get_version() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual bool is_trusted() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual uint64_t get_height() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::string get_block_hash(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address, int reserve_size) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> get_last_block_header() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_hash(const std::string& hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_height(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_height(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_height(std::vector<uint64_t> heights) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range(std::optional<uint64_t> start_height, std::optional<uint64_t> end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range_chunked(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range_chunked(uint64_t start_height, uint64_t end_height, uint64_t max_chunk_size) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::string> get_block_hashes(std::vector<std::string> block_hashes, uint64_t start_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::optional<std::shared_ptr<monero::monero_tx>> get_tx(const std::string& tx_hash, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroMinerTxSum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroFeeEstimate> get_fee_estimate(uint64_t grace_blocks = 0) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroSubmitTxResult> submit_tx_hex(std::string& tx_hex, bool do_not_relay = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void relay_tx_by_hash(std::string& tx_hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void relay_txs_by_hash(std::vector<std::string>& tx_hashes) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_tx_pool() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::string> get_tx_pool_hashes() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<PyMoneroTxBacklogEntry> get_tx_pool_backlog() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroTxPoolStats> get_tx_pool_stats() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void flush_tx_pool() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void flush_tx_pool(const std::vector<std::string> &hashes) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual PyMoneroKeyImageSpentStatus get_key_image_spent_status(std::string& key_image) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<PyMoneroKeyImageSpentStatus> get_key_image_spent_statuses(std::vector<std::string>& key_images) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_output>> get_outputs(std::vector<monero::monero_output>& outputs) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> get_output_histogram(std::vector<uint64_t> amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputDistributionEntry>> get_output_distribution(std::vector<uint64_t> amounts) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputDistributionEntry>> get_output_distribution(std::vector<uint64_t> amounts, bool is_cumulative, uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonInfo> get_info() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonSyncInfo> get_sync_info() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroHardForkInfo> get_hard_fork_info() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() { throw std::runtime_error("PyMoneroDaemon::get_alt_chains(): not implemented"); }
  virtual std::vector<std::string> get_alt_block_hashes() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int get_download_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int set_download_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int reset_download_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int get_upload_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int set_upload_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int reset_upload_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroPeer>> get_peers() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroPeer>> get_known_peers() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_outgoing_peer_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_incoming_peer_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroBan>> get_peer_bans() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_peer_bans(std::vector<std::shared_ptr<PyMoneroBan>> bans) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_peer_ban(const std::shared_ptr<PyMoneroBan>& ban) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void stop_mining() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroMiningStatus> get_mining_status() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void submit_block(const std::string& block_blob) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void submit_blocks(const std::vector<std::string>& block_blobs) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroPruneResult> prune_blockchain(bool check) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateCheckResult> check_for_update() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update(const std::string& path) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void stop() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> wait_for_next_block_header() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
};

class PyMoneroDaemonDefault : public PyMoneroDaemon {
public:
  void add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) override {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.push_back(listener);
  }

  void remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) override {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<PyMoneroDaemonListener> iter){ return iter == listener; }), m_listeners.end());
  }

  void remove_listeners() override {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.clear();
  }

  std::optional<std::shared_ptr<monero::monero_tx>> get_tx(const std::string& tx_hash, bool prune = false) override { 
    std::vector<std::string> hashes;
    hashes.push_back(tx_hash);
    auto txs = get_txs(hashes, prune);
    std::optional<std::shared_ptr<monero::monero_tx>> tx;

    if (txs.size() > 0) {
      tx = txs[0];
    }

    return tx;
  }

  void relay_tx_by_hash(std::string& tx_hash) override { 
    std::vector<std::string> tx_hashes;
    tx_hashes.push_back(tx_hash);
    relay_txs_by_hash(tx_hashes);
  }

  PyMoneroKeyImageSpentStatus get_key_image_spent_status(std::string& key_image) override { 
    std::vector<std::string> key_images;
    key_images.push_back(key_image);
    auto statuses = get_key_image_spent_statuses(key_images);
    if (statuses.empty()) throw std::runtime_error("Could not get key image spent status");
    return statuses[0];
  }

  std::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false) override { 
    std::vector<std::string> hashes;
    hashes.push_back(tx_hash);
    auto hexes = get_tx_hexes(hashes, prune);
    std::optional<std::string> hex;
    if (hexes.size() > 0) {
      hex = hexes[0];
    }

    return hex;
  }

  void submit_block(const std::string& block_blob) override { 
    std::vector<std::string> block_blobs;
    block_blobs.push_back(block_blob);
    return submit_blocks(block_blobs);
  }


protected:
  mutable boost::recursive_mutex m_listeners_mutex;
  std::vector<std::shared_ptr<PyMoneroDaemonListener>> m_listeners;

};

class PyMoneroDaemonRpc : public PyMoneroDaemonDefault {
public:
  PyMoneroDaemonRpc() {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroDaemonRpc(std::shared_ptr<PyMoneroRpcConnection> rpc) {
    m_rpc = rpc;
  }

  PyMoneroDaemonRpc(const std::string& uri, const std::string& username = "", const std::string& password = "") {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
    m_rpc->m_uri = uri;
    m_rpc->set_credentials(username, password);
  }

  std::shared_ptr<PyMoneroRpcConnection> get_rpc_connection() const {
    return m_rpc;
  }

  bool is_connected() {
    try {
      get_version();
      return true;
    }
    catch (...) {
      return false;
    }
  }

  // overrides

  monero::monero_version get_version() override { 
    PyMoneroJsonRequest request("get_version");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroVersion> info = std::make_shared<PyMoneroVersion>();
    PyMoneroVersion::from_property_tree(res, info);
    return *info;
  }

  bool is_trusted() override {
    PyMoneroPathRequest request("get_height");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);

    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_response.get();
    auto _res = std::make_shared<PyMoneroGetHeightResponse>();
    PyMoneroGetHeightResponse::from_property_tree(res, _res);
    return !_res->m_untrusted.get();
  }

  uint64_t get_height() override { 
    PyMoneroJsonRequest request("get_block_count");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroGetBlockCountResult> result = std::make_shared<PyMoneroGetBlockCountResult>();
    PyMoneroGetBlockCountResult::from_property_tree(res, result);

    if (result->m_count == boost::none) throw std::runtime_error("Could not get height");

    return result->m_count.get();
  }

  std::string get_block_hash(uint64_t height) override { 
    std::shared_ptr<PyMoneroGetBlockHashParams> params = std::make_shared<PyMoneroGetBlockHashParams>(height);

    PyMoneroJsonRequest request("on_get_block_hash", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    return res.data();
  }

  std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address, int reserve_size) override {
    auto params = std::make_shared<PyMoneroGetBlockParams>(wallet_address, reserve_size);
    PyMoneroJsonRequest request("get_block_template", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroBlockTemplate> tmplt = std::make_shared<PyMoneroBlockTemplate>();
    PyMoneroBlockTemplate::from_property_tree(res, tmplt);
    return tmplt;
  }

  std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address) override {
    auto params = std::make_shared<PyMoneroGetBlockParams>(wallet_address);
    PyMoneroJsonRequest request("get_block_template", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroBlockTemplate> tmplt = std::make_shared<PyMoneroBlockTemplate>();
    PyMoneroBlockTemplate::from_property_tree(res, tmplt);
    return tmplt;
  }

  std::shared_ptr<monero::monero_block_header> get_last_block_header() override {
    PyMoneroJsonRequest request("get_last_block_header");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
    PyMoneroBlockHeader::from_property_tree(res, header);
    return header;
  }

  std::shared_ptr<monero::monero_block_header> get_block_header_by_hash(const std::string& hash) override {
    std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(hash);

    PyMoneroJsonRequest request("/get_block_header_by_hash", params);

    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
    PyMoneroBlockHeader::from_property_tree(res, header);
    return header;
  }

  std::shared_ptr<monero::monero_block_header> get_block_header_by_height(uint64_t height) override {
    std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(height);

    PyMoneroJsonRequest request("/get_block_header_by_height", params);

    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
    PyMoneroBlockHeader::from_property_tree(res, header);
    return header;
  }

  std::vector<std::shared_ptr<monero::monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) override { 
    auto params = std::make_shared<PyMoneroGetBlockRangeParams>();
    PyMoneroJsonRequest request("get_block_headers_range", params);

    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::vector<std::shared_ptr<monero::monero_block_header>> headers;
    PyMoneroBlockHeader::from_property_tree(res, headers);
    return headers;
  }

  std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) override {
    std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(hash);

    PyMoneroJsonRequest request("/get_block", params);

    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto block = std::make_shared<monero::monero_block>();
    PyMoneroBlock::from_property_tree(res, block);
    return block;
  }

  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) override { 
    throw std::runtime_error("PyMoneroDaemonRpc::get_blocks_by_hash(): not implemented"); 
  }

  std::shared_ptr<monero::monero_block> get_block_by_height(uint64_t height) override {
    std::shared_ptr<PyMoneroGetBlockParams> params = std::make_shared<PyMoneroGetBlockParams>(height);

    PyMoneroJsonRequest request("/get_block", params);

    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto block = std::make_shared<monero::monero_block>();
    PyMoneroBlock::from_property_tree(res, block);
    return block;
  }

  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_height(std::vector<uint64_t> heights) override { 
    // TODO Binary Request
    throw std::runtime_error("PyMoneroDaemonRpc::get_blocks_by_height(): not implemented"); 
  }

  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range(std::optional<uint64_t> start_height, std::optional<uint64_t> end_height) override {
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

  std::vector<std::string> get_block_hashes(std::vector<std::string> block_hashes, uint64_t start_height) override { 
    throw std::runtime_error("PyMoneroDaemonRpc::get_block_hashes(): not implemented"); 
  }

  std::vector<std::shared_ptr<monero::monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) override { 
    if (tx_hashes.empty()) throw std::runtime_error("Must provide an array of transaction hashes"); 
    auto params = std::make_shared<PyMoneroGetTxsParams>(tx_hashes, prune);
    PyMoneroPathRequest request("get_transactions", params);
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero RPC response");
    auto res = response->m_response.get();
    std::vector<std::shared_ptr<monero::monero_tx>> txs;
    PyMoneroTx::from_property_tree(res, txs);
    return txs;
  }

  std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) override { 
    throw std::runtime_error("PyMoneroDaemon: not implemented"); 
  }

  std::shared_ptr<PyMoneroMinerTxSum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) override {
    auto params = std::make_shared<PyMoneroGetMinerTxSumParams>();
    PyMoneroJsonRequest request("get_coinbase_tx_sum", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto sum = std::make_shared<PyMoneroMinerTxSum>();
    PyMoneroMinerTxSum::from_property_tree(res, sum);
    return sum;
  }

  std::shared_ptr<PyMoneroFeeEstimate> get_fee_estimate(uint64_t grace_blocks = 0) override { 
    auto params = std::make_shared<PyMoneroGetFeeEstimateParams>(grace_blocks);
    PyMoneroJsonRequest request("get_fee_estimate", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto estimate = std::make_shared<PyMoneroFeeEstimate>();
    PyMoneroFeeEstimate::from_property_tree(res, estimate);
    return estimate;
  }

  std::shared_ptr<PyMoneroSubmitTxResult> submit_tx_hex(std::string& tx_hex, bool do_not_relay = false) override { 
    auto params = std::make_shared<PyMoneroSubmitTxParams>(tx_hex, do_not_relay);
    PyMoneroPathRequest request("send_raw_transaction", params);
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_response.get();
    auto sum = std::make_shared<PyMoneroSubmitTxResult>();
    PyMoneroSubmitTxResult::from_property_tree(res, sum);
    return sum;
  }

  void relay_txs_by_hash(std::vector<std::string>& tx_hashes) override { 
    auto params = std::make_shared<PyMoneroRelayTxParams>(tx_hashes);
    PyMoneroJsonRequest request("relay_tx", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    check_response_status(response);
  }

  std::shared_ptr<PyMoneroTxPoolStats> get_tx_pool_stats() override { 
    PyMoneroPathRequest request("get_tx_pool_stats");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_response.get();
    auto stats = std::make_shared<PyMoneroTxPoolStats>();
    PyMoneroTxPoolStats::from_property_tree(res, stats);
    return stats;
  }

  std::vector<std::shared_ptr<monero::monero_tx>> get_tx_pool() override {
    PyMoneroPathRequest request("get_transaction_pool");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_response.get();
    std::vector<std::shared_ptr<monero::monero_tx>> pool;
    PyMoneroTx::from_property_tree(res, pool);
    return pool;
  }

  std::vector<std::string> get_tx_pool_hashes() override {
    PyMoneroPathRequest request("get_transaction_pool_hashes");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero RPC response");
    auto res = response->m_response.get();
    return PyMoneroTxHashes::from_property_tree(res);
  }

  void flush_tx_pool(const std::vector<std::string> &hashes) override {
    auto params = std::make_shared<PyMoneroRelayTxParams>(hashes);
    PyMoneroJsonRequest request("flush_txpool", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    check_response_status(response);
  }

  void flush_tx_pool() override { 
    std::vector<std::string> hashes;
    flush_tx_pool(hashes);
  }

  std::vector<PyMoneroKeyImageSpentStatus> get_key_image_spent_statuses(std::vector<std::string>& key_images) override { 
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

  std::vector<std::shared_ptr<monero::monero_output>> get_outputs(std::vector<monero::monero_output>& outputs) override { 
    throw std::runtime_error("PyMoneroDaemonRpc::get_outputs(): not implemented"); 
  }

  std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> get_output_histogram(std::vector<uint64_t> amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) override { 
    auto params = std::make_shared<PyMoneroGetOutputHistrogramParams>(amounts, min_count, max_count, is_unlocked, recent_cutoff);
    PyMoneroJsonRequest request("get_output_histogram", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> entries;
    PyMoneroOutputHistogramEntry::from_property_tree(res, entries);
    return entries;
  }

  std::shared_ptr<PyMoneroDaemonInfo> get_info() override { 
    PyMoneroJsonRequest request("get_info");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    std::shared_ptr<PyMoneroDaemonInfo> info = std::make_shared<PyMoneroDaemonInfo>();
    PyMoneroDaemonInfo::from_property_tree(res, info);
    return info;
  }

  std::shared_ptr<PyMoneroDaemonSyncInfo> get_sync_info() override {
    PyMoneroJsonRequest request("get_sync_info");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroDaemonSyncInfo> info = std::make_shared<PyMoneroDaemonSyncInfo>();
    PyMoneroDaemonSyncInfo::from_property_tree(res, info);
    return info;
  }

  std::shared_ptr<PyMoneroHardForkInfo> get_hard_fork_info() override {
    PyMoneroJsonRequest request("hard_fork_info");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroHardForkInfo> info = std::make_shared<PyMoneroHardForkInfo>();
    PyMoneroHardForkInfo::from_property_tree(res, info);
    return info;
  }

  std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() override { 
    py::print("PyMoneroDaemonRpc::get_alt_chains()");
    std::vector<std::shared_ptr<PyMoneroAltChain>> result;
    
    PyMoneroJsonRequest request("/get_alternate_chains");
    py::print("PyMoneroDaemonRpc::get_alt_chains(): requesting alt chains...");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    py::print("PyMoneroDaemonRpc::get_alt_chains(): got response");

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    for (boost::property_tree::ptree::const_iterator it = res.begin(); it != res.end(); ++it) {
      std::string key = it->first;
      
      if (key == std::string("chains")) {
        py::print("PyMoneroDaemonRpc::get_alt_chains(): found chains member");
        boost::property_tree::ptree chains = it->second;
        for (boost::property_tree::ptree::const_iterator it2 = chains.begin(); it2 != chains.end(); ++it2) {
          std::shared_ptr<PyMoneroAltChain> alt_chain = std::make_shared<PyMoneroAltChain>();
          py::print("PyMoneroDaemonRpc::get_alt_chains(): before from property tree");
          PyMoneroAltChain::from_property_tree(it2->second, alt_chain);
          py::print("PyMoneroDaemonRpc::get_alt_chains(): after from property tree");
          result.push_back(alt_chain);
        }
      }
    }

    return result;
  }

  std::vector<std::string> get_alt_block_hashes() override {
    PyMoneroPathRequest request("get_alt_blocks_hashes");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_response.get();
    std::vector<std::string> hashes;
    PyMoneroGetAltBlocksHashesResponse::from_property_tree(res, hashes);
    return hashes;
  }

  int get_download_limit() override { 
    auto limits = get_bandwidth_limits();
    if (limits->m_down != boost::none) return limits->m_down.get();
    throw std::runtime_error("Could not get download limit");
  }

  int set_download_limit(int limit) override {
    auto res = set_bandwidth_limits(0, limit);
    if (res->m_down != boost::none) return res->m_down.get();
    throw std::runtime_error("Could not set download limit");
  }

  int reset_download_limit() override {
    auto res = set_bandwidth_limits(0, -1);
    if (res->m_down != boost::none) return res->m_down.get();
    throw std::runtime_error("Could not set download limit");
  }

  int get_upload_limit() override { 
    auto limits = get_bandwidth_limits();
    if (limits->m_up != boost::none) return limits->m_up.get();
    throw std::runtime_error("Could not get upload limit");
  }

  int set_upload_limit(int limit) override {
    auto res = set_bandwidth_limits(limit, 0);
    if (res->m_up != boost::none) return res->m_up.get();
    throw std::runtime_error("Could not set download limit");
  }

  int reset_upload_limit() override {
    auto res = set_bandwidth_limits(-1, 0);
    if (res->m_up != boost::none) return res->m_up.get();
    throw std::runtime_error("Could not set download limit");
  }

  std::vector<std::shared_ptr<PyMoneroPeer>> get_peers() override { 
    PyMoneroJsonRequest request("get_connections");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::vector<std::shared_ptr<PyMoneroPeer>> peers;
    PyMoneroPeer::from_property_tree(res, peers);
    return peers;
  }

  std::vector<std::shared_ptr<PyMoneroPeer>> get_known_peers() override { 
    PyMoneroPathRequest request("get_peer_list");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);

    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_response.get();

    std::vector<std::shared_ptr<PyMoneroPeer>> peers;
    PyMoneroPeer::from_property_tree(res, peers);
    return peers;
  }

  void set_outgoing_peer_limit(int limit) override {
    if (limit < 0) throw std::runtime_error("Outgoing peer limit must be >= 0");
    auto params = std::make_shared<PyMoneroPeerLimits>();
    params->m_out_peers = limit;
    PyMoneroPathRequest request("out_peers", params);
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    check_response_status(response);
  }

  void set_incoming_peer_limit(int limit) override { 
    if (limit < 0) throw std::runtime_error("Incoming peer limit must be >= 0");
    auto params = std::make_shared<PyMoneroPeerLimits>();
    params->m_in_peers = limit;
    PyMoneroPathRequest request("in_peers", params);
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    check_response_status(response);
  }

  std::vector<std::shared_ptr<PyMoneroBan>> get_peer_bans() override {
    PyMoneroJsonRequest request("get_bans");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::vector<std::shared_ptr<PyMoneroBan>> bans;
    PyMoneroBan::from_property_tree(res, bans);
    return bans;
  }

  void set_peer_bans(std::vector<std::shared_ptr<PyMoneroBan>> bans) override {
    auto params = std::make_shared<PyMoneroSetBansParams>(bans);
    PyMoneroJsonRequest request("set_bans");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    check_response_status(response);
  }

  void start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) override { 
    if (address.empty()) throw std::runtime_error("Must provide address to mine to");
    if (num_threads <= 0) throw std::runtime_error("Number of threads must be an integer greater than 0");
    auto params = std::make_shared<PyMoneroStartMiningParams>(address, num_threads, is_background, ignore_battery);
    PyMoneroPathRequest request("start_mining", params);
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
  }

  void stop_mining() override { 
    PyMoneroPathRequest request("stop_mining");
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
  }

  std::shared_ptr<PyMoneroMiningStatus> get_mining_status() override { 
    PyMoneroPathRequest request("mining_status");
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
    auto result = std::make_shared<PyMoneroMiningStatus>();
    auto res = response->m_response.get();
    PyMoneroMiningStatus::from_property_tree(res, result);
    return result;
  }

  void submit_blocks(const std::vector<std::string>& block_blobs) override { 
    if (block_blobs.empty()) throw std::runtime_error("Must provide an array of mined block blobs to submit");
    auto params = std::make_shared<PyMoneroSubmitBlocksParams>(block_blobs);
    PyMoneroJsonRequest request("submit_block", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    check_response_status(response);
  }

  std::shared_ptr<PyMoneroPruneResult> prune_blockchain(bool check) override { 
    auto params = std::make_shared<PyMoneroPruneBlockchainParams>(check);
    PyMoneroJsonRequest request("prune_blockchain", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroPruneResult> result = std::make_shared<PyMoneroPruneResult>();
    PyMoneroPruneResult::from_property_tree(res, result);
    return result;
  }

  std::shared_ptr<PyMoneroDaemonUpdateCheckResult> check_for_update() override { 
    auto params = std::make_shared<PyMoneroCheckUpdateParams>();
    PyMoneroPathRequest request("update", params);
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
    auto result = std::make_shared<PyMoneroDaemonUpdateCheckResult>();
    auto res = response->m_response.get();
    PyMoneroDaemonUpdateCheckResult::from_property_tree(res, result);
    return result;
  }

  std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update(const std::string& path) override { 
    auto params = std::make_shared<PyMoneroDownloadUpdateParams>(path);
    PyMoneroPathRequest request("update", params);
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
    auto result = std::make_shared<PyMoneroDaemonUpdateDownloadResult>();
    auto res = response->m_response.get();
    PyMoneroDaemonUpdateDownloadResult::from_property_tree(res, result);
    return result;
  }

  std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update() override { 
    auto params = std::make_shared<PyMoneroDownloadUpdateParams>();
    PyMoneroPathRequest request("update", params);
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
    auto result = std::make_shared<PyMoneroDaemonUpdateDownloadResult>();
    auto res = response->m_response.get();
    PyMoneroDaemonUpdateDownloadResult::from_property_tree(res, result);
    return result;
  }

  void stop() override {
    PyMoneroPathRequest request("stop_daemon");
    std::shared_ptr<PyMoneroPathResponse> response = m_rpc->send_path_request(request);
    check_response_status(response);
  };

  std::shared_ptr<monero::monero_block_header> wait_for_next_block_header() {
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

  static void check_response_status(std::shared_ptr<PyMoneroPathResponse> response) {
    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero RPC response");
    auto node = response->m_response.get();
    check_response_status(node);
  };

  static void check_response_status(std::shared_ptr<PyMoneroJsonResponse> response) {
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSON RPC response");
    auto node = response->m_result.get();
    check_response_status(node);
  };

protected:
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;

  std::shared_ptr<PyMoneroBandwithLimits> get_bandwidth_limits() {
    PyMoneroPathRequest request("get_limit");
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
    auto res = response->m_response.get();
    auto limits = std::make_shared<PyMoneroBandwithLimits>();
    PyMoneroBandwithLimits::from_property_tree(res, limits);
    return limits;
  }

  std::shared_ptr<PyMoneroBandwithLimits> set_bandwidth_limits(int up, int down) {
    auto limits = std::make_shared<PyMoneroBandwithLimits>(up, down);
    PyMoneroPathRequest request("set_limit", limits);
    auto response = m_rpc->send_path_request(request);
    check_response_status(response);
    auto res = response->m_response.get();
    PyMoneroBandwithLimits::from_property_tree(res, limits);
    return limits;
  }

  static void check_response_status(const boost::property_tree::ptree& node) {
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
};

class PyMoneroDaemonPoller {
public:
  PyMoneroDaemonPoller(std::shared_ptr<PyMoneroDaemon> daemon) {
    m_daemon = daemon;
  }

  void set_is_polling(bool is_poolling) {
    if (is_poolling) start_poolling();
    else stop_poolling();
  }

protected:
  std::shared_ptr<PyMoneroDaemon> m_daemon;
  boost::optional<monero::monero_block_header> m_last_header;
  void start_poolling() {}
  void stop_poolling() {}
  void pool() {}
};

