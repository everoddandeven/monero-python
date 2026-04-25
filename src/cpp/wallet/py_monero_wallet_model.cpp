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
#include "py_monero_wallet_model.h"
#include "utils/monero_utils.h"

// ------------------------------ Custom Data Model ---------------------------------

PyMoneroKeyImage::PyMoneroKeyImage(const monero::monero_key_image &key_image) {
  m_hex = key_image.m_hex;
  m_signature = key_image.m_signature;
}

rapidjson::Value PyMoneroKeyImage::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_hex != boost::none) monero_utils::add_json_member("key_image", m_hex.get(), allocator, root, value_str);
  if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);

  // return root
  return root;
}

bool PyMoneroOutputQuery::is_contextual(const monero::monero_output_query &query) {
  if (query.m_tx_query == boost::none) return false;
  if (query.m_tx_query.get()->m_is_incoming != boost::none) return true;       // requires context of all transfers
  if (query.m_tx_query.get()->m_is_outgoing != boost::none) return true;
  if (query.m_tx_query.get()->m_transfer_query != boost::none) return true; // requires context of transfers
  return false;
}

bool PyMoneroTransferQuery::is_contextual(const monero::monero_transfer_query &query) {
  if (query.m_tx_query == boost::none) return false;
  // requires context of all transfers
  if (query.m_tx_query.get()->m_is_incoming != boost::none) return true;
  if (query.m_tx_query.get()->m_is_outgoing != boost::none) return true;
  // requires context of inputs
  if (query.m_tx_query.get()->m_input_query != boost::none) return true;
  // requires context of inputs
  if (query.m_tx_query.get()->m_output_query != boost::none) return true;
  return false;
}

std::shared_ptr<monero_tx_query> PyMoneroTxQuery::decontextualize(const std::shared_ptr<monero::monero_tx_query> &query) {
  query->m_is_incoming = boost::none;
  query->m_is_outgoing = boost::none;
  query->m_transfer_query = boost::none;
  query->m_input_query = boost::none;
  query->m_output_query = boost::none;
  return query;
}

bool PyMoneroTxWallet::decode_rpc_type(const std::string &rpc_type, const std::shared_ptr<monero::monero_tx_wallet> &tx) {
  bool is_outgoing = false;
  if (rpc_type == std::string("in")) {
    tx->m_is_confirmed = true;
    tx->m_in_tx_pool = false;
    tx->m_is_relayed = true;
    tx->m_relay = true;
    tx->m_is_failed = false;
    tx->m_is_miner_tx = false;
  } else if (rpc_type == std::string("out")) {
    is_outgoing = true;
    tx->m_is_confirmed = true;
    tx->m_in_tx_pool = false;
    tx->m_is_relayed = true;
    tx->m_relay = true;
    tx->m_is_failed = false;
    tx->m_is_miner_tx = false;
  } else if (rpc_type == std::string("pool")) {
    tx->m_is_confirmed = false;
    tx->m_in_tx_pool = true;
    tx->m_is_relayed = true;
    tx->m_relay = true;
    tx->m_is_failed = false;
    tx->m_is_miner_tx = false;  // TODO: but could it be?
  } else if (rpc_type == std::string("pending")) {
    is_outgoing = true;
    tx->m_is_confirmed = false;
    tx->m_in_tx_pool = true;
    tx->m_is_relayed = true;
    tx->m_relay = true;
    tx->m_is_failed = false;
    tx->m_is_miner_tx = false;
  } else if (rpc_type == std::string("block")) {
    tx->m_is_confirmed = true;
    tx->m_in_tx_pool = false;
    tx->m_is_relayed = true;
    tx->m_relay = true;
    tx->m_is_failed = false;
    tx->m_is_miner_tx = true;
  } else if (rpc_type == std::string("failed")) {
    is_outgoing = true;
    tx->m_is_confirmed = false;
    tx->m_in_tx_pool = false;
    tx->m_is_relayed = false;
    tx->m_relay = true;
    tx->m_is_failed = true;
    tx->m_is_miner_tx = false;
  } else {
    throw std::runtime_error(std::string("Unrecognized transfer type: ") + rpc_type);
  }
  return is_outgoing;
}

void PyMoneroTxWallet::init_sent(const monero::monero_tx_config &config, std::shared_ptr<monero::monero_tx_wallet> &tx, bool copy_destinations) {
  bool relay = bool_equals_2(true, config.m_relay);
  tx->m_is_outgoing = true;
  tx->m_is_confirmed = false;
  tx->m_num_confirmations = 0;
  tx->m_in_tx_pool = relay;
  tx->m_relay = relay;
  tx->m_is_relayed = relay;
  tx->m_is_miner_tx = false;
  tx->m_is_failed = false;
  tx->m_is_locked = true;
  tx->m_ring_size = monero_utils::RING_SIZE;

  auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
  outgoing_transfer->m_tx = tx;

  if (config.m_subaddress_indices.size() == 1) {
    // we know src subaddress indices iff request specifies 1
    outgoing_transfer->m_subaddress_indices = config.m_subaddress_indices;
  }

  if (copy_destinations) {
    auto conf_dests = config.get_normalized_destinations();
    for(const auto &conf_dest : conf_dests) {
      auto dest = std::make_shared<monero::monero_destination>();
      conf_dest->copy(conf_dest, dest);
      outgoing_transfer->m_destinations.push_back(dest);
    }
  }

  tx->m_outgoing_transfer = outgoing_transfer;
  tx->m_payment_id = config.m_payment_id;
  if (tx->m_unlock_time == boost::none) tx->m_unlock_time = 0;
  if (bool_equals_2(true, tx->m_relay)) {
    if (tx->m_last_relayed_timestamp == boost::none) {
      // set last relayed timestamp to current time iff relayed
      // TODO (monero-wallet-rpc): provide timestamp on response; unconfirmed timestamps vary
      tx->m_last_relayed_timestamp = static_cast<uint64_t>(time(NULL));
    }
    if (tx->m_is_double_spend_seen == boost::none) tx->m_is_double_spend_seen = false;
  }
}

