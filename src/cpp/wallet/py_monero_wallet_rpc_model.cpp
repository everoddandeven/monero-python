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

#include "py_monero_wallet_rpc_model.h"
#include "utils/monero_utils.h"

// --------------------------- MONERO GET PAYMENT URI ---------------------------

monero_payment_uri_params::monero_payment_uri_params(const monero_tx_config& config):
  m_recipient_name(config.m_recipient_name),
  m_tx_description(config.m_note),
  m_payment_id(config.m_payment_id) {

  if (config.m_destinations.empty()) {
    m_address = config.m_address;
    m_amount = config.m_amount;
  } else {
    const auto& dest = config.m_destinations[0];
    m_address = dest->m_address;
    m_amount = dest->m_amount;
  }
}

std::string monero_payment_uri_params::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("uri")) return it->second.data();
  }
  throw std::runtime_error("Invalid make uri response");
}

void monero_payment_uri_params::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_payment_uri_params>& response) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("uri")) {
      monero_payment_uri_params::from_property_tree(it->second, response);
      return;
    }
    if (key == std::string("address") && !it->second.data().empty()) response->m_address = it->second.data();
    else if (key == std::string("amount")) response->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("payment_id") && !it->second.data().empty()) response->m_payment_id = it->second.data();
    else if (key == std::string("recipient_name") && !it->second.data().empty()) response->m_recipient_name = it->second.data();
    else if (key == std::string("tx_description") && !it->second.data().empty()) response->m_tx_description = it->second.data();
  }
}

std::shared_ptr<monero::monero_tx_config> monero_payment_uri_params::to_tx_config() const {
  auto tx_config = std::make_shared<monero::monero_tx_config>();
  tx_config->m_payment_id = m_payment_id;
  tx_config->m_recipient_name = m_recipient_name;
  tx_config->m_note = m_tx_description;
  auto dest = std::make_shared<monero::monero_destination>();
  dest->m_amount = m_amount;
  dest->m_address = m_address;
  tx_config->m_destinations.push_back(dest);
  return tx_config;
}

rapidjson::Value monero_payment_uri_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);
  if (m_recipient_name != boost::none) monero_utils::add_json_member("recipient_name", m_recipient_name.get(), allocator, root, value_str);
  if (m_tx_description != boost::none) monero_utils::add_json_member("tx_description", m_tx_description.get(), allocator, root, value_str);
  if (m_uri != boost::none) monero_utils::add_json_member("uri", m_uri.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO SIGNATURE ---------------------------

std::string monero_signature::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("signature")) return it->second.data();
  }

  throw std::runtime_error("Invalid reserve proof response");
}

// --------------------------- MONERO GET BALANCE PARAMS ---------------------------

monero_get_balance_params::monero_get_balance_params(uint32_t account_idx, boost::optional<uint32_t> address_idx, bool all_accounts, bool strict):
  m_account_idx(account_idx),
  m_all_accounts(all_accounts),
  m_strict(strict) {
  if (address_idx != boost::none) m_address_indices.push_back(address_idx.get());
}

rapidjson::Value monero_get_balance_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_idx != boost::none) monero_utils::add_json_member("account_index", m_account_idx.get(), allocator, root, value_num);

  // set bool values
  if (m_all_accounts != boost::none) monero_utils::add_json_member("all_accounts", m_all_accounts.get(), allocator, root);
  if (m_strict != boost::none) monero_utils::add_json_member("strict", m_strict.get(), allocator, root);

  // set sub-arrays
  if (!m_address_indices.empty()) root.AddMember("address_indices", monero_utils::to_rapidjson_val(allocator, m_address_indices), allocator);

  // return root
  return root;
}

// --------------------------- MONERO IMPORT EXPORT KEY IMAGES PARAMS ---------------------------

monero_wallet_data_params::monero_wallet_data_params(const std::vector<std::shared_ptr<monero::monero_key_image>> &key_images) {
  for(const auto &key_image : key_images) {
    m_key_images.push_back(std::make_shared<PyMoneroKeyImage>(*key_image));
  }
}

rapidjson::Value monero_wallet_data_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_outputs_hex != boost::none) monero_utils::add_json_member("outputs_data_hex", m_outputs_hex.get(), allocator, root, value_str);

  // set bool values
  if (m_all != boost::none) monero_utils::add_json_member("all", m_all.get(), allocator, root);

  // set sub-arrays
  if (m_all == boost::none && m_key_images.size() > 0) root.AddMember("signed_key_images", monero_utils::to_rapidjson_val(allocator, m_key_images), allocator);

  // return root
  return root;
}

// --------------------------- MONERO SWEEP PARAMS ---------------------------

