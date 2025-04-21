#include "daemon/py_monero_daemon.h"

enum PyMoneroAddressType : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
};

class PyMoneroDecodedAddress {
public:
  PyMoneroDecodedAddress(std::string& address, PyMoneroAddressType address_type, monero::monero_network_type network_type) {
    m_address = address;
    m_address_type = address_type;
    m_network_type = network_type;
  }

  std::string m_address;
  PyMoneroAddressType m_address_type;
  monero::monero_network_type m_network_type;
};

class PyMoneroAccountTag {
public:
  PyMoneroAccountTag() { }

  PyMoneroAccountTag(std::string& tag, std::string& label) {
    m_tag = tag;
    m_label = label;
  }

  PyMoneroAccountTag(std::string& tag, std::string& label, std::vector<uint32_t> account_indices) {
    m_tag = tag;
    m_label = label;
    m_account_indices = account_indices;
  }

  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;
  std::vector<uint32_t> m_account_indices;
};

class PyMoneroTransfer : public monero_transfer {
public:
  using monero_transfer::monero_transfer;

  boost::optional<bool> is_incoming() const override {
    PYBIND11_OVERRIDE_PURE(
      boost::optional<bool>,
      monero_transfer,
      is_incoming
    );
  }
};

class PyMoneroSubaddress : public monero::monero_subaddress {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("major")) subaddress->m_account_index = it->second.get_value<uint32_t>();
      else if (key == std::string("minor")) subaddress->m_index = it->second.get_value<uint32_t>();
      else if (key == std::string("index")) {
        auto node2 = it->second;
        from_property_tree(node2, subaddress);
      }
    }
  }
};

class PyMoneroIntegratedAddress : public monero::monero_integrated_address {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_integrated_address>& subaddress) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("integrated_address")) subaddress->m_integrated_address = it->second.data();
      else if (key == std::string("standard_address")) subaddress->m_standard_address = it->second.data();
      else if (key == std::string("payment_id")) subaddress->m_payment_id = it->second.data();
    }
  }
};

class PyMoneroWalletGetHeightResponse {
public:
  static uint64_t from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("height")) return it->second.get_value<uint64_t>();
    }
    throw std::runtime_error("Invalid get_height response");
  }
};

class PyMoneroQueryKeyParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key_type;

  PyMoneroQueryKeyParams() { }
  PyMoneroQueryKeyParams(const std::string& key_type) {
    m_key_type = key_type;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_key_type != boost::none) monero_utils::add_json_member("key_type", m_key_type.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroGetAddressIndexParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;

  PyMoneroGetAddressIndexParams() { }
  PyMoneroGetAddressIndexParams(const std::string& address) {
    m_address = address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroMakeIntegratedAddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_standard_address;
  boost::optional<std::string> m_payment_id;

  PyMoneroMakeIntegratedAddressParams() { }
  PyMoneroMakeIntegratedAddressParams(const std::string& standard_address, const std::string& payment_id) {
    m_standard_address = standard_address;
    m_payment_id = payment_id;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_standard_address != boost::none) monero_utils::add_json_member("standard_address", m_standard_address.get(), allocator, root, value_str);
    if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroSplitIntegratedAddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_integrated_address;

  PyMoneroSplitIntegratedAddressParams() { }
  PyMoneroSplitIntegratedAddressParams(const std::string& integrated_address) {
    m_integrated_address = integrated_address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_integrated_address != boost::none) monero_utils::add_json_member("integrated_address", m_integrated_address.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroCloseWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_save;

  PyMoneroCloseWalletParams(bool save = true) {
    m_save = save;
  };

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_save != boost::none) monero_utils::add_json_member("save", m_save.get(), allocator, root);
    return root; 
  }
};

class PyMoneroChangeWalletPasswordParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_old_password;
  boost::optional<std::string> m_new_password;

  PyMoneroChangeWalletPasswordParams(const std::string& old_password, const std::string& new_password) {
    m_old_password = old_password;
    m_new_password = new_password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_old_password != boost::none) monero_utils::add_json_member("old_password", m_old_password.get(), allocator, root, value_str);
    if (m_new_password != boost::none) monero_utils::add_json_member("new_password", m_new_password.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroWalletAttributeParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key;
  boost::optional<std::string> m_value;

  PyMoneroWalletAttributeParams(const std::string& key, const std::string& value) {
    m_key = key;
    m_value = value;
  }

  PyMoneroWalletAttributeParams(const std::string& key) {
    m_key = key;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_key != boost::none) monero_utils::add_json_member("key", m_key.get(), allocator, root, value_str);
    if (m_value != boost::none) monero_utils::add_json_member("value", m_value.get(), allocator, root, value_str);
    return root; 
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroWalletAttributeParams>& attributes) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("key")) attributes->m_key = it->second.data();
      else if (key == std::string("value")) attributes->m_value = it->second.data();
    }
  }
};

class PyMoneroScanTxParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;

  PyMoneroScanTxParams() {}
  PyMoneroScanTxParams(const std::vector<std::string>& tx_hashes) {
    m_tx_hashes = tx_hashes;
  }
};

class PyMoneroWallet : public monero_wallet {
public:
  using monero_wallet::monero_wallet;

  std::string get_seed() const override {
    PYBIND11_OVERRIDE_PURE(
      std::string,
      monero_wallet,
      get_seed,
    );
  }
};
  
class PyMoneroWalletRpc : public monero_wallet {
public:

  PyMoneroWalletRpc() {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroWalletRpc(std::shared_ptr<PyMoneroRpcConnection> rpc_connection) {
    m_rpc = rpc_connection;
  }

  PyMoneroWalletRpc(const std::string& uri = "", const std::string& username = "", const std::string& password = "")
  {
    m_rpc = std::make_shared<PyMoneroRpcConnection>(uri, username, password);
    m_rpc->check_connection();
  }

  boost::optional<monero::monero_rpc_connection> get_daemon_connection() const override {
    if (m_rpc == nullptr) return boost::none;
    return boost::optional<monero::monero_rpc_connection>(*m_rpc);
  }

  void open_wallet(const std::shared_ptr<monero::monero_wallet_config> config) {
    throw std::runtime_error("PyMoneroWalletRpc::open_wallet(): not implemented");
  }

  void open_wallet(const std::string& name, const std::string& password) {
    auto config = std::make_shared<monero::monero_wallet_config>();
    config->m_path = name;
    config->m_password = password;
    return open_wallet(config);
  }

  std::string get_seed() const override {
    std::string key = "mnemonic";
    return query_key(key);
  }

  std::string get_seed_language() const override {
    throw std::runtime_error("MoneroWalletRpc::get_seed_language() not supported");
  }

  std::string get_public_view_key() const override {
    std::string key = "public_view_key";
    return query_key(key);
  }

  std::string get_private_view_key() const override {
    std::string key = "view_key";
    return query_key(key);
  }

  std::string get_public_spend_key() const override {
    std::string key = "public_spend_key";
    return query_key(key);
  }

  std::string get_private_spend_key() const override {
    std::string key = "spend_key";
    return query_key(key);
  }

  monero_subaddress get_address_index(const std::string& address) const {
    auto params = std::make_shared<PyMoneroGetAddressIndexParams>(address);
    PyMoneroJsonRequest request("get_address_index", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    auto tmplt = std::make_shared<monero::monero_subaddress>();
    PyMoneroSubaddress::from_property_tree(res, tmplt);
    return *tmplt;
  }
  
  monero_integrated_address get_integrated_address(const std::string& standard_address = "", const std::string& payment_id = "") const override {
    auto params = std::make_shared<PyMoneroMakeIntegratedAddressParams>(standard_address, payment_id);
    PyMoneroJsonRequest request("make_integrated_address", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    auto tmplt = std::make_shared<monero::monero_integrated_address>();
    PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
    return decode_integrated_address(tmplt->m_integrated_address);
  }

  monero_integrated_address decode_integrated_address(const std::string& integrated_address) const override {
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

  uint64_t get_height() const override {
    PyMoneroJsonRequest request("get_height");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroWalletGetHeightResponse::from_property_tree(res);
  }

  void set_attribute(const std::string& key, const std::string& val) override {
    auto params = std::make_shared<PyMoneroWalletAttributeParams>(key, val);
    PyMoneroJsonRequest request("set_attribute");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  }

  bool get_attribute(const std::string& key, std::string& value) const override {
    try {
      auto params = std::make_shared<PyMoneroWalletAttributeParams>(key);
      PyMoneroJsonRequest request("get_attribute");
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

  void start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) override {
    auto params = std::make_shared<PyMoneroStartMiningParams>(num_threads.value_or(0), background_mining.value_or(false), ignore_battery.value_or(false));
    PyMoneroPathRequest request("start_mining", params);
    auto response = m_rpc->send_path_request(request);
    PyMoneroDaemonRpc::check_response_status(response);
  }

  void stop_mining() override {
    PyMoneroJsonRequest request("stop_mining");
    m_rpc->send_json_request(request);
  }

  void change_password(const std::string& old_password, const std::string& new_password) override {
    auto params = std::make_shared<PyMoneroChangeWalletPasswordParams>(old_password, new_password);
    PyMoneroJsonRequest request("change_wallet_password", params);
    m_rpc->send_json_request(request);
  }

  void save() override {
    PyMoneroJsonRequest request("store");
    m_rpc->send_json_request(request);
  }

  void close(bool save = false) override {
    auto params = std::make_shared<PyMoneroCloseWalletParams>(save);
    PyMoneroJsonRequest request("close_wallet", params);
    m_rpc->send_json_request(request);
  }

protected:
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;

  std::string query_key(const std::string& key_type) const {
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
};
  