void PyMoneroTxWallet::from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing, const monero_tx_config &config) {
  std::shared_ptr<monero::monero_block> header = nullptr;
  std::shared_ptr<monero::monero_outgoing_transfer> outgoing_transfer = nullptr;
  std::shared_ptr<monero::monero_incoming_transfer> incoming_transfer = nullptr;

  bool key_found = false;

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("type")) {
      is_outgoing = decode_rpc_type(it->second.data(), tx);
      key_found = true;
    }
  }

  for (auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("txid") || key == std::string("tx_hash")) tx->m_hash = it->second.data();
    else if (key == std::string("fee")) tx->m_fee = it->second.get_value<uint64_t>();
    else if (key == std::string("note") && !it->second.data().empty()) tx->m_note = it->second.data();
    else if (key == std::string("tx_key") && !it->second.data().empty()) tx->m_key = it->second.data();
    else if (key == std::string("tx_size")) tx->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("unlock_time")) tx->m_unlock_time = it->second.get_value<uint64_t>();
    else if (key == std::string("weight")) tx->m_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("locked")) tx->m_is_locked = it->second.get_value<bool>();
    else if (key == std::string("tx_blob") && !it->second.data().empty()) tx->m_full_hex = it->second.data();
    else if (key == std::string("tx_metadata") && !it->second.data().empty()) tx->m_metadata = it->second.data();
    else if (key == std::string("double_spend_seen")) tx->m_is_double_spend_seen = it->second.get_value<bool>();
    else if (key == std::string("block_height") || key == std::string("height")) {
      if (bool_equals_2(true, tx->m_is_confirmed)) {
        if (header == nullptr) header = std::make_shared<monero::monero_block>();
        header->m_height = it->second.get_value<uint64_t>();
      }
    }
    else if (key == std::string("timestamp")) {
      if (bool_equals_2(true, tx->m_is_confirmed)) {
        if (header == nullptr) header = std::make_shared<monero::monero_block>();
        header->m_timestamp = it->second.get_value<uint64_t>();
      }
    }
    else if (key == std::string("confirmations")) tx->m_num_confirmations = it->second.get_value<uint64_t>();
    else if (key == std::string("suggested_confirmations_threshold")) {
      if (*is_outgoing) {
        if (outgoing_transfer == nullptr)
          outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
        outgoing_transfer->m_tx = tx;
      }
      else {
        if (incoming_transfer == nullptr)
          incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
        incoming_transfer->m_tx = tx;
        incoming_transfer->m_num_suggested_confirmations = it->second.get_value<uint64_t>();
      }
    }
    else if (key == std::string("amount")) {
      if (*is_outgoing) {
        if (outgoing_transfer == nullptr) {
          outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          outgoing_transfer->m_tx = tx;
        }
        outgoing_transfer->m_amount = it->second.get_value<uint64_t>();
      }
      else {
        if (incoming_transfer == nullptr) incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
        incoming_transfer->m_tx = tx;
        incoming_transfer->m_amount = it->second.get_value<uint64_t>();
      }
    }
    else if (key == std::string("address")) {
      if (!*is_outgoing) {
        if (incoming_transfer == nullptr) incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
        incoming_transfer->m_tx = tx;
        incoming_transfer->m_address = it->second.data();
      }
    }
    else if (key == std::string("payment_id")) {
      std::string payment_id = it->second.data();
      if (payment_id != std::string("") && payment_id != monero::monero_tx_wallet::DEFAULT_PAYMENT_ID) {
        tx->m_payment_id = payment_id;
      }
    }
    else if (key == std::string("subaddr_indices")) {
      if (*is_outgoing) {
        if (outgoing_transfer == nullptr) {
          outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          outgoing_transfer->m_tx = tx;
        }
      }
      else {
        if (incoming_transfer == nullptr) incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
        incoming_transfer->m_tx = tx;
      }

      auto node2 = it->second;
      bool first_major = true;
      bool first_minor = true;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;

        for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
          std::string index_key = it3->first;

          if (index_key == std::string("major") && first_major) {
            if (*is_outgoing) outgoing_transfer->m_account_index = it3->second.get_value<uint32_t>();
            else incoming_transfer->m_account_index = it3->second.get_value<uint32_t>();
            first_major = false;
          }
          else if (index_key == std::string("minor")) {
            if (*is_outgoing) {
              outgoing_transfer->m_subaddress_indices.push_back(it3->second.get_value<uint32_t>());
            }
            else if (first_minor) {
              incoming_transfer->m_subaddress_index = it3->second.get_value<uint32_t>();
              first_minor = false;
            }
          }
        }
      }
    }
    else if (key == std::string("destinations") || key == std::string("recipients")) {
      if (!*is_outgoing) throw std::runtime_error("Expected outgoing transaction");
      if (outgoing_transfer == nullptr) {
        outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
        outgoing_transfer->m_tx = tx;
      }
      auto node2 = it->second;
      outgoing_transfer->m_destinations.clear();

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;
        auto dest = std::make_shared<monero::monero_destination>();

        for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
          std::string _key = it3->first;

          if (_key == std::string("address")) dest->m_address = it3->second.data();
          else if (_key == std::string("amount")) dest->m_amount = it3->second.get_value<uint64_t>();
          else throw std::runtime_error(std::string("Unrecognized transaction destination field: ") + _key);
        }

        outgoing_transfer->m_destinations.push_back(dest);
      }
    }
    else if (key == std::string("amount_in")) tx->m_input_sum = it->second.get_value<uint64_t>();
    else if (key == std::string("amount_out")) tx->m_output_sum = it->second.get_value<uint64_t>();
    else if (key == std::string("change_address") && !it->second.data().empty()) tx->m_change_address = it->second.data();
    else if (key == std::string("change_amount")) tx->m_change_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("dummy_outputs")) tx->m_num_dummy_outputs = it->second.get_value<uint64_t>();
    else if (key == std::string("extra")) tx->m_extra_hex = it->second.data();
    else if (key == std::string("ring_size")) tx->m_ring_size = it->second.get_value<uint32_t>();
    else if (key == std::string("spent_key_images")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        std::string _key = it2->first;

        if (_key == std::string("key_images")) {
          auto node3 = it2->second;
          if (tx->m_inputs.size() > 0) throw std::runtime_error("inputs should be empty");

          for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
            auto output = std::make_shared<monero::monero_output_wallet>();
            auto key_image = std::make_shared<monero::monero_key_image>();

            key_image->m_hex = it3->second.data();
            output->m_key_image = key_image;
            output->m_tx = tx;
            tx->m_inputs.push_back(output);
          }
        }
      }
    }
    else if (key == std::string("amounts_by_dest")) {
      if (!*is_outgoing) throw std::runtime_error("Expected outgoing transaction");
      if (outgoing_transfer == nullptr) {
        outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
        outgoing_transfer->m_tx = tx;
      }
      auto node2 = it->second;
      std::vector<uint64_t> amounts_by_dest;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        std::string _key = it2->first;

        if (_key == std::string("amounts")) {
          auto node3 = it2->second;

          for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
            amounts_by_dest.push_back(it3->second.get_value<uint64_t>());
          }
        }
      }

      auto destinations = config.get_normalized_destinations();
      size_t num_destinations = destinations.size();
      if (num_destinations != amounts_by_dest.size()) throw std::runtime_error("Expected destinations size equal to amounts by dest size");
      outgoing_transfer->m_destinations.clear();
      for(uint64_t i = 0; i < num_destinations; i++) {
        auto dest = std::make_shared<monero::monero_destination>();
        dest->m_address = destinations[i]->m_address;
        dest->m_amount = amounts_by_dest[i];
        outgoing_transfer->m_destinations.push_back(dest);
      }
    }
  }

  if (!key_found && is_outgoing == boost::none) throw std::runtime_error("Must indicate if tx is outgoing (true) xor incoming (false) since unknown");
  // link block and tx
  if (header != nullptr) {
    auto block = std::make_shared<monero::monero_block>();
    header->copy(header, block);
    block->m_txs.push_back(tx);
    tx->m_block = block;
  }

  if (*is_outgoing && outgoing_transfer != nullptr) {
    if (tx->m_is_confirmed == boost::none) tx->m_is_confirmed = false;
    if (bool_equals_2(false, outgoing_transfer->m_tx->m_is_confirmed)) tx->m_num_confirmations = 0;
    tx->m_is_outgoing = true;

    if (tx->m_outgoing_transfer != boost::none) {
      // overwrite to avoid reconcile error TODO: remove after >18.3.1 when amounts_by_dest supported
      if (!outgoing_transfer->m_destinations.empty()) {
        tx->m_outgoing_transfer.get()->m_destinations.clear();
      }
      tx->m_outgoing_transfer.get()->merge(tx->m_outgoing_transfer.get(), outgoing_transfer);
    }
    else tx->m_outgoing_transfer = outgoing_transfer;
  }
  else if (is_outgoing != boost::none && *is_outgoing == false && incoming_transfer != nullptr) {
    if (tx->m_is_confirmed == boost::none) tx->m_is_confirmed = false;
    if (bool_equals_2(false, incoming_transfer->m_tx->m_is_confirmed)) tx->m_num_confirmations = 0;
    tx->m_is_incoming = true;
    tx->m_incoming_transfers.push_back(incoming_transfer);
  }

}