monero_sweep_params::monero_sweep_params(const monero_tx_config& config):
  m_address(config.m_address),
  m_account_index(config.m_account_index),
  m_subaddr_indices(config.m_subaddress_indices),
  m_key_image(config.m_key_image),
  m_relay(config.m_relay),
  m_priority(config.m_priority),
  m_payment_id(config.m_payment_id),
  m_below_amount(config.m_below_amount),
  m_get_tx_key(true),
  m_get_tx_hex(true),
  m_get_tx_metadata(true) {
}

rapidjson::Value monero_sweep_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_key_image != boost::none) monero_utils::add_json_member("key_image", m_key_image.get(), allocator, root, value_str);
  if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value val_num(rapidjson::kNumberType);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, val_num);
  if (m_priority != boost::none) monero_utils::add_json_member("priority", m_priority.get(), allocator, root, val_num);
  if (m_below_amount != boost::none) monero_utils::add_json_member("below_amount", m_below_amount.get(), allocator, root, val_num);

  // set bool values
  if (m_get_tx_key != boost::none) monero_utils::add_json_member("get_tx_key", m_get_tx_key.get(), allocator, root);
  if (m_get_tx_keys != boost::none) monero_utils::add_json_member("get_tx_keys", m_get_tx_keys.get(), allocator, root);
  if (m_get_tx_hex != boost::none) monero_utils::add_json_member("get_tx_hex", m_get_tx_hex.get(), allocator, root);
  if (m_get_tx_metadata != boost::none) monero_utils::add_json_member("get_tx_metadata", m_get_tx_metadata.get(), allocator, root);
  bool relay = bool_equals_2(true, m_relay);
  monero_utils::add_json_member("do_not_relay", !relay, allocator, root);

  // set sub-arrays
  if (m_subaddr_indices.size() > 0) root.AddMember("subaddr_indices", monero_utils::to_rapidjson_val(allocator, m_subaddr_indices), allocator);

  // return root
  return root;
}

// --------------------------- MONERO TRANSFER PARAMS ---------------------------

monero_transfer_params::monero_transfer_params(const monero::monero_tx_config &config) {
  for (const auto& sub_idx : config.m_subaddress_indices) {
    m_subaddress_indices.push_back(sub_idx);
  }

  if (config.m_address != boost::none) {
    auto dest = std::make_shared<monero::monero_destination>();
    dest->m_address = config.m_address;
    dest->m_amount = config.m_amount;
    m_destinations.push_back(dest);
  }

  for (const auto &dest : config.m_destinations) {
    if (dest->m_address == boost::none) throw std::runtime_error("Destination address is not defined");
    if (dest->m_amount == boost::none) throw std::runtime_error("Destination amount is not defined");
    if (config.m_address != boost::none && *dest->m_address == *config.m_address) continue;
    m_destinations.push_back(dest);
  }

  m_subtract_fee_from_outputs = config.m_subtract_fee_from;
  m_account_index = config.m_account_index;
  m_payment_id = config.m_payment_id;
  if (bool_equals_2(true, config.m_relay)) {
    m_do_not_relay = false;
  }
  else {
    m_do_not_relay = true;
  }
  if (config.m_priority == monero_tx_priority::DEFAULT) {
    m_priority = 0;
  }
  else if (config.m_priority == monero_tx_priority::UNIMPORTANT) {
    m_priority = 1;
  }
  else if (config.m_priority == monero_tx_priority::NORMAL) {
    m_priority = 2;
  }
  else if (config.m_priority == monero_tx_priority::ELEVATED) {
    m_priority = 3;
  }
  m_get_tx_hex = true;
  m_get_tx_metadata = true;
  if (bool_equals_2(true, config.m_can_split)) m_get_tx_keys = true;
  else m_get_tx_key = true;
}

rapidjson::Value monero_transfer_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
  if (m_priority != boost::none) monero_utils::add_json_member("priority", m_priority.get(), allocator, root, value_num);

  // set bool values
  if (m_do_not_relay != boost::none) monero_utils::add_json_member("do_not_relay", m_do_not_relay.get(), allocator, root);
  if (m_get_tx_hex != boost::none) monero_utils::add_json_member("get_tx_hex", m_get_tx_hex.get(), allocator, root);
  if (m_get_tx_metadata != boost::none) monero_utils::add_json_member("get_tx_metadata", m_get_tx_metadata.get(), allocator, root);
  if (m_get_tx_keys != boost::none) monero_utils::add_json_member("get_tx_keys", m_get_tx_keys.get(), allocator, root);
  if (m_get_tx_key != boost::none) monero_utils::add_json_member("get_tx_key", m_get_tx_key.get(), allocator, root);

  // set sub-arrays
  if (!m_subtract_fee_from_outputs.empty()) root.AddMember("subtract_fee_from_outputs", monero_utils::to_rapidjson_val(allocator, m_subtract_fee_from_outputs), allocator);
  if (!m_subaddress_indices.empty()) root.AddMember("subaddr_indices", monero_utils::to_rapidjson_val(allocator, m_subaddress_indices), allocator);
  if (!m_destinations.empty()) root.AddMember("destinations", monero_utils::to_rapidjson_val(allocator, m_destinations), allocator);

  // return root
  return root;
}

