/**
 * Copyright (c) everoddandeven
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Parts of this file are originally copyright (c) 2025-2026 woodser
 *
 * Parts of this file are originally copyright (c) 2014-2019, The Monero Project
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * All rights reserved.
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of
 *    conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list
 *    of conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be
 *    used to endorse or promote products derived from this software without specific
 *    prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
 * THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Parts of this file are originally copyright (c) 2012-2013 The Cryptonote developers
 */
#pragma once

#include "daemon/py_monero_daemon_model.h"
#include "wallet/monero_wallet_model.h"

// ------------------------------ Custom Data Model ---------------------------------

struct PyMoneroTxQuery : public monero::monero_tx_query {
public:

  static std::shared_ptr<monero::monero_tx_query> decontextualize(const std::shared_ptr<monero::monero_tx_query> &query);
};

struct PyMoneroOutputQuery : public monero::monero_output_query {
public:

  static bool is_contextual(const monero::monero_output_query &query);
};

struct PyMoneroTransferQuery : public monero::monero_transfer_query {
public:

  static bool is_contextual(const monero::monero_transfer_query &query);
};

struct PyMoneroTxWallet : public monero::monero_tx_wallet {
public:

  static bool decode_rpc_type(const std::string &rpc_type, const std::shared_ptr<monero::monero_tx_wallet> &tx);
  static void init_sent(const monero::monero_tx_config &config, std::shared_ptr<monero::monero_tx_wallet> &tx, bool copy_destinations);
  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing, const monero_tx_config &config);
  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing);
  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx);
  static void from_property_tree_with_transfer_and_merge(const boost::property_tree::ptree& node, std::unordered_map<std::string, std::shared_ptr<monero::monero_tx_wallet>>& tx_map, std::unordered_map<uint64_t, std::shared_ptr<monero::monero_block>>& block_map);
  static void from_property_tree_with_output(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx);
  static void from_property_tree_with_output_and_merge(const boost::property_tree::ptree& node, std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>& tx_map, std::unordered_map<uint64_t, std::shared_ptr<monero_block>>& block_map);
  static void merge_tx(const std::shared_ptr<monero::monero_tx_wallet>& tx, std::unordered_map<std::string, std::shared_ptr<monero::monero_tx_wallet>>& tx_map, std::unordered_map<uint64_t, std::shared_ptr<monero::monero_block>>& block_map);
};

struct PyMoneroTxSet : public monero::monero_tx_set {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set);
  static void from_tx(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, const std::shared_ptr<monero::monero_tx_wallet> &tx, bool is_outgoing, const monero_tx_config &config);
  static void from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set);
  static void from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, std::vector<std::shared_ptr<monero::monero_tx_wallet>> &txs, const boost::optional<monero_tx_config> &conf);
  static void from_describe_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set);
};

struct PyMoneroKeyImage : public monero::monero_key_image {
public:

  PyMoneroKeyImage(const monero::monero_key_image &key_image);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image>& key_image);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_key_image>>& key_images);
};

struct PyMoneroKeyImageImportResult : public monero::monero_key_image_import_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image_import_result>& result);
};

struct PyMoneroMultisigInfo : public monero::monero_multisig_info {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_info>& info);
};

struct PyMoneroMultisigInitResult : public monero::monero_multisig_init_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_init_result>& info);
};

struct PyMoneroMultisigSignResult : public monero::monero_multisig_sign_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_sign_result>& res);
};

struct PyMoneroTransfer : public monero_transfer {
public:
  using monero_transfer::monero_transfer;

  boost::optional<bool> is_incoming() const override {
    PYBIND11_OVERRIDE_PURE(boost::optional<bool>, monero_transfer, is_incoming);
  }
};

struct PyMoneroSubaddress : public monero::monero_subaddress {
public:

  static void from_rpc_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress);
  static void from_rpc_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_subaddress>>& subaddresses);
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress);
};

struct PyMoneroIntegratedAddress : public monero::monero_integrated_address {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_integrated_address>& subaddress);
};

struct PyMoneroAccount : public monero::monero_account {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_account>& account);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_account>>& accounts);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<monero::monero_account>& accounts);
};

struct PyMoneroAddressBookEntry : public monero::monero_address_book_entry {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_address_book_entry>& entry);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_address_book_entry>>& entries);
};