void PyMoneroTxWallet::from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing) {
  monero::monero_tx_config config;
  from_property_tree_with_transfer(node, tx, is_outgoing, config);
}

void PyMoneroTxWallet::from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx) {
  boost::optional<bool> is_outgoing;
  from_property_tree_with_transfer(node, tx, is_outgoing);
}

void PyMoneroTxWallet::from_property_tree_with_output(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx) {
  tx->m_is_confirmed = true;
  tx->m_is_relayed = true;
  tx->m_is_failed = false;
  tx->m_in_tx_pool = false;

  auto output = std::make_shared<monero::monero_output_wallet>();
  output->m_tx = tx;

  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("amount")) output->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("spent")) output->m_is_spent = it->second.get_value<bool>();
    else if (key == std::string("key_image") && !it->second.data().empty()) {
      auto key_image = std::make_shared<monero::monero_key_image>();
      key_image->m_hex = it->second.data();
      output->m_key_image = key_image;
    }
    else if (key == std::string("global_index")) output->m_index = it->second.get_value<uint64_t>();
    else if (key == std::string("tx_hash")) tx->m_hash = it->second.data();
    else if (key == std::string("unlocked")) tx->m_is_locked = !it->second.get_value<bool>();
    else if (key == std::string("frozen")) output->m_is_frozen = it->second.get_value<bool>();
    else if (key == std::string("pubkey")) output->m_stealth_public_key = it->second.data();
    else if (key == std::string("subaddr_index")) {
      for(auto indices_it = it->second.begin(); indices_it != it->second.end(); ++indices_it) {
        std::string indices_key = indices_it->first;
        if (indices_key == std::string("major")) output->m_account_index = indices_it->second.get_value<uint32_t>();
        if (indices_key == std::string("minor")) output->m_subaddress_index = indices_it->second.get_value<uint32_t>();
      }
    }
    else if (key == std::string("block_height")) {
      auto block = std::make_shared<monero::monero_block>();
      block->m_height = it->second.get_value<uint64_t>();
      block->m_txs.push_back(tx);
      tx->m_block = block;
    }
  }

  tx->m_outputs.push_back(output);
}

