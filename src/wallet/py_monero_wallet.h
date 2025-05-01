#include "daemon/py_monero_daemon.h"

enum PyMoneroAddressType : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
};

class PyMoneroMultisigInfo : public monero::monero_multisig_info {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_info>& info) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("multisig")) info->m_is_multisig = it->second.get_value<bool>();
      else if (key == std::string("ready")) info->m_is_ready = it->second.get_value<bool>();
      else if (key == std::string("threshold")) info->m_threshold = it->second.get_value<uint32_t>();
      else if (key == std::string("total")) info->m_num_participants = it->second.get_value<uint32_t>();
    }
  }
};

class PyMoneroMultisigInitResult : public monero::monero_multisig_init_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_init_result>& info) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("address")) info->m_address = it->second.data();
      else if (key == std::string("multisig_info")) info->m_multisig_hex = it->second.data();
    }
  }
};

class PyMoneroMultisigSignResult : public monero::monero_multisig_sign_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_sign_result>& res) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tx_data_hex")) res->m_signed_multisig_tx_hex = it->second.data();
      else if (key == std::string("tx_hash_list")) {
        auto node2 = it->second;
        for (boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node.end(); ++it2) {
          res->m_tx_hashes.push_back(it2->second.data());
        }
      }
    }
  }
};

class PyMoneroMultisigTxDataParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_multisig_tx_hex;

  PyMoneroMultisigTxDataParams() {}
  PyMoneroMultisigTxDataParams(const std::string& multisig_tx_hex) {
    m_multisig_tx_hex = multisig_tx_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_multisig_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_multisig_tx_hex.get(), allocator, root, value_str);
    return root; 
  }
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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAccountTag>& account_tag) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tag")) account_tag->m_tag = it->second.data();
      else if (key == std::string("label")) account_tag->m_label = it->second.data();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroAccountTag>>& account_tags) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("account_tags")) {
        auto account_tags_node = it->second;

        for (auto it2 = account_tags_node.begin(); it2 != account_tags_node.end(); ++it2) {
          auto account_tag = std::make_shared<PyMoneroAccountTag>();
          from_property_tree(it2->second, account_tag);
          account_tags.push_back(account_tag);
        }
      }
    }
  }
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

class PyMoneroWalletStartMiningParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<int> m_num_threads;
  boost::optional<bool> m_is_background;
  boost::optional<bool> m_ignore_battery;

  PyMoneroWalletStartMiningParams() { }

  PyMoneroWalletStartMiningParams(int num_threads, bool is_background, bool ignore_battery) {
    m_num_threads = num_threads;
    m_is_background = is_background;
    m_ignore_battery = ignore_battery;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);
    if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
    if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);
    return root;
  };
};

class PyMoneroPrepareMultisigParams : public PyMoneroJsonRequestParams {
public:
  // TODO monero-docs document this parameter
  boost::optional<bool> m_enable_multisig_experimental;
  PyMoneroPrepareMultisigParams(bool enable_multisig_experimental = true) {
    m_enable_multisig_experimental = enable_multisig_experimental;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_enable_multisig_experimental != boost::none) monero_utils::add_json_member("enable_multisig_experimental", m_enable_multisig_experimental.get(), allocator, root);
    return root; 
  }
};

class PyMoneroExportMultisigHexResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("info")) return it->second.data();
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroImportMultisigHexParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_hexes;

  PyMoneroImportMultisigHexParams() {}

  PyMoneroImportMultisigHexParams(const std::vector<std::string>& multisig_hexes) {
    m_multisig_hexes = multisig_hexes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_multisig_hexes.empty()) root.AddMember("info", monero_utils::to_rapidjson_val(allocator, m_multisig_hexes), allocator);
    return root;
  }
};