struct PyMoneroCheckReserve : public monero::monero_check_reserve {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_reserve>& check);
};

struct PyMoneroCheckTxProof : public monero::monero_check_tx {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_tx>& check);
};

struct PyMoneroMessageSignatureResult : public monero::monero_message_signature_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_message_signature_result> result);
};

// ------------------------------ Extended Data Model ---------------------------------

enum monero_address_type : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
};

// Compares two transactions by their height
struct monero_tx_height_comparator {
  bool operator()(const std::shared_ptr<monero::monero_tx>& tx1, const std::shared_ptr<monero::monero_tx>& tx2) const;
};

// Compares two transfers by ascending account and subaddress indices
struct monero_incoming_transfer_comparator {
  bool operator()(const std::shared_ptr<monero::monero_incoming_transfer>& t1, const std::shared_ptr<monero::monero_incoming_transfer>& t2) const;
  bool operator()(const monero::monero_incoming_transfer& t1, const monero::monero_incoming_transfer& t2) const;
};

// Compares two outputs by ascending account and subaddress indices
struct monero_output_comparator {
  bool operator()(const monero::monero_output_wallet& o1, const monero::monero_output_wallet& o2) const;
};

struct monero_decoded_address {
public:
  std::string m_address;
  monero_address_type m_address_type;
  monero::monero_network_type m_network_type;

  monero_decoded_address(const std::string& address, monero_address_type address_type, monero::monero_network_type network_type);
};

struct monero_account_tag : public monero::serializable_struct {
public:
  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;
  std::vector<uint32_t> m_account_indices;

  monero_account_tag() { }
  monero_account_tag(const std::string& tag, const std::string& label): m_tag(tag), m_label(label) { }
  monero_account_tag(const std::string& tag, const std::string& label, const std::vector<uint32_t>& account_indices): m_tag(tag), m_label(label), m_account_indices(account_indices) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_account_tag>& account_tag);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_account_tag>>& account_tags);
};

struct monero_signature {
public:

  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_wallet_balance {
public:
  uint64_t m_balance;
  uint64_t m_unlocked_balance;

  monero_wallet_balance(uint64_t balance = 0, uint64_t unlocked_balance = 0): m_balance(balance), m_unlocked_balance(unlocked_balance) { }
};

// ------------------------------ JSON-RPC Params ---------------------------------

struct monero_multisig_tx_data_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_multisig_tx_hex;

  monero_multisig_tx_data_params(const std::string& multisig_tx_hex): m_multisig_tx_hex(multisig_tx_hex) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_query_key_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_key_type;

  monero_query_key_params(const std::string& key_type): m_key_type(key_type) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_query_output_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_key_image;

