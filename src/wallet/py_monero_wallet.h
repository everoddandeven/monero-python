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
  PyMoneroGetAddressIndexParams(const std::string& m_address) {
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
    return tmplt;
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
  