void PyMoneroTxWallet::from_property_tree_with_output_and_merge(const boost::property_tree::ptree& node, std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>& tx_map, std::unordered_map<uint64_t, std::shared_ptr<monero_block>>& block_map) {
  for(auto it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("transfers")) {
      for(auto rpc_output_it = it->second.begin(); rpc_output_it != it->second.end(); ++rpc_output_it) {
        auto tx = std::make_shared<monero::monero_tx_wallet>();
        from_property_tree_with_output(rpc_output_it->second, tx);
        merge_tx(tx, tx_map, block_map);
      }
    }
  }
}

void PyMoneroTxWallet::from_property_tree_with_transfer_and_merge(const boost::property_tree::ptree& node, std::unordered_map<std::string, std::shared_ptr<monero::monero_tx_wallet>>& tx_map, std::unordered_map<uint64_t, std::shared_ptr<monero::monero_block>>& block_map) {
  for (auto it = node.begin(); it != node.end(); ++it) {
    for (auto it2 = it->second.begin(); it2 != it->second.end(); ++it2) {
      auto tx = std::make_shared<monero::monero_tx_wallet>();
      PyMoneroTxWallet::from_property_tree_with_transfer(it2->second, tx);

      if (tx->m_is_confirmed != boost::none && *tx->m_is_confirmed == true) {
        if (tx->m_block == boost::none) throw std::runtime_error("Confirmed tx has no block");
        auto& block_txs = tx->m_block.get()->m_txs;
        if (std::find(block_txs.begin(), block_txs.end(), tx) == block_txs.end()) {
          throw std::runtime_error("Tx not found in its block");
        }
      }

      // replace transfer amount with destination sum
      // TODO monero-wallet-rpc: confirmed tx from/to same account has amount 0 but cached transfers
      if (tx->m_outgoing_transfer != boost::none && bool_equals_2(true, tx->m_is_relayed) && !bool_equals_2(true, tx->m_is_failed) &&
          !tx->m_outgoing_transfer.get()->m_destinations.empty() && tx->m_outgoing_transfer.get()->m_amount.get() == 0) {
        auto outgoing_transfer = tx->m_outgoing_transfer.get();
        uint64_t transfer_total = 0;
        for(const auto& destination : outgoing_transfer->m_destinations) {
          transfer_total += destination->m_amount.get();
        }
        outgoing_transfer->m_amount = transfer_total;
      }

      // merge tx
      merge_tx(tx, tx_map, block_map);
    }
  }
}

/**
  * Merges a transaction into a unique set of transactions.
  *
  * @param tx is the transaction to merge into the existing txs
  * @param tx_map maps tx hashes to txs
  * @param block_map maps block heights to blocks
  */