// --------------------------- MONERO QUERY KEY PARAMS ---------------------------

rapidjson::Value monero_query_key_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_key_type != boost::none) monero_utils::add_json_member("key_type", m_key_type.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO QUERY OUTPUT PARAMS ---------------------------

rapidjson::Value monero_query_output_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_key_image != boost::none) monero_utils::add_json_member("key_image", m_key_image.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO GET ADDRESS PARAMS ---------------------------

rapidjson::Value monero_get_address_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);

  // set sub-arrays
  if (!m_subaddress_indices.empty()) root.AddMember("address_index", monero_utils::to_rapidjson_val(allocator, m_subaddress_indices), allocator);

  // return root
  return root;
}

// --------------------------- MONERO INTEGRATED ADDRESS PARAMS ---------------------------

rapidjson::Value monero_integrated_address_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_standard_address != boost::none) monero_utils::add_json_member("standard_address", m_standard_address.get(), allocator, root, value_str);
  if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);
  if (m_integrated_address != boost::none) monero_utils::add_json_member("integrated_address", m_integrated_address.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO MULTISIG PARAMS ---------------------------

rapidjson::Value monero_multisig_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, value_str);
  if (m_multisig_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_multisig_tx_hex.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value val_num(rapidjson::kNumberType);
  if (m_threshold != boost::none) monero_utils::add_json_member("threshold", m_threshold.get(), allocator, root, val_num);

  // set bool values
  if (m_enable_multisig_experimental != boost::none) monero_utils::add_json_member("enable_multisig_experimental", m_enable_multisig_experimental.get(), allocator, root);

  // set sub-arrays
  if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
  if (!m_multisig_hexes.empty()) root.AddMember("info", monero_utils::to_rapidjson_val(allocator, m_multisig_hexes), allocator);

  // return root
  return root;
}

// --------------------------- MONERO CLOSE WALLET PARAMS ---------------------------

rapidjson::Value monero_close_wallet_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set bool values
  if (m_save != boost::none) monero_utils::add_json_member("autosave_current", m_save.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO CHANGE WALLET PASSWORD PARAMS ---------------------------

rapidjson::Value monero_change_wallet_password_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_old_password != boost::none) monero_utils::add_json_member("old_password", m_old_password.get(), allocator, root, value_str);
  if (m_new_password != boost::none) monero_utils::add_json_member("new_password", m_new_password.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO SET DAEMON PARAMS ---------------------------

rapidjson::Value monero_set_daemon_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_username != boost::none) monero_utils::add_json_member("username", m_username.get(), allocator, root, value_str);
  if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, value_str);
  if (m_ssl_support != boost::none) monero_utils::add_json_member("ssl_support", m_ssl_support.get(), allocator, root, value_str);
  if (m_ssl_options != boost::none && m_ssl_options->m_ssl_private_key_path != boost::none) monero_utils::add_json_member("ssl_private_key_path", m_ssl_options->m_ssl_private_key_path.get(), allocator, root, value_str);
  if (m_ssl_options != boost::none && m_ssl_options->m_ssl_certificate_path != boost::none) monero_utils::add_json_member("ssl_certificate_path", m_ssl_options->m_ssl_certificate_path.get(), allocator, root, value_str);
  if (m_ssl_options != boost::none && m_ssl_options->m_ssl_ca_file != boost::none) monero_utils::add_json_member("ssl_ca_file", m_ssl_options->m_ssl_ca_file.get(), allocator, root, value_str);

  // set bool values
  if (m_trusted != boost::none) monero_utils::add_json_member("trusted", m_trusted.get(), allocator, root);
  if (m_ssl_options != boost::none && m_ssl_options->m_ssl_allow_any_cert != boost::none) monero_utils::add_json_member("ssl_allow_any_cert", m_ssl_options->m_ssl_allow_any_cert.get(), allocator, root);

  // set sub-arrays
  if (m_ssl_options != boost::none && !m_ssl_options->m_ssl_allowed_fingerprints.empty()) root.AddMember("ssl_allowed_fingerprints", monero_utils::to_rapidjson_val(allocator, m_ssl_options->m_ssl_allowed_fingerprints), allocator);

  // return root
  return root;
}