class PyMoneroImportMultisigHexResponse {
public:
  static int from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("n_outputs")) return it->second.get_value<int>();
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroSubmitMultisigTxHexResponse {
public:
  PyMoneroSubmitMultisigTxHexResponse() {}
  static std::vector<std::string> from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tx_hash_list")) {
        auto node2 = it->second;
        std::vector<std::string> hashes;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          hashes.push_back(it2->second.data());
        }

        return hashes;
      }
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroMakeMultisigParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_info;
  boost::optional<int> m_threshold;
  boost::optional<std::string> m_password;

  PyMoneroMakeMultisigParams(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) {
    m_multisig_info = multisig_hexes;
    m_threshold = threshold;
    m_password = password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
    if (m_threshold != boost::none) monero_utils::add_json_member("threshold", m_threshold.get(), allocator, root, val_num);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
    return root; 
  }
};
  
class PyMoneroPrepareMakeMultisigResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("multisig_info")) return it->second.data();
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroExchangeMultisigKeysParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_info;
  boost::optional<std::string> m_password;

  PyMoneroExchangeMultisigKeysParams() {}
  PyMoneroExchangeMultisigKeysParams(const std::vector<std::string>& multisig_hexes, const std::string& password) {
    m_multisig_info = multisig_hexes;
    m_password = password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
    return root; 
  }
};

class PyMoneroParsePaymentUriParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_uri;

  PyMoneroParsePaymentUriParams() {}
  PyMoneroParsePaymentUriParams(const std::string& uri) {
    m_uri = uri;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (m_uri != boost::none) monero_utils::add_json_member("uri", m_uri.get(), allocator, root, val_str);
    return root;
  }
};

class PyMoneroParsePaymentUriResponse {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_payment_id;
  boost::optional<std::string> m_recipient_name;
  boost::optional<std::string> m_tx_description;

  PyMoneroParsePaymentUriResponse() {}

  std::shared_ptr<monero::monero_tx_config> to_tx_config() const {
    auto tx_config = std::make_shared<monero::monero_tx_config>();
    tx_config->m_payment_id = m_payment_id;
    tx_config->m_recipient_name = m_recipient_name;
    tx_config->m_note = m_tx_description;
    tx_config->m_amount = m_amount;
    tx_config->m_address = m_address;
    return tx_config;
  }
  
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroParsePaymentUriResponse>& response) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("address")) response->m_address = it->second.data();
      else if (key == std::string("amount")) response->m_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("payment_id")) response->m_payment_id = it->second.data();
      else if (key == std::string("recipient_name")) response->m_recipient_name = it->second.data();
      else if (key == std::string("tx_description")) response->m_tx_description = it->second.data();
    }
  }
};

class PyMoneroGetPaymentUriParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_recipient_name;
  boost::optional<std::string> m_tx_description;

  PyMoneroGetPaymentUriParams() {}
  PyMoneroGetPaymentUriParams(const monero_tx_config & config) {
    m_address = config.m_address;
    m_amount = config.m_amount;
    m_recipient_name = config.m_recipient_name;
    m_tx_description = config.m_note;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);
    if (m_recipient_name != boost::none) monero_utils::add_json_member("recipient_name", m_recipient_name.get(), allocator, root, value_str);
    if (m_tx_description != boost::none) monero_utils::add_json_member("tx_description", m_tx_description.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroGetPaymentUriResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("uri")) return it->second.data();
    }
    throw std::runtime_error("Invalid make uri response");
  }
};

class PyMoneroGetBalanceParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint32_t> m_account_idx;
  std::vector<uint32_t> m_address_indices;
  boost::optional<bool> m_all_accounts;
  boost::optional<bool> m_strict;

  PyMoneroGetBalanceParams() {};
  PyMoneroGetBalanceParams(uint32_t account_idx, const std::vector<uint32_t>& address_indices, bool all_accounts = false, bool strict = false) {
    m_account_idx = account_idx;
    m_address_indices = address_indices;
    m_all_accounts = all_accounts;
    m_strict = strict;
  }
  PyMoneroGetBalanceParams(uint32_t account_idx, boost::optional<uint32_t> address_idx, bool all_accounts = false, bool strict = false) {
    m_account_idx = account_idx;
    if (address_idx != boost::none) m_address_indices.push_back(address_idx.get());
    m_all_accounts = all_accounts;
    m_strict = strict;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_account_idx != boost::none) monero_utils::add_json_member("account_index", m_account_idx.get(), allocator, root, value_num);
    if (!m_address_indices.empty()) root.AddMember("address_indices", monero_utils::to_rapidjson_val(allocator, m_address_indices), allocator);
    if (m_all_accounts != boost::none) monero_utils::add_json_member("all_accounts", m_all_accounts.get(), allocator, root);
    if (m_strict != boost::none) monero_utils::add_json_member("strict", m_strict.get(), allocator, root);
    return root; 
  }
};

class PyMoneroSubaddressBalance {
public:
  boost::optional<uint32_t> m_account_idx;
  boost::optional<uint32_t> m_address_idx;
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_balance;
  boost::optional<uint64_t> m_unlocked_balance;
  boost::optional<std::string> m_label;
  boost::optional<uint64_t> m_num_unspent_outputs;
  boost::optional<uint64_t> m_time_to_unlock;
  boost::optional<uint64_t> m_blocks_to_unlock;

  PyMoneroSubaddressBalance() {}

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroSubaddressBalance>& subaddress) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("account_index")) subaddress->m_account_idx = it->second.get_value<uint32_t>();
      else if (key == std::string("address_index")) subaddress->m_address_idx = it->second.get_value<uint32_t>();
      else if (key == std::string("address")) subaddress->m_address = it->second.data();
      else if (key == std::string("balance")) subaddress->m_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("unlocked_balance")) subaddress->m_unlocked_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("label")) subaddress->m_label = it->second.data();
      else if (key == std::string("num_unspent_outputs")) subaddress->m_num_unspent_outputs = it->second.get_value<uint64_t>();
      else if (key == std::string("time_to_unlock")) subaddress->m_time_to_unlock = it->second.get_value<uint64_t>();
      else if (key == std::string("blocks_to_unlock")) subaddress->m_blocks_to_unlock = it->second.get_value<uint64_t>();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroSubaddressBalance>>& subaddresses) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("per_subaddress")) {
        auto per_subaddress_node = it->second;

        for (auto it2 = per_subaddress_node.begin(); it2 != per_subaddress_node.end(); ++it2) {
          auto sub = std::make_shared<PyMoneroSubaddressBalance>();
          from_property_tree(it2->second, sub);
          subaddresses.push_back(sub);
        }
      }
    }
  }
};

class PyMoneroGetBalanceResponse {
public:
  boost::optional<uint64_t> m_balance;
  boost::optional<uint64_t> m_unlocked_balance;
  boost::optional<bool> m_multisig_import_needed;
  boost::optional<uint64_t> m_time_to_unlock;
  boost::optional<uint64_t> m_blocks_to_unlock;
  std::vector<std::shared_ptr<PyMoneroSubaddressBalance>> m_per_subaddress;

  PyMoneroGetBalanceResponse() {
    m_balance = 0;
    m_unlocked_balance = 0;
  }

  PyMoneroGetBalanceResponse(uint64_t balance, uint64_t unlocked_balance, bool multisig_import_needed, uint64_t time_to_unlock, uint64_t blocks_to_unlock) {
    m_balance = balance;
    m_unlocked_balance = unlocked_balance;
    m_multisig_import_needed = multisig_import_needed;
    m_time_to_unlock = time_to_unlock;
    m_blocks_to_unlock = blocks_to_unlock;
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBalanceResponse>& response) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("balance")) response->m_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("unlocked_balance")) response->m_unlocked_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("multisig_import_needed")) response->m_multisig_import_needed = it->second.get_value<bool>();
      else if (key == std::string("time_to_unlock")) response->m_time_to_unlock = it->second.get_value<uint64_t>();
      else if (key == std::string("blocks_to_unlock")) response->m_blocks_to_unlock = it->second.get_value<uint64_t>();
      else if (key == std::string("per_subaddress")) {
        auto node2 = it->second;

        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto sub = std::make_shared<PyMoneroSubaddressBalance>();
          PyMoneroSubaddressBalance::from_property_tree(it2->second, sub);
          response->m_per_subaddress.push_back(sub);
        }
      }
    }
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
    return root; 
  }
};

class PyMoneroSetDaemonParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_username;
  boost::optional<std::string> m_password;
  boost::optional<bool> m_trusted;
  boost::optional<std::string> m_ssl_support;
  boost::optional<std::string> m_ssl_private_key_path;
  boost::optional<std::string> m_ssl_certificate_path;
  boost::optional<std::string> m_ssl_ca_file;
  std::vector<std::string> m_ssl_allowed_fingerprints;
  boost::optional<bool> m_ssl_allow_any_cert;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_username != boost::none) monero_utils::add_json_member("username", m_username.get(), allocator, root, value_str);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, value_str);
    if (m_trusted != boost::none) monero_utils::add_json_member("trusted", m_trusted.get(), allocator, root);
    if (m_ssl_support != boost::none) monero_utils::add_json_member("ssl_support", m_ssl_support.get(), allocator, root, value_str);
    if (m_ssl_private_key_path != boost::none) monero_utils::add_json_member("ssl_private_key_path", m_ssl_private_key_path.get(), allocator, root, value_str);
    if (m_ssl_certificate_path != boost::none) monero_utils::add_json_member("ssl_certificate_path", m_ssl_certificate_path.get(), allocator, root, value_str);
    if (m_ssl_ca_file != boost::none) monero_utils::add_json_member("ssl_ca_file", m_ssl_ca_file.get(), allocator, root, value_str);
    if (!m_ssl_allowed_fingerprints.empty()) root.AddMember("ssl_allowed_fingerprints", monero_utils::to_rapidjson_val(allocator, m_ssl_allowed_fingerprints), allocator);
    if (m_ssl_allow_any_cert != boost::none) monero_utils::add_json_member("ssl_allow_any_cert", m_ssl_allow_any_cert.get(), allocator, root);

    return root; 
  }
};

class PyMoneroAutoRefreshParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_enable;

  PyMoneroAutoRefreshParams(bool enable): m_enable(enable) { } 

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_enable != boost::none) monero_utils::add_json_member("enable", m_enable.get(), allocator, root);
    return root; 
  }
};

class PyMoneroSetAccountTagDescriptionParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;

  PyMoneroSetAccountTagDescriptionParams() {}
  PyMoneroSetAccountTagDescriptionParams(const std::string& tag, const std::string& label) {
    m_tag = tag;
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
    if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroTagAccountsParams : public PyMoneroJsonRequestParams {
public:
  std::vector<uint32_t> m_account_indices;
  boost::optional<std::string> m_tag;

  PyMoneroTagAccountsParams() {}
  PyMoneroTagAccountsParams(const std::vector<uint32_t>& account_indices) {
    m_account_indices = account_indices;
  }
  PyMoneroTagAccountsParams(const std::string& tag, const std::vector<uint32_t>& account_indices) {
    m_account_indices = account_indices;
    m_tag = tag;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
    if (!m_account_indices.empty()) root.AddMember("accounts", monero_utils::to_rapidjson_val(allocator, m_account_indices), allocator);
    return root; 
  }
};

class PyMoneroTxNotesParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;
  std::vector<std::string> m_notes;

  PyMoneroTxNotesParams(const std::vector<std::string>& tx_hashes) {
    m_tx_hashes = tx_hashes;
  }

  PyMoneroTxNotesParams(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
    m_tx_hashes = tx_hashes;
    m_notes = notes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
    if (!m_notes.empty()) root.AddMember("notes", monero_utils::to_rapidjson_val(allocator, m_notes), allocator);
    return root; 
  }
};

class PyMoneroAddressBookEntryParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_index;  // TODO: not boost::optional
  boost::optional<bool> m_set_address;
  boost::optional<std::string> m_address;
  boost::optional<bool> m_set_description;
  boost::optional<std::string> m_description;
  std::vector<uint64_t> m_entries;

  PyMoneroAddressBookEntryParams() {}
  PyMoneroAddressBookEntryParams(uint64_t index) {
    m_index = index;
  }
  PyMoneroAddressBookEntryParams(const std::vector<uint64_t>& entries) {
    m_entries = entries;
  }
  PyMoneroAddressBookEntryParams(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
    m_index = index;
    m_set_address = set_address;
    m_address = address;
    m_set_description = set_description;
    m_description = description;
  }
  PyMoneroAddressBookEntryParams(const std::string& address, const std::string& description) {
    m_address = address;
    m_description = description;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_index != boost::none) monero_utils::add_json_member("index", m_index.get(), allocator, root, value_num);
    if (m_set_address != boost::none) monero_utils::add_json_member("set_address", m_set_address.get(), allocator, root);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_set_description != boost::none) monero_utils::add_json_member("set_description", m_set_description.get(), allocator, root);
    if (m_description != boost::none) monero_utils::add_json_member("description", m_description.get(), allocator, root, value_str);
    if (!m_entries.empty()) root.AddMember("entries", monero_utils::to_rapidjson_val(allocator, m_entries), allocator);
    return root; 
  }
};

class PyMoneroAddressBookEntry : public monero::monero_address_book_entry {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_address_book_entry>& entry) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("index")) entry->m_index = it->second.get_value<uint64_t>();
      else if (key == std::string("address")) entry->m_address = it->second.data();
      else if (key == std::string("description")) entry->m_description = it->second.data();
      else if (key == std::string("payment_id")) entry->m_payment_id = it->second.data();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_address_book_entry>>& entries) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("entries")) {
        auto entries_node = it->second;

        for (auto it2 = entries_node.begin(); it2 != entries_node.end(); ++it2) {
          auto entry = std::make_shared<monero::monero_address_book_entry>();
          from_property_tree(it2->second, entry);
          entries.push_back(entry);
        }
      }
    }
  }
};

class PyMoneroWalletBalance {
public:
  uint64_t m_balance;
  uint64_t m_unlocked_balance;