void PyMoneroTxWallet::merge_tx(const std::shared_ptr<monero_tx_wallet>& tx, std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>& tx_map, std::unordered_map<uint64_t, std::shared_ptr<monero_block>>& block_map) {
  if (tx->m_hash == boost::none) throw std::runtime_error("Tx hash is not initialized");

  // merge tx
  std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>>::const_iterator tx_iter = tx_map.find(*tx->m_hash);
  if (tx_iter == tx_map.end()) {
    tx_map[*tx->m_hash] = tx; // cache new tx
  } else {
    std::shared_ptr<monero_tx_wallet>& a_tx = tx_map[*tx->m_hash];
    a_tx->merge(a_tx, tx); // merge with existing tx
  }

  // merge tx's block if confirmed
  if (tx->get_height() != boost::none) {
    std::unordered_map<uint64_t, std::shared_ptr<monero_block>>::const_iterator block_iter = block_map.find(tx->get_height().get());
    if (block_iter == block_map.end()) {
      block_map[tx->get_height().get()] = tx->m_block.get(); // cache new block
    } else {
      std::shared_ptr<monero_block>& a_block = block_map[tx->get_height().get()];
      a_block->merge(a_block, tx->m_block.get()); // merge with existing block
    }
  }
}

void PyMoneroTxSet::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("multisig_txset") && !it->second.data().empty()) set->m_multisig_tx_hex = it->second.data();
    else if (key == std::string("unsigned_txset") && !it->second.data().empty()) set->m_unsigned_tx_hex = it->second.data();
    else if (key == std::string("signed_txset") && !it->second.data().empty()) set->m_signed_tx_hex = it->second.data();
  }
}

void PyMoneroTxSet::from_tx(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, const std::shared_ptr<monero::monero_tx_wallet> &tx, bool is_outgoing, const monero_tx_config &config) {
  from_property_tree(node, set);
  boost::optional<bool> outgoing = is_outgoing;
  PyMoneroTxWallet::from_property_tree_with_transfer(node, tx, outgoing, config);
  tx->m_tx_set = set;
  set->m_txs.push_back(tx);
}

void PyMoneroTxSet::from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
  std::vector<std::shared_ptr<monero::monero_tx_wallet>> txs;
  from_sent_txs(node, set, txs, boost::none);
}

void PyMoneroTxSet::from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, std::vector<std::shared_ptr<monero::monero_tx_wallet>> &txs, const boost::optional<monero_tx_config> &conf) {
  from_property_tree(node, set);
  int num_txs = 0;
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("fee_list") && num_txs == 0) {
      auto fee_list_node = it->second;
      for (auto it2 = fee_list_node.begin(); it2 != fee_list_node.end(); ++it2) {
        num_txs++;
      }
    }
    else if (key == std::string("tx_hash_list") && num_txs == 0) {
      auto tx_hash_list_node = it->second;
      for (auto it2 = tx_hash_list_node.begin(); it2 != tx_hash_list_node.end(); ++it2) {
        num_txs++;
      }
    }
  }

  if (num_txs == 0) {
    if (txs.size() > 0) throw std::runtime_error("txs should be empty");
    return;
  }

  if (txs.size() > 0) set->m_txs = txs;
  else {
    for(int i = 0; i < num_txs; i++) {
      auto tx = std::make_shared<monero::monero_tx_wallet>();
      txs.push_back(tx);
    }
  }

  for(const auto &tx : txs) {
    tx->m_tx_set = set;
    tx->m_is_outgoing = true;
  }

  set->m_txs = txs;

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("tx_hash_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_hash = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("tx_key_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_key = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("tx_blob_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_full_hex = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("tx_metadata_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_metadata = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("fee_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_fee = it2->second.get_value<uint64_t>();
        i++;
      }
    }
    else if (key == std::string("amount_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        if (tx->m_outgoing_transfer == boost::none) {
          auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          outgoing_transfer->m_tx = tx;
          tx->m_outgoing_transfer = outgoing_transfer;
        }
        tx->m_outgoing_transfer.get()->m_amount = it2->second.get_value<uint64_t>();
        i++;
      }
    }
    else if (key == std::string("weight_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_weight = it2->second.get_value<uint64_t>();
        i++;
      }
    }
    else if (key == std::string("spent_key_images_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        if (tx->m_inputs.size() > 0) throw std::runtime_error("Expected no inputs in sent tx");

        auto node3 = it2->second;
        for (auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
          std::string _key = it3->first;

          if (_key == std::string("key_images")) {
            auto node4 = it3->second;

            for (auto it4 = node4.begin(); it4 != node4.end(); ++it4) {
              auto output = std::make_shared<monero::monero_output_wallet>();
              output->m_key_image = std::make_shared<monero::monero_key_image>();
              output->m_key_image.get()->m_hex = it4->second.data();
              output->m_tx = tx;
              tx->m_inputs.push_back(output);
            }
          }
        }

        i++;
      }
    }
    else if (key == std::string("amounts_by_dest_list")) {
      auto node2 = it->second;
      int i = 0;
      int destination_idx = 0;

      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        auto node3 = it2->second;
        for (auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
          std::string _key = it3->first;

          if (_key == std::string("amounts")) {
            std::vector<uint64_t> amounts_by_dest;
            auto node4 = it3->second;

            for(auto it4 = node4.begin(); it4 != node4.end(); ++it4) {
              amounts_by_dest.push_back(it4->second.get_value<uint64_t>());
            }

            if (tx->m_outgoing_transfer == boost::none) {
              auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
              outgoing_transfer->m_tx = tx;
              tx->m_outgoing_transfer = outgoing_transfer;
            }

            tx->m_outgoing_transfer.get()->m_destinations.clear();

            for(const auto& amount : amounts_by_dest) {
              if (conf == boost::none) throw std::runtime_error("Expected tx configuration");
              auto config = conf.get();
              if (config.m_destinations.size() == 1) {
                // sweeping can create multiple withone address
                auto dest = std::make_shared<monero::monero_destination>();
                dest->m_address = config.m_destinations[0]->m_address;
                dest->m_amount = amount;
                tx->m_outgoing_transfer.get()->m_destinations.push_back(dest);
              }
              else {
                auto dest = std::make_shared<monero::monero_destination>();
                dest->m_address = config.get_normalized_destinations()[destination_idx]->m_address;
                dest->m_amount = amount;
                tx->m_outgoing_transfer.get()->m_destinations.push_back(dest);
                destination_idx++;
              }
            }
          }
        }

        i++;
      }
    }
  }
}