  monero_query_output_params(const std::string& key_image): m_key_image(key_image) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_address_params : public monero_json_request_params {
public:
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddress_indices;

  monero_get_address_params(uint32_t account_index): m_account_index(account_index) { }
  monero_get_address_params(uint32_t account_index, const std::vector<uint32_t>& subaddress_indices): m_account_index(account_index), m_subaddress_indices(subaddress_indices) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_address_index_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_address;

  monero_get_address_index_params(const std::string& address): m_address(address) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_make_integrated_address_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_standard_address;
  boost::optional<std::string> m_payment_id;

  monero_make_integrated_address_params(const std::string& standard_address, const std::string& payment_id): m_standard_address(standard_address), m_payment_id(payment_id) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_split_integrated_address_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_integrated_address;

  monero_split_integrated_address_params(const std::string& integrated_address): m_integrated_address(integrated_address) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_prepare_multisig_params : public monero_json_request_params {
public:
  // TODO monero-docs document this parameter
  boost::optional<bool> m_enable_multisig_experimental;

  monero_prepare_multisig_params(bool enable_multisig_experimental = true): m_enable_multisig_experimental(enable_multisig_experimental) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_import_multisig_hex_params : public monero_json_request_params {
public:
  std::vector<std::string> m_multisig_hexes;

  monero_import_multisig_hex_params(const std::vector<std::string>& multisig_hexes): m_multisig_hexes(multisig_hexes) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_make_multisig_params : public monero_json_request_params {
public:
  std::vector<std::string> m_multisig_info;
  boost::optional<int> m_threshold;
  boost::optional<std::string> m_password;

  monero_make_multisig_params(const std::vector<std::string>& multisig_hexes, const std::string& password): m_multisig_info(multisig_hexes), m_password(password) { }
  monero_make_multisig_params(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password): m_multisig_info(multisig_hexes), m_threshold(threshold), m_password(password) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_parse_payment_uri_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_uri;

  monero_parse_payment_uri_params(const std::string& uri): m_uri(uri) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_payment_uri : public monero_json_request_params {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_payment_id;
  boost::optional<std::string> m_recipient_name;
  boost::optional<std::string> m_tx_description;

  monero_get_payment_uri() { }
  monero_get_payment_uri(const monero_tx_config& config);

  std::shared_ptr<monero::monero_tx_config> to_tx_config() const;
  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_payment_uri>& response);
  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_get_balance_params : public monero_json_request_params {
public:
  boost::optional<uint32_t> m_account_idx;
  std::vector<uint32_t> m_address_indices;
  boost::optional<bool> m_all_accounts;
  boost::optional<bool> m_strict;

  monero_get_balance_params(bool all_accounts, bool strict = false): m_all_accounts(all_accounts), m_strict(strict) { }
  monero_get_balance_params(uint32_t account_idx, const std::vector<uint32_t>& address_indices, bool all_accounts = false, bool strict = false): m_account_idx(account_idx), m_address_indices(address_indices), m_all_accounts(all_accounts), m_strict(strict) { }
  monero_get_balance_params(uint32_t account_idx, boost::optional<uint32_t> address_idx, bool all_accounts = false, bool strict = false);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_create_account_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_tag;

  monero_create_account_params(const std::string& tag = ""): m_tag(tag) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_close_wallet_params : public monero_json_request_params {
public:
  boost::optional<bool> m_save;

  monero_close_wallet_params(bool save = false): m_save(save) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_change_wallet_password_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_old_password;
  boost::optional<std::string> m_new_password;

  monero_change_wallet_password_params(const std::string& old_password, const std::string& new_password): m_old_password(old_password), m_new_password(new_password) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_key_value : public monero_json_request_params {
public:
  boost::optional<std::string> m_key;
  boost::optional<std::string> m_value;

  monero_key_value() { }
  monero_key_value(const std::string& key): m_key(key) { }
  monero_key_value(const std::string& key, const std::string& value): m_key(key), m_value(value) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_key_value>& attributes);
};

struct monero_set_daemon_params : public monero_json_request_params {
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

struct monero_auto_refresh_params : public monero_json_request_params {
public:
  boost::optional<bool> m_enable;

  monero_auto_refresh_params(bool enable): m_enable(enable) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_tag_accounts_params : public monero_json_request_params {
public:
  std::vector<uint32_t> m_account_indices;
  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;

  monero_tag_accounts_params(const std::string& tag, const std::string& label = ""): m_tag(tag), m_label(label) { }
  monero_tag_accounts_params(const std::vector<uint32_t>& account_indices): m_account_indices(account_indices) { }
  monero_tag_accounts_params(const std::string& tag, const std::vector<uint32_t>& account_indices): m_tag(tag), m_account_indices(account_indices) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_tx_notes_params : public monero_json_request_params {
public:
  std::vector<std::string> m_tx_hashes;
  std::vector<std::string> m_notes;

  monero_tx_notes_params(const std::vector<std::string>& tx_hashes): m_tx_hashes(tx_hashes) { }
  monero_tx_notes_params(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes): m_tx_hashes(tx_hashes), m_notes(notes) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_address_book_entry_params : public monero_json_request_params {
public:
  boost::optional<uint64_t> m_index;  // TODO: not boost::optional
  boost::optional<bool> m_set_address;
  boost::optional<std::string> m_address;
  boost::optional<bool> m_set_description;
  boost::optional<std::string> m_description;
  std::vector<uint64_t> m_entries;

  monero_address_book_entry_params(uint64_t index): m_index(index) { }
  monero_address_book_entry_params(const std::vector<uint64_t>& entries): m_entries(entries) { }
  monero_address_book_entry_params(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description): m_index(index), m_set_address(set_address), m_address(address), m_set_description(set_description), m_description(description) { }
  monero_address_book_entry_params(const std::string& address, const std::string& description): m_address(address), m_description(description) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_verify_sign_message_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_data;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_signature;
  boost::optional<monero::monero_message_signature_type> m_signature_type;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_address_index;

  monero_verify_sign_message_params(const std::string &data, const std::string &address, const std::string& signature): m_data(data), m_address(address), m_signature(signature) { }
  monero_verify_sign_message_params(const std::string &data, monero::monero_message_signature_type signature_type, uint32_t account_index, uint32_t address_index): m_data(data), m_signature_type(signature_type), m_account_index(account_index), m_address_index(address_index) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_check_tx_key_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_tx_hash;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_tx_key;

  monero_check_tx_key_params(const std::string &tx_hash): m_tx_hash(tx_hash) { }
  monero_check_tx_key_params(const std::string &tx_hash, const std::string &tx_key, const std::string &address): m_tx_hash(tx_hash), m_tx_key(tx_key), m_address(address) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_sign_describe_transfer_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_unsigned_txset;
  boost::optional<std::string> m_multisig_txset;

  monero_sign_describe_transfer_params() { }
  monero_sign_describe_transfer_params(const std::string &unsigned_txset) : m_unsigned_txset(unsigned_txset) { }
  monero_sign_describe_transfer_params(const std::string &unsigned_txset, const std::string &multisig_txset) : m_unsigned_txset(unsigned_txset), m_multisig_txset(multisig_txset) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_wallet_relay_tx_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_hex;

  monero_wallet_relay_tx_params(const std::string &hex): m_hex(hex) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_sweep_params : public monero_json_request_params {
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
  boost::optional<bool> m_get_tx_keys;
  boost::optional<bool> m_get_tx_hex;
  boost::optional<bool> m_get_tx_metadata;

  monero_sweep_params(bool relay = false): m_relay(relay) { }
  monero_sweep_params(const monero_tx_config& config);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_submit_transfer_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_signed_tx_hex;

  monero_submit_transfer_params(const std::string& signed_tx_hex): m_signed_tx_hex(signed_tx_hex) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_create_edit_subaddress_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_label;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_subaddress_index;

  monero_create_edit_subaddress_params(uint32_t account_idx, const std::string& label): m_account_index(account_idx), m_label(label) { }
  monero_create_edit_subaddress_params(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label): m_account_index(account_idx), m_subaddress_index(subaddress_idx), m_label(label) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_import_export_outputs_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_outputs_hex;
  boost::optional<bool> m_all;

  monero_import_export_outputs_params(bool all): m_all(all) { }
  monero_import_export_outputs_params(const std::string& outputs_hex): m_outputs_hex(outputs_hex) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_import_export_key_images_params : public monero_json_request_params {
public:
  boost::optional<bool> m_all;
  std::vector<std::shared_ptr<PyMoneroKeyImage>> m_key_images;

  monero_import_export_key_images_params(const std::vector<std::shared_ptr<monero::monero_key_image>> &key_images);
  monero_import_export_key_images_params(const std::vector<std::shared_ptr<PyMoneroKeyImage>> &key_images): m_key_images(key_images) { }
  monero_import_export_key_images_params(bool all): m_all(all) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_create_open_wallet_params : public monero_json_request_params {
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

  monero_create_open_wallet_params(const boost::optional<std::string>& filename, const boost::optional<std::string> &password): m_filename(filename), m_password(password), m_autosave_current(false) { }
  monero_create_open_wallet_params(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &language): m_filename(filename), m_password(password), m_language(language), m_autosave_current(false) { }
  monero_create_open_wallet_params(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &seed, const boost::optional<std::string> &seed_offset, const boost::optional<uint64_t> &restore_height, const boost::optional<std::string> &language, const boost::optional<bool> &autosave_current, const boost::optional<bool> &enable_multisig_experimental): m_filename(filename), m_password(password), m_seed(seed), m_seed_offset(seed_offset), m_restore_height(restore_height), m_language(language), m_autosave_current(autosave_current), m_enable_multisig_experimental(enable_multisig_experimental) { }
  monero_create_open_wallet_params(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &address, const boost::optional<std::string> &view_key, const boost::optional<std::string> &spend_key, const boost::optional<uint64_t> &restore_height, const boost::optional<bool> &autosave_current): m_filename(filename), m_password(password), m_address(address), m_view_key(view_key), m_spend_key(spend_key), m_restore_height(restore_height), m_autosave_current(autosave_current) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_reserve_proof_params : public monero_json_request_params {
public:
  boost::optional<bool> m_all;
  boost::optional<std::string> m_message;
  boost::optional<std::string> m_tx_hash;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_signature;

  monero_reserve_proof_params(const std::string &message, bool all = true): m_all(all), m_message(message) { }
  monero_reserve_proof_params(const std::string &address, const std::string &message, const std::string &signature): m_address(address), m_message(message), m_signature(signature) { }
  monero_reserve_proof_params(const std::string &tx_hash, const std::string &address, const std::string &message, const std::string &signature): m_tx_hash(tx_hash), m_address(address), m_message(message), m_signature(signature) { }
  monero_reserve_proof_params(const std::string &tx_hash, const std::string &message): m_tx_hash(tx_hash), m_message(message) { }
  monero_reserve_proof_params(uint32_t account_index, uint64_t amount, const std::string &message): m_account_index(account_index), m_amount(amount), m_message(message) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_refresh_wallet_params : public monero_json_request_params {
public:
  boost::optional<bool> m_enable;
  boost::optional<uint64_t> m_period;
  boost::optional<uint64_t> m_start_height;

  monero_refresh_wallet_params() { }
  monero_refresh_wallet_params(bool enable, uint64_t period): m_enable(enable), m_period(period) { }
  monero_refresh_wallet_params(uint64_t start_height): m_start_height(start_height) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_transfer_params : public monero_json_request_params {
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

  monero_transfer_params(const monero::monero_tx_config &config);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_transfers_params : public monero_json_request_params {
public:
  boost::optional<bool> m_in;
  boost::optional<bool> m_out;
  boost::optional<bool> m_pool;
  boost::optional<bool> m_pending;
  boost::optional<bool> m_failed;
  boost::optional<uint64_t> m_min_height;
  boost::optional<uint64_t> m_max_height;
  boost::optional<bool> m_all_accounts;
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddr_indices;

  bool filter_by_height() const { return m_min_height != boost::none || m_max_height != boost::none; }
  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_incoming_transfers_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_transfer_type;
  boost::optional<bool> m_verbose;
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddr_indices;

  monero_get_incoming_transfers_params(const std::string& transfer_type, bool verbose = true): m_transfer_type(transfer_type), m_verbose(verbose) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

// ------------------------------ JSON-RPC Response ---------------------------------

struct monero_wallet_get_height_response {
public:
  static uint64_t from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_export_multisig_hex_response {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_import_multisig_hex_response {
public:
  static int from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_submit_multisig_tx_hex_response {
public:
  static std::vector<std::string> from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_prepare_make_multisig_response {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node);
};

struct monero_get_balance_response {
public:
  boost::optional<uint64_t> m_balance;
  boost::optional<uint64_t> m_unlocked_balance;
  boost::optional<bool> m_multisig_import_needed;
  boost::optional<uint64_t> m_time_to_unlock;
  boost::optional<uint64_t> m_blocks_to_unlock;
  std::vector<std::shared_ptr<monero::monero_subaddress>> m_per_subaddress;

  monero_get_balance_response(): m_balance(0), m_unlocked_balance(0) { }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_balance_response>& response);
};

// ------------------------------ Utilities ---------------------------------

// TODO expose bool_equals_2 from monero-cpp
bool bool_equals_2(bool val, const boost::optional<bool>& opt_val);
bool tx_height_less_than(const std::shared_ptr<monero_tx>& tx1, const std::shared_ptr<monero_tx>& tx2);
bool incoming_transfer_before(const std::shared_ptr<monero_incoming_transfer>& transfer1, const std::shared_ptr<monero_incoming_transfer>& transfer2);
bool vout_before(const std::shared_ptr<monero_output>& o1, const std::shared_ptr<monero_output>& o2);

template <typename Parent, typename Child>
void set_query(std::shared_ptr<Parent>& self, boost::optional<std::shared_ptr<Child>>& field, const boost::optional<std::shared_ptr<Child>>& val) {

  const auto old = field;
  field = val;

  // set new reference
  if (field != boost::none) {
    field.get()->m_tx_query = self;
  }

  // cleanup old
  if (old != boost::none) {
    if (val != boost::none && val.get() == old.get()) {
      return;
    }
    old.get()->m_tx_query = boost::none;
  }
}
