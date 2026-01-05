#pragma once

#include "daemon/py_monero_daemon_model.h"

enum PyMoneroAddressType : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
};

class PyMoneroTxQuery : public monero::monero_tx_query {
public:

  static void decontextualize(const std::shared_ptr<monero::monero_tx_query> &query);
  static void decontextualize(monero::monero_tx_query &query);
};

class PyMoneroOutputQuery : public monero::monero_output_query {
public:

  static bool is_contextual(const std::shared_ptr<monero::monero_output_query> &query);
  static bool is_contextual(const monero::monero_output_query &query);
};

class PyMoneroTransferQuery : public monero::monero_transfer_query {
public:

  static bool is_contextual(const std::shared_ptr<monero::monero_transfer_query> &query);
  static bool is_contextual(const monero::monero_transfer_query &query);
};

struct PyMoneroWalletConfig : public monero::monero_wallet_config {
public:
  boost::optional<std::shared_ptr<PyMoneroConnectionManager>> m_connection_manager;

  PyMoneroWalletConfig() {
    m_connection_manager = boost::none;
  }

  PyMoneroWalletConfig(const PyMoneroWalletConfig& config) {
    m_path = config.m_path;
    m_password = config.m_password;
    m_network_type = config.m_network_type;
    m_server = config.m_server;
    m_seed = config.m_seed;
    m_seed_offset = config.m_seed_offset;
    m_primary_address = config.m_primary_address;
    m_private_view_key = config.m_private_view_key;
    m_private_spend_key = config.m_private_spend_key;
    m_restore_height = config.m_restore_height;
    m_language = config.m_language;
    m_save_current = config.m_save_current;
    m_account_lookahead = config.m_account_lookahead;
    m_subaddress_lookahead = config.m_subaddress_lookahead;
    m_is_multisig = config.m_is_multisig;
    m_connection_manager = config.m_connection_manager;
  }

};

class PyMoneroTxWallet : public monero::monero_tx_wallet {
public:

  static bool decode_rpc_type(const std::string &rpc_type, const std::shared_ptr<monero::monero_tx_wallet> &tx);
  static void init_sent(const monero::monero_tx_config &config, std::shared_ptr<monero::monero_tx_wallet> &tx, bool copy_destinations);
  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing, const monero_tx_config &config);
  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing);
  static void from_property_tree_with_output(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx);
};

class PyMoneroTxSet : public monero::monero_tx_set {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set);
  static void from_tx(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, const std::shared_ptr<monero::monero_tx_wallet> &tx, bool is_outgoing, const monero_tx_config &config);
  static void from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set);
  static void from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, std::vector<std::shared_ptr<monero::monero_tx_wallet>> &txs, const boost::optional<monero_tx_config> &conf);
  static void from_describe_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set);
};

class PyMoneroKeyImage : public monero::monero_key_image {
public:
  PyMoneroKeyImage() {}
  PyMoneroKeyImage(const monero::monero_key_image &key_image) {
    m_hex = key_image.m_hex;
    m_signature = key_image.m_signature;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image>& key_image);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_key_image>>& key_images);
};

class PyMoneroKeyImageImportResult : public monero::monero_key_image_import_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image_import_result>& result);
};

class PyMoneroMultisigInfo : public monero::monero_multisig_info {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_info>& info);
};

class PyMoneroMultisigInitResult : public monero::monero_multisig_init_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_init_result>& info);
};

class PyMoneroMultisigSignResult : public monero::monero_multisig_sign_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_sign_result>& res);
};

class PyMoneroMultisigTxDataParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_multisig_tx_hex;

  PyMoneroMultisigTxDataParams() {}
  PyMoneroMultisigTxDataParams(const std::string& multisig_tx_hex) {
    m_multisig_tx_hex = multisig_tx_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroDecodedAddress {
public:
  std::string m_address;
  PyMoneroAddressType m_address_type;
  monero::monero_network_type m_network_type;

  PyMoneroDecodedAddress(std::string& address, PyMoneroAddressType address_type, monero::monero_network_type network_type) {
    m_address = address;
    m_address_type = address_type;
    m_network_type = network_type;
  }

};

class PyMoneroAccountTag {
public:
  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;
  std::vector<uint32_t> m_account_indices;

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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAccountTag>& account_tag);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroAccountTag>>& account_tags);
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

  static void from_rpc_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress);
  static void from_rpc_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_subaddress>>& subaddresses);
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress);
};