void PyMoneroTxSet::from_describe_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("desc")) {
      auto node2 = it->second;

      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = std::make_shared<monero::monero_tx_wallet>();
        boost::optional<bool> outgoing = true;
        PyMoneroTxWallet::from_property_tree_with_transfer(it2->second, tx, outgoing);
        tx->m_tx_set = set;
        set->m_txs.push_back(tx);
      }
    }
  }
}

void PyMoneroKeyImage::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image>& key_image) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("key_image")) key_image->m_hex = it->second.data();
    else if (key == std::string("signature")) key_image->m_signature = it->second.data();
  }
}

void PyMoneroKeyImage::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_key_image>>& key_images) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("signed_key_images")) {
      auto key_images_node = it->second;

      for (auto it2 = key_images_node.begin(); it2 != key_images_node.end(); ++it2) {
        auto key_image = std::make_shared<monero::monero_key_image>();
        from_property_tree(it2->second, key_image);
        key_images.push_back(key_image);
      }
    }
  }
}

void PyMoneroKeyImageImportResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image_import_result>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) result->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("spent")) result->m_spent_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("unspent")) result->m_unspent_amount = it->second.get_value<uint64_t>();
  }
}

void PyMoneroMultisigInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_info>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("multisig")) info->m_is_multisig = it->second.get_value<bool>();
    else if (key == std::string("ready")) info->m_is_ready = it->second.get_value<bool>();
    else if (key == std::string("threshold")) info->m_threshold = it->second.get_value<uint32_t>();
    else if (key == std::string("total")) info->m_num_participants = it->second.get_value<uint32_t>();
  }
}

void PyMoneroMultisigInitResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_init_result>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("address")) info->m_address = it->second.data();
    else if (key == std::string("multisig_info")) info->m_multisig_hex = it->second.data();
  }
}

void PyMoneroMultisigSignResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_sign_result>& res) {
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

void PyMoneroSubaddress::from_rpc_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("account_index")) subaddress->m_account_index = it->second.get_value<uint32_t>();
    else if (key == std::string("address_index")) subaddress->m_index = it->second.get_value<uint32_t>();
    else if (key == std::string("address")) subaddress->m_address = it->second.data();
    else if (key == std::string("balance")) subaddress->m_balance = it->second.get_value<uint64_t>();
    else if (key == std::string("unlocked_balance")) subaddress->m_unlocked_balance = it->second.get_value<uint64_t>();
    else if (key == std::string("label") && !it->second.data().empty()) subaddress->m_label = it->second.data();
    else if (key == std::string("used")) subaddress->m_is_used = it->second.get_value<bool>();
    else if (key == std::string("num_unspent_outputs")) subaddress->m_num_unspent_outputs = it->second.get_value<uint64_t>();
    else if (key == std::string("blocks_to_unlock")) subaddress->m_num_blocks_to_unlock = it->second.get_value<uint64_t>();
  }
}

void PyMoneroSubaddress::from_rpc_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_subaddress>>& subaddresses) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    bool rpc_subaddresses = key == std::string("addresses");

    if (key == std::string("per_subaddress") || rpc_subaddresses) {
      auto per_subaddress_node = it->second;

      for (auto it2 = per_subaddress_node.begin(); it2 != per_subaddress_node.end(); ++it2) {
        auto sub = std::make_shared<monero::monero_subaddress>();
        if (rpc_subaddresses) from_rpc_property_tree(it2->second, sub);
        else from_property_tree(it2->second, sub);
        subaddresses.push_back(sub);
      }
    }
  }
}

void PyMoneroSubaddress::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
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

void PyMoneroIntegratedAddress::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_integrated_address>& subaddress) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("integrated_address")) subaddress->m_integrated_address = it->second.data();
    else if (key == std::string("standard_address")) subaddress->m_standard_address = it->second.data();
    else if (key == std::string("payment_id")) subaddress->m_payment_id = it->second.data();
  }
}

