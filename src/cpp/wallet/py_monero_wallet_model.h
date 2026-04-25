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

struct monero_decoded_address : public monero::serializable_struct {
public:
  std::string m_address;
  monero_address_type m_address_type;
  monero::monero_network_type m_network_type;

  monero_decoded_address(const std::string& address, monero_address_type address_type, monero::monero_network_type network_type);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
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

struct monero_wallet_balance {
public:
  uint64_t m_balance;
  uint64_t m_unlocked_balance;

  monero_wallet_balance(uint64_t balance = 0, uint64_t unlocked_balance = 0): m_balance(balance), m_unlocked_balance(unlocked_balance) { }
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