class PyMoneroIntegratedAddress : public monero::monero_integrated_address {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_integrated_address>& subaddress);
};

class PyMoneroAccount : public monero::monero_account {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_account>& account);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_account>>& accounts);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<monero::monero_account>& accounts);
};

class PyMoneroWalletGetHeightResponse {
public:

  static uint64_t from_property_tree(const boost::property_tree::ptree& node);
};

class PyMoneroQueryKeyParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key_type;

  PyMoneroQueryKeyParams() { }
  PyMoneroQueryKeyParams(const std::string& key_type) {
    m_key_type = key_type;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroQueryOutputParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key_image;

  PyMoneroQueryOutputParams() { }
  PyMoneroQueryOutputParams(const std::string& key_image) {
    m_key_image = key_image;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetAddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddress_indices;

  PyMoneroGetAddressParams() { }
  PyMoneroGetAddressParams(uint32_t account_index, const std::vector<uint32_t>& subaddress_indices) {
    m_account_index = account_index;
    m_subaddress_indices = subaddress_indices;
  }
  PyMoneroGetAddressParams(uint32_t account_index) {
    m_account_index = account_index;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetAddressIndexParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;

  PyMoneroGetAddressIndexParams() { }
  PyMoneroGetAddressIndexParams(const std::string& address) {
    m_address = address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSplitIntegratedAddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_integrated_address;

  PyMoneroSplitIntegratedAddressParams() { }
  PyMoneroSplitIntegratedAddressParams(const std::string& integrated_address) {
    m_integrated_address = integrated_address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroPrepareMultisigParams : public PyMoneroJsonRequestParams {
public:
  // TODO monero-docs document this parameter
  boost::optional<bool> m_enable_multisig_experimental;
  PyMoneroPrepareMultisigParams(bool enable_multisig_experimental = true) {
    m_enable_multisig_experimental = enable_multisig_experimental;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroExportMultisigHexResponse {
public:

  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

class PyMoneroImportMultisigHexParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_hexes;

  PyMoneroImportMultisigHexParams() {}

  PyMoneroImportMultisigHexParams(const std::vector<std::string>& multisig_hexes) {
    m_multisig_hexes = multisig_hexes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroImportMultisigHexResponse {
public:

  static int from_property_tree(const boost::property_tree::ptree& node);
};

class PyMoneroSubmitMultisigTxHexResponse {
public:
  PyMoneroSubmitMultisigTxHexResponse() {}
  static std::vector<std::string> from_property_tree(const boost::property_tree::ptree& node);
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};
  
class PyMoneroPrepareMakeMultisigResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node);
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroParsePaymentUriParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_uri;

  PyMoneroParsePaymentUriParams() {}
  PyMoneroParsePaymentUriParams(const std::string& uri) {
    m_uri = uri;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroParsePaymentUriResponse {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_payment_id;
  boost::optional<std::string> m_recipient_name;
  boost::optional<std::string> m_tx_description;

  PyMoneroParsePaymentUriResponse() {}

  std::shared_ptr<monero::monero_tx_config> to_tx_config() const;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroParsePaymentUriResponse>& response);
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetPaymentUriResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

class PyMoneroGetBalanceParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint32_t> m_account_idx;
  std::vector<uint32_t> m_address_indices;
  boost::optional<bool> m_all_accounts;
  boost::optional<bool> m_strict;

  PyMoneroGetBalanceParams() {};
  PyMoneroGetBalanceParams(bool all_accounts, bool strict = false) {
    m_all_accounts = all_accounts;
    m_strict = strict;
  };

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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetBalanceResponse {
public:
  boost::optional<uint64_t> m_balance;
  boost::optional<uint64_t> m_unlocked_balance;
  boost::optional<bool> m_multisig_import_needed;
  boost::optional<uint64_t> m_time_to_unlock;
  boost::optional<uint64_t> m_blocks_to_unlock;
  std::vector<std::shared_ptr<monero::monero_subaddress>> m_per_subaddress;

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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBalanceResponse>& response);
};

class PyMoneroCreateAccountParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_tag;

  PyMoneroCreateAccountParams(const std::string& tag = "") {
    m_tag = tag;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroCloseWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_save;

  PyMoneroCloseWalletParams(bool save = true) {
    m_save = save;
  };

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroChangeWalletPasswordParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_old_password;
  boost::optional<std::string> m_new_password;

  PyMoneroChangeWalletPasswordParams(const std::string& old_password, const std::string& new_password) {
    m_old_password = old_password;
    m_new_password = new_password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroWalletAttributeParams>& attributes);
};

class PyMoneroScanTxParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;

  PyMoneroScanTxParams() {}
  PyMoneroScanTxParams(const std::vector<std::string>& tx_hashes) {
    m_tx_hashes = tx_hashes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroAutoRefreshParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_enable;

  PyMoneroAutoRefreshParams(bool enable): m_enable(enable) { } 

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroAddressBookEntry : public monero::monero_address_book_entry {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_address_book_entry>& entry);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_address_book_entry>>& entries);
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

class PyMoneroGetAccountsParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_label;

  PyMoneroGetAccountsParams() {}
  PyMoneroGetAccountsParams(const std::string& label) {
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroVerifySignMessageParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_data;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_signature;
  boost::optional<monero::monero_message_signature_type> m_signature_type;

  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_address_index;


  PyMoneroVerifySignMessageParams() {}

  PyMoneroVerifySignMessageParams(const std::string &data, const std::string &address, const std::string& signature) {
    m_data = data;
    m_address = address;
    m_signature = signature;
  }

  PyMoneroVerifySignMessageParams(const std::string &data, monero::monero_message_signature_type signature_type, uint32_t account_index, uint32_t address_index) {
    m_data = data;
    m_signature_type = signature_type;
    m_account_index = account_index;
    m_address_index = address_index;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroCheckTxKeyParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_tx_hash;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_tx_key;

  PyMoneroCheckTxKeyParams() {}

  PyMoneroCheckTxKeyParams(const std::string &tx_hash) {
    m_tx_hash = tx_hash;
  }

  PyMoneroCheckTxKeyParams(const std::string &tx_hash, const std::string &tx_key, const std::string &address) {
    m_tx_hash = tx_hash;
    m_tx_key = tx_key;
    m_address = address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSignDescribeTransferParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_unsigned_txset;
  boost::optional<std::string> m_multisig_txset;

  PyMoneroSignDescribeTransferParams() {}

  PyMoneroSignDescribeTransferParams(const std::string &unsigned_txset) {
    m_unsigned_txset = unsigned_txset;
  }

  PyMoneroSignDescribeTransferParams(const std::string &unsigned_txset, const std::string &multisig_txset) {
    m_unsigned_txset = unsigned_txset;
    m_multisig_txset = multisig_txset;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroWalletRelayTxParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_hex;

  PyMoneroWalletRelayTxParams() {}

  PyMoneroWalletRelayTxParams(const std::string &hex) {
    m_hex = hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSweepParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddr_indices;
  boost::optional<std::string> m_key_image;
  boost::optional<bool> m_relay;
  boost::optional<monero_tx_priority> m_priority;
  boost::optional<std::string> m_payment_id;
  boost::optional<uint64_t> m_below_amount;
  boost::optional<bool> m_get_tx_key;
  boost::optional<bool> m_get_tx_hex;
  boost::optional<bool> m_get_tx_metadata;
  
  PyMoneroSweepParams(bool relay = false) {
    m_relay = relay;
  }

  PyMoneroSweepParams(const monero_tx_config& config);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSubmitTransferParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_signed_tx_hex;

  PyMoneroSubmitTransferParams() {}
  PyMoneroSubmitTransferParams(const std::string& signed_tx_hex) {
    m_signed_tx_hex = signed_tx_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroCreateSubaddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_label;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_subaddress_index;

  PyMoneroCreateSubaddressParams() {}
  PyMoneroCreateSubaddressParams(uint32_t account_idx, const std::string& label) {
    m_account_index = account_idx;
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSetSubaddressLabelParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_label;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_subaddress_index;

  PyMoneroSetSubaddressLabelParams() {}
  PyMoneroSetSubaddressLabelParams(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
    m_account_index = account_idx;
    m_subaddress_index = subaddress_idx;
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroImportExportOutputsParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_outputs_hex;
  boost::optional<bool> m_all;

  PyMoneroImportExportOutputsParams() {}
  PyMoneroImportExportOutputsParams(bool all) {
    m_all = all;
  }
  PyMoneroImportExportOutputsParams(const std::string& outputs_hex) {
    m_outputs_hex = outputs_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroImportExportKeyImagesParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_all;
  std::vector<std::shared_ptr<PyMoneroKeyImage>> m_key_images;

  PyMoneroImportExportKeyImagesParams() {}
  PyMoneroImportExportKeyImagesParams(const std::vector<std::shared_ptr<monero::monero_key_image>> &key_images) {
    for(const auto &key_image : key_images) {
      m_key_images.push_back(std::make_shared<PyMoneroKeyImage>(*key_image));
    }
  }
  PyMoneroImportExportKeyImagesParams(const std::vector<std::shared_ptr<PyMoneroKeyImage>> &key_images) {
    m_key_images = key_images;
  }
  PyMoneroImportExportKeyImagesParams(bool all) {
    m_all = all;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroCreateOpenWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_filename;
  boost::optional<std::string> m_password;
  boost::optional<std::string> m_language;
  boost::optional<std::string> m_seed;
  boost::optional<std::string> m_seed_offset;
  boost::optional<uint64_t> m_restore_height;
  boost::optional<bool> m_autosave_current;
  boost::optional<bool> m_enable_multisig_experimental;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_view_key;
  boost::optional<std::string> m_spend_key;

  PyMoneroCreateOpenWalletParams() {}

  PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password);

  PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &language);

  PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &seed, const boost::optional<std::string> &seed_offset, const boost::optional<uint64_t> &restore_height, const boost::optional<std::string> &language, const boost::optional<bool> &autosave_current, const boost::optional<bool> &enable_multisig_experimental);

  PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &address, const boost::optional<std::string> &view_key, const boost::optional<std::string> &spend_key, const boost::optional<uint64_t> &restore_height, const boost::optional<bool> &autosave_current);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroReserveProofParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_all;
  boost::optional<std::string> m_message;
  boost::optional<std::string> m_tx_hash;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_signature;

  PyMoneroReserveProofParams() {}

  PyMoneroReserveProofParams(const std::string &message, bool all = true);

  PyMoneroReserveProofParams(const std::string &address, const std::string &message, const std::string &signature);

  PyMoneroReserveProofParams(const std::string &tx_hash, const std::string &address, const std::string &message, const std::string &signature);

  PyMoneroReserveProofParams(const std::string &tx_hash, const std::string &message);

  PyMoneroReserveProofParams(uint32_t account_index, uint64_t amount, const std::string &message);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroRefreshWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_enable;
  boost::optional<uint64_t> m_period;
  boost::optional<uint64_t> m_start_height;

  PyMoneroRefreshWalletParams() {}

  PyMoneroRefreshWalletParams(bool enable, uint64_t period) {
    m_enable = enable;
    m_period = period;
  }

  PyMoneroRefreshWalletParams(uint64_t start_height) {
    m_start_height = start_height;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroTransferParams : public PyMoneroJsonRequestParams {
public:
  std::vector<uint32_t> m_subtract_fee_from_outputs;
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddress_indices;
  boost::optional<std::string> m_payment_id;
  boost::optional<bool> m_do_not_relay;
  boost::optional<int> m_priority;
  boost::optional<bool> m_get_tx_hex;
  boost::optional<bool> m_get_tx_metadata;
  boost::optional<bool> m_get_tx_keys;
  boost::optional<bool> m_get_tx_key;
  std::vector<std::shared_ptr<monero::monero_destination>> m_destinations;

  PyMoneroTransferParams() {}
  PyMoneroTransferParams(const monero::monero_tx_config &config);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroCheckReserve : public monero::monero_check_reserve {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_reserve>& check);
};

class PyMoneroCheckTxProof : public monero::monero_check_tx {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_tx>& check);
};

class PyMoneroReserveProofSignature {
public:

  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

class PyMoneroMessageSignatureResult : public monero::monero_message_signature_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_message_signature_result> result);
};