  PyMoneroWalletBalance(uint64_t balance = 0, uint64_t unlocked_balance = 0) {
    m_balance = balance;
    m_unlocked_balance = unlocked_balance;
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

  boost::optional<monero::monero_rpc_connection> get_rpc_connection() const {
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

  std::vector<std::string> get_seed_languages() const {
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

  void stop() {
    PyMoneroJsonRequest request("stop_wallet");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  }  
 
  bool is_view_only() const override {
    try {
      std::string key = "mnemonic";
      query_key(key);
      return false;
    }
    catch (const MoneroRpcError& e) {
      if (e.code == -29) return true;
      if (e.code == -1) return false;
      throw e;
    }
  }

  boost::optional<monero::monero_rpc_connection> get_daemon_connection() const override {
    if (m_daemon_connection == nullptr) return boost::none;
    return boost::optional<monero::monero_rpc_connection>(*m_daemon_connection);
  }
  
  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection, bool is_trusted, const boost::optional<std::shared_ptr<PyMoneroSslOptions>> ssl_options) {
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

  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection) override {
    set_daemon_connection(connection, false, boost::none);
  }

  bool is_connected_to_daemon() const override {
    try {
      check_reserve_proof(get_primary_address(), "", "");
      return false;
    }
    catch (const MoneroRpcError& e) {
      if (e.message == std::string("Failed to connect to daemon")) return false;
      return true;
    }
  }

  monero::monero_version get_version() const override { 
    PyMoneroJsonRequest request("get_version");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroVersion> info = std::make_shared<PyMoneroVersion>();
    PyMoneroVersion::from_property_tree(res, info);
    return *info;
  }

  std::string get_path() const override {
    return m_path;
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

  // TODO implement get_address

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

  void stop_syncing() override {
    auto params = std::make_shared<PyMoneroAutoRefreshParams>(false);
    PyMoneroJsonRequest request("auto_refresh", params);
    m_rpc->send_json_request(request);
  }

  void scan_txs(const std::vector<std::string>& tx_hashes) override {
    if (tx_hashes.empty()) throw std::runtime_error("No tx hashes given to scan");
    auto params = std::make_shared<PyMoneroScanTxParams>(tx_hashes);
    PyMoneroJsonRequest request("scan_tx", params);
    m_rpc->send_json_request(request);
    poll();
  }

  void rescan_spent() override {
    PyMoneroJsonRequest request("rescan_spent");
    m_rpc->send_json_request(request);
  }

  void rescan_blockchain() override {
    PyMoneroJsonRequest request("rescan_blockchain");
    m_rpc->send_json_request(request);
  }

  std::vector<std::string> get_tx_notes(const std::vector<std::string>& tx_hashes) const override {
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

  void set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) override {
    auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes, notes);
    PyMoneroJsonRequest request("set_tx_notes", params);
    m_rpc->send_json_request(request);
  }

  std::vector<monero_address_book_entry> get_address_book_entries(const std::vector<uint64_t>& indices) const override {
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

  uint64_t add_address_book_entry(const std::string& address, const std::string& description) override {
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

  void edit_address_book_entry(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) override {
    auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index, set_address, address, set_description, description);
    PyMoneroJsonRequest request("edit_address_book", params);
    m_rpc->send_json_request(request);
  }

  void delete_address_book_entry(uint64_t index) override {
    auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index);
    PyMoneroJsonRequest request("delete_address_book", params);
    m_rpc->send_json_request(request);
  }

  void tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) {
    auto params = std::make_shared<PyMoneroTagAccountsParams>(tag, account_indices);
    PyMoneroJsonRequest request("tag_accounts", params);
    m_rpc->send_json_request(request);
  }

  void untag_accounts(const std::vector<uint32_t>& account_indices) {
    auto params = std::make_shared<PyMoneroTagAccountsParams>(account_indices);
    PyMoneroJsonRequest request("untag_accounts", params);
    m_rpc->send_json_request(request);
  }

  std::vector<std::shared_ptr<PyMoneroAccountTag>> get_account_tags() {
    PyMoneroJsonRequest request("get_account_tags");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    std::vector<std::shared_ptr<PyMoneroAccountTag>> account_tags;
    PyMoneroAccountTag::from_property_tree(res, account_tags);
    return account_tags;
  }

  void set_account_tag_label(const std::string& tag, const std::string& label) {
    auto params = std::make_shared<PyMoneroSetAccountTagDescriptionParams>(tag, label);
    PyMoneroJsonRequest request("set_account_tag_description", params);
    m_rpc->send_json_request(request);
  }

  std::string get_payment_uri(const monero_tx_config& config) const override {
    auto params = std::make_shared<PyMoneroGetPaymentUriParams>(config);
    PyMoneroJsonRequest request("make_uri", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroGetPaymentUriResponse::from_property_tree(res);
  }

  std::shared_ptr<monero_tx_config> parse_payment_uri(const std::string& uri) const {
    auto params = std::make_shared<PyMoneroParsePaymentUriParams>(uri);
    PyMoneroJsonRequest request("parse_uri", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto uri_response = std::make_shared<PyMoneroParsePaymentUriResponse>();
    PyMoneroParsePaymentUriResponse::from_property_tree(res, uri_response);
    return uri_response->to_tx_config();
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
    auto params = std::make_shared<PyMoneroWalletStartMiningParams>(num_threads.value_or(0), background_mining.value_or(false), ignore_battery.value_or(false));
    PyMoneroJsonRequest request("start_mining", params);
    auto response = m_rpc->send_json_request(request);
    PyMoneroDaemonRpc::check_response_status(response);
  }

  void stop_mining() override {
    PyMoneroJsonRequest request("stop_mining");
    m_rpc->send_json_request(request);
  }

  bool is_multisig_import_needed() const override {
    PyMoneroJsonRequest request("get_balance");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto balance = std::make_shared<PyMoneroGetBalanceResponse>();
    PyMoneroGetBalanceResponse::from_property_tree(res, balance);
    if (balance->m_multisig_import_needed) return true;
    return false;
  }

  monero_multisig_info get_multisig_info() const override {
    PyMoneroJsonRequest request("is_multisig");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto info = std::make_shared<monero::monero_multisig_info>();
    PyMoneroMultisigInfo::from_property_tree(res, info);
    return *info;
  }

  std::string prepare_multisig() override {
    auto params = std::make_shared<PyMoneroPrepareMultisigParams>();
    PyMoneroJsonRequest request("prepare_multisig", params);
    auto response = m_rpc->send_json_request(request);
    clear_address_cache();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
  }

  std::string make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) override {
    auto params = std::make_shared<PyMoneroMakeMultisigParams>(multisig_hexes, threshold, password);
    PyMoneroJsonRequest request("make_multisig", params);
    auto response = m_rpc->send_json_request(request);
    clear_address_cache();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
  }

  monero_multisig_init_result exchange_multisig_keys(const std::vector<std::string>& mutisig_hexes, const std::string& password) {
    auto params = std::make_shared<PyMoneroExchangeMultisigKeysParams>(mutisig_hexes, password);
    PyMoneroJsonRequest request("exchange_multisig_keys", params);
    auto response = m_rpc->send_json_request(request);
    clear_address_cache();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto multisig_init = std::make_shared<monero_multisig_init_result>();
    PyMoneroMultisigInitResult::from_property_tree(res, multisig_init);
    return *multisig_init;
  }

  std::string export_multisig_hex() override {
    PyMoneroJsonRequest request("export_multisig_info");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroExportMultisigHexResponse::from_property_tree(res);
  }
  
  int import_multisig_hex(const std::vector<std::string>& multisig_hexes) override {
    auto params = std::make_shared<PyMoneroImportMultisigHexParams>(multisig_hexes);
    PyMoneroJsonRequest request("import_multisig_info", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroImportMultisigHexResponse::from_property_tree(res);
  }

  monero_multisig_sign_result sign_multisig_tx_hex(const std::string& multisig_tx_hex) override {
    auto params = std::make_shared<PyMoneroMultisigTxDataParams>(multisig_tx_hex);
    PyMoneroJsonRequest request("sign_multisig", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto multisig_result = std::make_shared<monero::monero_multisig_sign_result>();
    PyMoneroMultisigSignResult::from_property_tree(res, multisig_result);
    return *multisig_result;
  }

  std::vector<std::string> submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex) {
    auto params = std::make_shared<PyMoneroMultisigTxDataParams>(signed_multisig_tx_hex);
    PyMoneroJsonRequest request("submit_multisig", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroSubmitMultisigTxHexResponse::from_property_tree(res);
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
  std::string m_path = "";
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;
  std::shared_ptr<PyMoneroRpcConnection> m_daemon_connection;
  serializable_unordered_map<uint32_t, serializable_unordered_map<uint32_t, std::string>> m_address_cache;
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

  std::shared_ptr<PyMoneroWalletBalance> get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) {
    auto balance = std::make_shared<PyMoneroWalletBalance>();

    if (account_idx == boost::none) {
      if (subaddress_idx != boost::none) throw std::runtime_error("Must provide account index with subaddress index");
    
      auto accounts = get_accounts();

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

  void clear_address_cache() {

  };

  void poll() {

  };
};
  