void PyMoneroAccount::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_account>& account) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("account_index")) account->m_index = it->second.get_value<uint32_t>();
    else if (key == std::string("balance")) account->m_balance = it->second.get_value<uint64_t>();
    else if (key == std::string("unlocked_balance")) account->m_unlocked_balance = it->second.get_value<uint64_t>();
    else if (key == std::string("base_address")) account->m_primary_address = it->second.data();
    else if (key == std::string("tag")) account->m_tag = it->second.data();
    else if (key == std::string("label")) {
      // label belongs to first subaddress
    }
  }
  if (account->m_tag != boost::none && account->m_tag->empty()) account->m_tag = boost::none;
}

void PyMoneroAccount::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_account>>& accounts) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("subaddress_accounts")) {
      auto accounts_node = it->second;

      for (auto it2 = accounts_node.begin(); it2 != accounts_node.end(); ++it2) {
        auto account = std::make_shared<monero::monero_account>();
        from_property_tree(it2->second, account);
        accounts.push_back(account);
      }
    }
  }
}

void PyMoneroAccount::from_property_tree(const boost::property_tree::ptree& node, std::vector<monero::monero_account>& accounts) {
  std::vector<std::shared_ptr<monero::monero_account>> accounts_ptr;
  from_property_tree(node, accounts_ptr);

  for (const auto &account : accounts_ptr) {
    accounts.push_back(*account);
  }
}

void PyMoneroAddressBookEntry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_address_book_entry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("index")) entry->m_index = it->second.get_value<uint64_t>();
    else if (key == std::string("address")) entry->m_address = it->second.data();
    else if (key == std::string("description")) entry->m_description = it->second.data();
    else if (key == std::string("payment_id")) entry->m_payment_id = it->second.data();
  }
}

void PyMoneroAddressBookEntry::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_address_book_entry>>& entries) {
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

void PyMoneroCheckReserve::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_reserve>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("good")) check->m_is_good = it->second.get_value<bool>();
    else if (key == std::string("total")) check->m_total_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("spent")) check->m_unconfirmed_spent_amount = it->second.get_value<uint64_t>();
  }

  if (!bool_equals_2(true, check->m_is_good)) {
    // normalize invalid check reserve
    check->m_total_amount = boost::none;
    check->m_unconfirmed_spent_amount = boost::none;
  }
}

void PyMoneroCheckTxProof::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_tx>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("good")) check->m_is_good = it->second.get_value<bool>();
    if (key == std::string("in_pool")) check->m_in_tx_pool = it->second.get_value<bool>();
    else if (key == std::string("confirmations")) check->m_num_confirmations = it->second.get_value<uint64_t>();
    else if (key == std::string("received")) check->m_received_amount = it->second.get_value<uint64_t>();
  }

  if (!bool_equals_2(true, check->m_is_good)) {
    // normalize invalid tx proof
    check->m_in_tx_pool = boost::none;
    check->m_num_confirmations = boost::none;
    check->m_received_amount = boost::none;
  }
}

void PyMoneroMessageSignatureResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_message_signature_result> result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("good")) result->m_is_good = it->second.get_value<bool>();
    else if (key == std::string("old")) result->m_is_old = it->second.get_value<bool>();
    else if (key == std::string("signature_type")) {
      std::string sig_type = it->second.data();
      if (sig_type == std::string("view")) {
        result->m_signature_type = monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY;
      }
      else {
        result->m_signature_type = monero::monero_message_signature_type::SIGN_WITH_SPEND_KEY;
      }
    }
    else if (key == std::string("version")) result->m_version = it->second.get_value<uint32_t>();
  }
}

// ------------------------------ Extended Data Model ---------------------------------

bool monero_tx_height_comparator::operator()(const std::shared_ptr<monero::monero_tx>& tx1, const std::shared_ptr<monero::monero_tx>& tx2) const {
  auto h1 = tx1->get_height();
  auto h2 = tx2->get_height();

  if (h1 == boost::none && h2 == boost::none) {
    // both unconfirmed
    return false;
  }
  else if (h1 == boost::none) {
    // tx1 is unconfirmed
    return false;
  }
  else if (h2 == boost::none) {
    // tx2 is unconfirmed
    return true;
  }

  if (*h1 != *h2) {
    return *h1 < *h2;
  }

  // txs are in the same block so retain their original order
  const auto& txs = tx1->m_block.get()->m_txs;
  auto it1 = std::find(txs.begin(), txs.end(), tx1);
  auto it2 = std::find(txs.begin(), txs.end(), tx2);

  return std::distance(txs.begin(), it1) < std::distance(txs.begin(), it2);
}

bool monero_incoming_transfer_comparator::operator()(const std::shared_ptr<monero::monero_incoming_transfer>& t1, const std::shared_ptr<monero::monero_incoming_transfer>& t2) const {
  return (*this)(*t1, *t2);
}

bool monero_incoming_transfer_comparator::operator()(const monero::monero_incoming_transfer& t1, const monero::monero_incoming_transfer& t2) const {
  monero_tx_height_comparator tx_comp;

  // compare by height
  if (tx_comp(t1.m_tx, t2.m_tx)) return true;
  if (tx_comp(t2.m_tx, t1.m_tx)) return false;

  // compare by account and subaddress index
  if (t1.m_account_index.value() != t2.m_account_index.value()) {
    return t1.m_account_index.value() < t2.m_account_index.value();
  }

  return t1.m_subaddress_index.value() < t2.m_subaddress_index.value();
}