// --------------------------- MONERO TAG ACCOUNT PARAMS ---------------------------

rapidjson::Value monero_account_tag_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);

  // set sub-arrays
  if (!m_account_indices.empty()) root.AddMember("accounts", monero_utils::to_rapidjson_val(allocator, m_account_indices), allocator);

  // return root
  return root;
}

// --------------------------- MONERO TX NOTES PARAMS ---------------------------

rapidjson::Value monero_tx_notes_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set sub-arrays
  if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  if (!m_notes.empty()) root.AddMember("notes", monero_utils::to_rapidjson_val(allocator, m_notes), allocator);

  // return root
  return root;
}

// --------------------------- MONERO ADDRESS BOOK ENTRY PARAMS ---------------------------

rapidjson::Value monero_address_book_entry_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_description != boost::none) monero_utils::add_json_member("description", m_description.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_index != boost::none) monero_utils::add_json_member("index", m_index.get(), allocator, root, value_num);

  // set bool values
  if (m_set_address != boost::none) monero_utils::add_json_member("set_address", m_set_address.get(), allocator, root);
  if (m_set_description != boost::none) monero_utils::add_json_member("set_description", m_set_description.get(), allocator, root);

  // set sub-arrays
  if (!m_entries.empty()) root.AddMember("entries", monero_utils::to_rapidjson_val(allocator, m_entries), allocator);

  // return root
  return root;
}

// --------------------------- MONERO VERIFY SIGN MESSAGE PARAMS ---------------------------

rapidjson::Value monero_verify_sign_message_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_data != boost::none) monero_utils::add_json_member("data", m_data.get(), allocator, root, value_str);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);
  if (m_signature_type != boost::none) {
    if (m_signature_type == monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY) {
      monero_utils::add_json_member("signature_type", std::string("view"), allocator, root, value_str);
    }
    else {
      monero_utils::add_json_member("signature_type", std::string("spend"), allocator, root, value_str);
    }
  }

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
  if (m_address_index != boost::none) monero_utils::add_json_member("address_index", m_address_index.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO CHECK TX KEY PARAMS ---------------------------

rapidjson::Value monero_check_tx_key_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tx_hash != boost::none) monero_utils::add_json_member("txid", m_tx_hash.get(), allocator, root, value_str);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_tx_key != boost::none) monero_utils::add_json_member("tx_key", m_tx_key.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO SIGN DESCRIBE TRANSFER PARAMS ---------------------------

rapidjson::Value monero_sign_describe_transfer_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_unsigned_txset != boost::none) monero_utils::add_json_member("unsigned_txset", m_unsigned_txset.get(), allocator, root, value_str);
  if (m_multisig_txset != boost::none) monero_utils::add_json_member("multisig_txset", m_multisig_txset.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO WALLET RELAY TX PARAMS ---------------------------

rapidjson::Value monero_wallet_relay_tx_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_hex != boost::none) monero_utils::add_json_member("hex", m_hex.get(), allocator, root, value_str);
  if (m_signed_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_signed_tx_hex.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO CREATE EDIT SUBADDRESS PARAMS ---------------------------

rapidjson::Value monero_create_edit_subaddress_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value val_num(rapidjson::kNumberType);
  if (m_account_index != boost::none && m_subaddress_index != boost::none) {
    rapidjson::Value index(rapidjson::kObjectType);
    monero_utils::add_json_member("major", m_account_index.get(), allocator, index, val_num);
    monero_utils::add_json_member("minor", m_subaddress_index.get(), allocator, index, val_num);
    root.AddMember("index", index, allocator);
  }
  else if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, val_num);

  // return root
  return root;
}

// --------------------------- MONERO CREATE OPEN WALLET PARAMS ---------------------------