bool monero_output_comparator::operator()(const monero::monero_output_wallet& o1, const monero::monero_output_wallet& o2) const {
  monero_tx_height_comparator tx_comp;

  if (tx_comp(o1.m_tx, o2.m_tx)) return true;
  if (tx_comp(o2.m_tx, o1.m_tx)) return false;

  if (o1.m_account_index.value() != o2.m_account_index.value()) {
    return o1.m_account_index.value() < o2.m_account_index.value();
  }

  if (o1.m_subaddress_index.value() != o2.m_subaddress_index.value()) {
    return o1.m_subaddress_index.value() < o2.m_subaddress_index.value();
  }

  if (o1.m_index.value() != o2.m_index.value()) {
    return o1.m_index.value() < o2.m_index.value();
  }

  return o1.m_key_image.get()->m_hex.value() < o2.m_key_image.get()->m_hex.value();
}

// --------------------------- MONERO DECODED ADDRESS ---------------------------

monero_decoded_address::monero_decoded_address(const std::string& address, monero_address_type address_type, monero::monero_network_type network_type):
  m_address(address),
  m_address_type(address_type),
  m_network_type(network_type) {
}

rapidjson::Value monero_decoded_address::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  monero_utils::add_json_member("address", m_address, allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  monero_utils::add_json_member("addressType", (uint8_t)m_address_type, allocator, root, value_num);
  monero_utils::add_json_member("networkType", (uint8_t)m_network_type, allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO ACCOUNT TAG ---------------------------

void monero_account_tag::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_account_tag>& account_tag) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("tag")) account_tag->m_tag = it->second.data();
    else if (key == std::string("label") && !it->second.data().empty()) account_tag->m_label = it->second.data();
  }
}

void monero_account_tag::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_account_tag>>& account_tags) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("account_tags")) {
      auto account_tags_node = it->second;

      for (auto it2 = account_tags_node.begin(); it2 != account_tags_node.end(); ++it2) {
        auto account_tag = std::make_shared<monero_account_tag>();
        from_property_tree(it2->second, account_tag);
        account_tags.push_back(account_tag);
      }
    }
  }
}

rapidjson::Value monero_account_tag::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);
  if (!m_account_indices.empty()) root.AddMember("accountIndices", monero_utils::to_rapidjson_val(allocator, m_account_indices), allocator);

  // return root
  return root;
}

/**
 * ---------------- DUPLICATED MONERO-CPP WALLET FULL CODE ---------------------
 */

bool bool_equals_2(bool val, const boost::optional<bool>& opt_val) {
  return opt_val == boost::none ? false : val == *opt_val;
}

/**
  * Returns true iff tx1's height is known to be less than tx2's height for sorting.
  */
bool tx_height_less_than(const std::shared_ptr<monero_tx>& tx1, const std::shared_ptr<monero_tx>& tx2) {
  if (tx1->m_block != boost::none && tx2->m_block != boost::none) return tx1->get_height() < tx2->get_height();
  else if (tx1->m_block == boost::none) return false;
  else return true;
}

/**
  * Returns true iff transfer1 is ordered before transfer2 by ascending account and subaddress indices.
  */
bool incoming_transfer_before(const std::shared_ptr<monero_incoming_transfer>& transfer1, const std::shared_ptr<monero_incoming_transfer>& transfer2) {

  // compare by height
  if (tx_height_less_than(transfer1->m_tx, transfer2->m_tx)) return true;

  // compare by account and subaddress index
  if (transfer1->m_account_index.get() < transfer2->m_account_index.get()) return true;
  else if (transfer1->m_account_index.get() == transfer2->m_account_index.get()) return transfer1->m_subaddress_index.get() < transfer2->m_subaddress_index.get();
  else return false;
}

/**
  * Returns true iff wallet vout1 is ordered before vout2 by ascending account and subaddress indices then index.
  */
bool vout_before(const std::shared_ptr<monero_output>& o1, const std::shared_ptr<monero_output>& o2) {
  if (o1 == o2) return false; // ignore equal references
  std::shared_ptr<monero_output_wallet> ow1 = std::static_pointer_cast<monero_output_wallet>(o1);
  std::shared_ptr<monero_output_wallet> ow2 = std::static_pointer_cast<monero_output_wallet>(o2);

  // compare by height
  if (tx_height_less_than(ow1->m_tx, ow2->m_tx)) return true;

  // compare by account index, subaddress index, output index, then key image hex
  if (ow1->m_account_index.get() < ow2->m_account_index.get()) return true;
  if (ow1->m_account_index.get() == ow2->m_account_index.get()) {
    if (ow1->m_subaddress_index.get() < ow2->m_subaddress_index.get()) return true;
    if (ow1->m_subaddress_index.get() == ow2->m_subaddress_index.get()) {
      if (ow1->m_index.get() < ow2->m_index.get()) return true;
      if (ow1->m_index.get() == ow2->m_index.get()) throw std::runtime_error("Should never sort outputs with duplicate indices");
    }
  }
  return false;
}