rapidjson::Value monero_create_open_wallet_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_view_key != boost::none && !m_view_key->empty()) monero_utils::add_json_member("viewkey", m_view_key.get(), allocator, root, value_str);
  if (m_spend_key != boost::none && !m_spend_key->empty()) monero_utils::add_json_member("spendkey", m_spend_key.get(), allocator, root, value_str);
  if (m_filename != boost::none) monero_utils::add_json_member("filename", m_filename.get(), allocator, root, value_str);
  if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, value_str);
  if (m_language != boost::none) monero_utils::add_json_member("language", m_language.get(), allocator, root, value_str);
  if (m_seed != boost::none) monero_utils::add_json_member("seed", m_seed.get(), allocator, root, value_str);
  if (m_seed_offset != boost::none) monero_utils::add_json_member("seed_offset", m_seed_offset.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value val_num(rapidjson::kNumberType);
  if (m_restore_height != boost::none) monero_utils::add_json_member("restore_height", m_restore_height.get(), allocator, root, val_num);

  // set bool values
  if (m_autosave_current != boost::none) monero_utils::add_json_member("autosave_current", m_autosave_current.get(), allocator, root);
  if (m_enable_multisig_experimental != boost::none) monero_utils::add_json_member("enable_multisig_experimental", m_enable_multisig_experimental.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO RESERVE PROOF PARAMS ---------------------------

rapidjson::Value monero_reserve_proof_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_message != boost::none) monero_utils::add_json_member("message", m_message.get(), allocator, root, value_str);
  if (m_tx_hash != boost::none) monero_utils::add_json_member("txid", m_tx_hash.get(), allocator, root, value_str);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
  if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);

  // set bool values
  if (m_all != boost::none) monero_utils::add_json_member("all", m_all.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO REFRESH WALLET PARAMS ---------------------------

rapidjson::Value monero_wallet_refresh_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_period != boost::none) monero_utils::add_json_member("period", m_period.get(), allocator, root, value_num);
  if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);

  // set bool values
  if (m_enable != boost::none) monero_utils::add_json_member("enable", m_enable.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO GET INCOMING TRANSFERS PARAMS ---------------------------

rapidjson::Value monero_get_incoming_transfers_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_transfer_type != boost::none) monero_utils::add_json_member("transfer_type", m_transfer_type.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);

  // set bool values
  if (m_verbose != boost::none) monero_utils::add_json_member("verbose", m_verbose.get(), allocator, root);

  // set sub-arrays
  if (!m_subaddr_indices.empty()) root.AddMember("subaddr_indices", monero_utils::to_rapidjson_val(allocator, m_subaddr_indices), allocator);

  // return root
  return root;
}

// --------------------------- MONERO GET TRANSFERS PARAMS ---------------------------

rapidjson::Value monero_get_transfers_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_min_height != boost::none) monero_utils::add_json_member("min_height", m_min_height.get(), allocator, root, value_num);
  if (m_max_height != boost::none) monero_utils::add_json_member("max_height", m_max_height.get(), allocator, root, value_num);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);

  // set bool values
  monero_utils::add_json_member("filter_by_height", m_min_height != boost::none || m_max_height != boost::none, allocator, root);
  if (m_in != boost::none) monero_utils::add_json_member("in", m_in.get(), allocator, root);
  if (m_out != boost::none) monero_utils::add_json_member("out", m_out.get(), allocator, root);
  if (m_pool != boost::none) monero_utils::add_json_member("pool", m_pool.get(), allocator, root);
  if (m_pending != boost::none) monero_utils::add_json_member("pending", m_pending.get(), allocator, root);
  if (m_failed != boost::none) monero_utils::add_json_member("failed", m_failed.get(), allocator, root);
  if (m_all_accounts != boost::none) monero_utils::add_json_member("all_accounts", m_all_accounts.get(), allocator, root);

  // set sub-arrays
  if (!m_subaddr_indices.empty()) root.AddMember("subaddr_indices", monero_utils::to_rapidjson_val(allocator, m_subaddr_indices), allocator);

  // return root
  return root;
}

// --------------------------- MONERO GET HEIGHT RESPONSE ---------------------------

uint64_t monero_wallet_get_height_response::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) return it->second.get_value<uint64_t>();
  }
  throw std::runtime_error("Invalid get_height response");
}

// --------------------------- MONERO MULTISIG RESPONSE ---------------------------

void monero_multisig_response::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_multisig_response>& response) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("n_outputs")) response->m_num_outputs = it->second.get_value<int>();
    else if (key == std::string("info") || key == std::string("multisig_info") && !it->second.data().empty()) response->m_multisig_info = it->second.data();
    else if (key == std::string("tx_hash_list")) {
      const auto& tx_hash_list_node = it->second;
      std::vector<std::string> hashes;
      for (auto it2 = tx_hash_list_node.begin(); it2 != tx_hash_list_node.end(); ++it2) {
        response->m_tx_hashes.push_back(it2->second.data());
      }
    }
  }
}

// --------------------------- MONERO GET BALANCE RESPONSE ---------------------------

void monero_get_balance_response::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_balance_response>& response) {
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
        auto sub = std::make_shared<monero::monero_subaddress>();
        PyMoneroSubaddress::from_rpc_property_tree(it2->second, sub);
        response->m_per_subaddress.push_back(sub);
      }
    }
  }
}
