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
#include "py_monero_daemon_model.h"
#include "utils/monero_utils.h"

// --------------------------- Custom Data Model ---------------------------

// Move to monero::monero_utils
rapidjson::Value to_rapidjson_vector_int_val(rapidjson::Document::AllocatorType& allocator, const std::vector<int>& nums) {
  rapidjson::Value value_arr(rapidjson::kArrayType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  for (const auto& num : nums) {
    value_num.SetInt(num);
    value_arr.PushBack(value_num, allocator);
  }
  return value_arr;
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
  // used by get_blocks_by_height
  const auto& rpc_blocks = node.get_child("blocks");
  const auto& rpc_txs = node.get_child("txs");
  if (rpc_blocks.size() != rpc_txs.size()) {
    throw std::runtime_error("blocks and txs size mismatch");
  }

  auto it_block = rpc_blocks.begin();
  auto it_txs = rpc_txs.begin();
  size_t idx = 0;

  for (; it_block != rpc_blocks.end(); ++it_block, ++it_txs, ++idx) {
    // build block
    auto block = std::make_shared<monero::monero_block>();
    PyMoneroBlock::from_property_tree(it_block->second, block);
    block->m_height = heights.at(idx);
    blocks.push_back(block);

    // build transactions
    std::vector<std::shared_ptr<monero::monero_tx>> txs;
    size_t tx_idx = 0;
    for (const auto& tx_node : it_txs->second) {
      auto tx = std::make_shared<monero::monero_tx>();
      tx->m_hash = block->m_tx_hashes.at(tx_idx++);
      tx->m_is_confirmed = true;
      tx->m_in_tx_pool = false;
      tx->m_is_miner_tx = false;
      tx->m_relay = true;
      tx->m_is_relayed = true;
      tx->m_is_failed = false;
      tx->m_is_double_spend_seen = false;
      PyMoneroTx::from_property_tree(tx_node.second, tx);
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
          auto offsets_node = it2->second;

          for (auto it3 = offsets_node.begin(); it3 != offsets_node.end(); ++it3) {
            output->m_ring_output_indices.push_back(it3->second.get_value<uint64_t>());
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
  std::shared_ptr<monero_block> block = tx->m_block == boost::none ? nullptr : tx->m_block.get();
  std::string as_json;
  std::string tx_json;

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
    else if (key == std::string("vin")) {
      auto &rpc_inputs = it->second;
      bool is_miner_input = false;

      if (rpc_inputs.size() == 1) {
        auto first = rpc_inputs.begin()->second;
        if (first.get_child_optional("gen")) {
          is_miner_input = true;
        }
      }
      // ignore miner input
      // TODO why?
      if (!is_miner_input) {
        std::vector<std::shared_ptr<monero::monero_output>> inputs;
        for (auto &vin_entry : rpc_inputs) {
          auto output = std::make_shared<monero::monero_output>();
          PyMoneroOutput::from_property_tree(vin_entry.second, output);
          output->m_tx = tx;
          inputs.push_back(output);
        }

        tx->m_inputs = inputs;
      }
    }
    else if (key == std::string("vout")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto output = std::make_shared<monero::monero_output>();
        PyMoneroOutput::from_property_tree(it2->second, output);
        output->m_tx = tx;
        tx->m_outputs.push_back(output);
      }
    }
    else if (key == std::string("rct_signatures")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        std::string _key = it2->first;

        if (_key == std::string("txnFee")) {
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
    else if (key == std::string("as_json")) as_json = it->second.data();
    else if (key == std::string("tx_json")) tx_json = it->second.data();
    else if ((key == std::string("as_hex") || key == std::string("tx_blob")) && !it->second.data().empty()) tx->m_full_hex = it->second.data();
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
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        tx->m_signatures.push_back(it2->second.data());
      }
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
    else if (key == std::string("max_used_block_id_hash") && !it->second.data().empty()) tx->m_max_used_block_hash = it->second.data();
    else if (key == std::string("prunable_hash") && !it->second.data().empty()) tx->m_prunable_hash = it->second.data();
    else if (key == std::string("prunable_as_hex") && !it->second.data().empty()) tx->m_prunable_hex = it->second.data();
    else if (key == std::string("pruned_as_hex") && !it->second.data().empty()) tx->m_pruned_hex = it->second.data();
  }

  bool is_confirmed = tx->m_is_confirmed != boost::none && tx->m_is_confirmed.get();

  if (block != nullptr && is_confirmed) {
    block->m_txs.push_back(tx);
    tx->m_block = block;
  }

  // initialize remaining known fields
  if (is_confirmed) {
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

  if (!as_json.empty()) {
    auto n = PyGenUtils::parse_json_string(as_json);
    PyMoneroTx::from_property_tree(n, tx);
  }
  if (!tx_json.empty()) {
    auto n = PyGenUtils::parse_json_string(tx_json);
    PyMoneroTx::from_property_tree(n, tx);
  }

  if (tx->m_is_relayed != boost::none && !tx->m_is_relayed.get()) tx->m_last_relayed_timestamp = boost::none;
}

void PyMoneroTx::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_tx>>& txs) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    bool pool_txs = key == std::string("transactions");

    if (pool_txs || key == std::string("txs")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;
        auto tx = std::make_shared<monero::monero_tx>();
        tx->m_is_miner_tx = false;
        if (pool_txs) {
          tx->m_is_confirmed = false;
          tx->m_in_tx_pool = true;
          tx->m_num_confirmations = 0;
        }
        from_property_tree(node3, tx);
        txs.push_back(tx);
      }
    }
  }
}

void PyMoneroTx::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& tx_hashes) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("tx_hashes")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        tx_hashes.push_back(it2->second.data());
      }
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

// --------------------------- MONERO RPC PAYMENT INFO ---------------------------

void monero_rpc_payment_info::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_rpc_payment_info>& rpc_payment_info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if ((key == std::string("top_hash") || key == std::string("top_block_hash")) && !it->second.data().empty()) rpc_payment_info->m_top_block_hash = it->second.data();
    else if (key == std::string("credits")) rpc_payment_info->m_credits = it->second.get_value<uint64_t>();
  }
}

rapidjson::Value monero_rpc_payment_info::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_top_block_hash != boost::none) monero_utils::add_json_member("topBlockHash", m_top_block_hash.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_credits != boost::none) monero_utils::add_json_member("credits", m_credits.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO ALT CHAIN ---------------------------

void monero_alt_chain::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_alt_chain>& alt_chain) {
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

rapidjson::Value monero_alt_chain::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_main_chain_parent_block_hash != boost::none) monero_utils::add_json_member("mainChainParentBlockHash", m_main_chain_parent_block_hash.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_difficulty != boost::none) monero_utils::add_json_member("difficulty", m_difficulty.get(), allocator, root, value_num);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_length != boost::none) monero_utils::add_json_member("length", m_length.get(), allocator, root, value_num);

  // set sub-arrays
  if (!m_block_hashes.empty()) root.AddMember("blockHashes", monero_utils::to_rapidjson_val(allocator, m_block_hashes), allocator);

  // return root
  return root;
}

// --------------------------- MONERO BAN ---------------------------

void monero_ban::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_ban>& ban) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("host")) ban->m_host = it->second.data();
    else if (key == std::string("ip")) ban->m_ip = it->second.get_value<int>();
    else if (key == std::string("ban")) ban->m_is_banned = it->second.get_value<bool>();
    else if (key == std::string("seconds")) ban->m_seconds = it->second.get_value<uint64_t>();
  }
}

void monero_ban::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_ban>>& bans) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("bans")) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto ban = std::make_shared<monero_ban>();
        monero_ban::from_property_tree(it2->second, ban);
        bans.push_back(ban);
      }
    }
  }
}

rapidjson::Value monero_ban::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_host != boost::none) monero_utils::add_json_member("host", m_host.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_ip != boost::none) monero_utils::add_json_member("ip", m_ip.get(), allocator, root, value_num);
  if (m_seconds != boost::none) monero_utils::add_json_member("seconds", m_seconds.get(), allocator, root, value_num);

  // set bool values
  if (m_is_banned != boost::none) monero_utils::add_json_member("ban", m_is_banned.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO PRUNE RESULT ---------------------------

void monero_prune_result::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_prune_result>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("pruned")) result->m_is_pruned = it->second.get_value<bool>();
    else if (key == std::string("pruning_seed")) result->m_pruning_seed = it->second.get_value<int>();
  }
}

rapidjson::Value monero_prune_result::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_pruning_seed != boost::none) monero_utils::add_json_member("pruningSeed", m_pruning_seed.get(), allocator, root, value_num);

  // set bool values
  if (m_is_pruned != boost::none) monero_utils::add_json_member("isPruned", m_is_pruned.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO MINING STATUS ---------------------------

void monero_mining_status::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_mining_status>& status) {
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

rapidjson::Value monero_mining_status::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_speed != boost::none) monero_utils::add_json_member("speed", m_speed.get(), allocator, root, value_num);
  if (m_num_threads != boost::none) monero_utils::add_json_member("numThreads", m_num_threads.get(), allocator, root, value_num);

  // set bool values
  if (m_is_active != boost::none) monero_utils::add_json_member("isActive", m_is_active.get(), allocator, root);
  if (m_is_background != boost::none) monero_utils::add_json_member("isBackground", m_is_background.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO MINER TX SUM ---------------------------

void monero_miner_tx_sum::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_miner_tx_sum>& sum) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("emission_amount")) sum->m_emission_sum = it->second.get_value<uint64_t>();
    else if (key == std::string("fee_amount")) sum->m_fee_sum = it->second.get_value<uint64_t>();
  }
}

rapidjson::Value monero_miner_tx_sum::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_emission_sum != boost::none) monero_utils::add_json_member("emissionSum", m_emission_sum.get(), allocator, root, value_num);
  if (m_fee_sum != boost::none) monero_utils::add_json_member("feeSum", m_fee_sum.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO BLOCK TEMPLATE ---------------------------

void monero_block_template::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_block_template>& tmplt) {
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

rapidjson::Value monero_block_template::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_block_template_blob != boost::none) monero_utils::add_json_member("blockTemplateBlob", m_block_template_blob.get(), allocator, root, value_str);
  if (m_block_hashing_blob != boost::none) monero_utils::add_json_member("blockHashingBlob", m_block_hashing_blob.get(), allocator, root, value_str);
  if (m_prev_hash != boost::none) monero_utils::add_json_member("prevHash", m_prev_hash.get(), allocator, root, value_str);
  if (m_seed_hash != boost::none) monero_utils::add_json_member("seedHash", m_seed_hash.get(), allocator, root, value_str);
  if (m_next_seed_hash != boost::none) monero_utils::add_json_member("nextSeedHash", m_next_seed_hash.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_difficulty != boost::none) monero_utils::add_json_member("difficulty", m_difficulty.get(), allocator, root, value_num);
  if (m_expected_reward != boost::none) monero_utils::add_json_member("expectedReward", m_expected_reward.get(), allocator, root, value_num);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_reserved_offset != boost::none) monero_utils::add_json_member("reservedOffset", m_reserved_offset.get(), allocator, root, value_num);
  if (m_seed_height != boost::none) monero_utils::add_json_member("seedHeight", m_seed_height.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO CONNECTION SPAN ---------------------------

void monero_connection_span::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_connection_span>& span) {
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

rapidjson::Value monero_connection_span::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_connection_id != boost::none) monero_utils::add_json_member("connectionId", m_connection_id.get(), allocator, root, value_str);
  if (m_remote_address != boost::none) monero_utils::add_json_member("remoteAddress", m_remote_address.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_num_blocks != boost::none) monero_utils::add_json_member("numBlocks", m_num_blocks.get(), allocator, root, value_num);
  if (m_rate != boost::none) monero_utils::add_json_member("rate", m_rate.get(), allocator, root, value_num);
  if (m_speed != boost::none) monero_utils::add_json_member("speed", m_speed.get(), allocator, root, value_num);
  if (m_size != boost::none) monero_utils::add_json_member("size", m_size.get(), allocator, root, value_num);
  if (m_start_height != boost::none) monero_utils::add_json_member("startHeight", m_start_height.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO PEER ---------------------------

void monero_peer::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_peer>& peer) {
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
        peer->m_connection_type = monero_connection_type::INVALID;
      }
      else if (rpc_type == 1) {
        peer->m_connection_type = monero_connection_type::IPV4;
      }
      else if (rpc_type == 2) {
        peer->m_connection_type = monero_connection_type::IPV6;
      }
      else if (rpc_type == 3) {
        peer->m_connection_type = monero_connection_type::TOR;
      }
      else if (rpc_type == 4) {
        peer->m_connection_type = monero_connection_type::I2P;
      }
      else throw std::runtime_error("Invalid RPC peer type, expected 0-4: " + std::to_string(rpc_type));
    }
  }
}

void monero_peer::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_peer>>& peers) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    bool is_online = key == std::string("white_list");
    if (key == std::string("connections") || is_online || key == std::string("gray_list") ) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto peer = std::make_shared<monero_peer>();
        monero_peer::from_property_tree(it2->second, peer);
        peer->m_is_online = is_online;
        peers.push_back(peer);
      }
    }
  }
}

rapidjson::Value monero_peer::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_host != boost::none) monero_utils::add_json_member("host", m_host.get(), allocator, root, value_str);
  if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
  if (m_state != boost::none) monero_utils::add_json_member("state", m_state.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_port != boost::none) monero_utils::add_json_member("port", m_port.get(), allocator, root, value_num);
  if (m_rpc_port != boost::none) monero_utils::add_json_member("rpcPort", m_rpc_port.get(), allocator, root, value_num);
  if (m_last_seen_timestamp != boost::none) monero_utils::add_json_member("lastSeenTimestamp", m_last_seen_timestamp.get(), allocator, root, value_num);
  if (m_pruning_seed != boost::none) monero_utils::add_json_member("pruningSeed", m_pruning_seed.get(), allocator, root, value_num);
  if (m_rpc_credits_per_hash != boost::none) monero_utils::add_json_member("rpcCreditsPerHash", m_rpc_credits_per_hash.get(), allocator, root, value_num);
  if (m_avg_download != boost::none) monero_utils::add_json_member("avgDownload", m_avg_download.get(), allocator, root, value_num);
  if (m_avg_upload != boost::none) monero_utils::add_json_member("avgUpload", m_avg_upload.get(), allocator, root, value_num);
  if (m_current_download != boost::none) monero_utils::add_json_member("currentDownload", m_current_download.get(), allocator, root, value_num);
  if (m_current_upload != boost::none) monero_utils::add_json_member("currentUpload", m_current_upload.get(), allocator, root, value_num);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_live_time != boost::none) monero_utils::add_json_member("liveTime", m_live_time.get(), allocator, root, value_num);
  if (m_num_receives != boost::none) monero_utils::add_json_member("numReceives", m_num_receives.get(), allocator, root, value_num);
  if (m_num_sends != boost::none) monero_utils::add_json_member("numSends", m_num_sends.get(), allocator, root, value_num);
  if (m_receive_idle_time != boost::none) monero_utils::add_json_member("receiveIdleTime", m_receive_idle_time.get(), allocator, root, value_num);
  if (m_send_idle_time != boost::none) monero_utils::add_json_member("sendIdleTime", m_send_idle_time.get(), allocator, root, value_num);
  if (m_num_support_flags != boost::none) monero_utils::add_json_member("numSupportFlags", m_num_support_flags.get(), allocator, root, value_num);

  // set bool values
  if (m_is_online != boost::none) monero_utils::add_json_member("isOnline", m_is_online.get(), allocator, root);
  if (m_is_incoming != boost::none) monero_utils::add_json_member("isIncoming", m_is_incoming.get(), allocator, root);
  if (m_is_local_ip != boost::none) monero_utils::add_json_member("isLocalIp", m_is_local_ip.get(), allocator, root);
  if (m_is_local_host != boost::none) monero_utils::add_json_member("isLocalHost", m_is_local_host.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO SUBMIT TX RESULT ---------------------------

void monero_submit_tx_result::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_submit_tx_result>& result) {
  monero_rpc_payment_info::from_property_tree(node, result);

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
    else if (key == std::string("reason") && !it->second.data().empty()) result->m_reason = it->second.data();
    else if (key == std::string("too_big")) result->m_is_too_big = it->second.get_value<bool>();
    else if (key == std::string("sanity_check_failed")) result->m_sanity_check_failed = it->second.get_value<bool>();
    else if (key == std::string("tx_extra_too_big")) result->m_is_tx_extra_too_big = it->second.get_value<bool>();
    else if (key == std::string("nonzero_unlock_time")) result->m_is_nonzero_unlock_time = it->second.get_value<bool>();
  }
}

rapidjson::Value monero_submit_tx_result::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root = monero_rpc_payment_info::to_rapidjson_val(allocator);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_reason != boost::none) monero_utils::add_json_member("reason", m_reason.get(), allocator, root, value_str);

  // set bool values
  if (m_has_invalid_input != boost::none) monero_utils::add_json_member("hasInvalidInput", m_has_invalid_input.get(), allocator, root);
  if (m_has_invalid_output != boost::none) monero_utils::add_json_member("hasInvalidOutput", m_has_invalid_output.get(), allocator, root);
  if (m_has_too_few_outputs != boost::none) monero_utils::add_json_member("hasTooFewOutputs", m_has_too_few_outputs.get(), allocator, root);
  if (m_is_good != boost::none) monero_utils::add_json_member("isGood", m_is_good.get(), allocator, root);
  if (m_is_relayed != boost::none) monero_utils::add_json_member("isRelayed", m_is_relayed.get(), allocator, root);
  if (m_is_double_spend != boost::none) monero_utils::add_json_member("isDoubleSpend", m_is_double_spend.get(), allocator, root);
  if (m_is_fee_too_low != boost::none) monero_utils::add_json_member("isFeeTooLow", m_is_fee_too_low.get(), allocator, root);
  if (m_is_mixin_too_low != boost::none) monero_utils::add_json_member("isMixinTooLow", m_is_mixin_too_low.get(), allocator, root);
  if (m_is_overspend != boost::none) monero_utils::add_json_member("isOverspend", m_is_overspend.get(), allocator, root);
  if (m_is_too_big != boost::none) monero_utils::add_json_member("isTooBig", m_is_too_big.get(), allocator, root);
  if (m_is_tx_extra_too_big != boost::none) monero_utils::add_json_member("isTxExtraTooBig", m_is_tx_extra_too_big.get(), allocator, root);
  if (m_is_nonzero_unlock_time != boost::none) monero_utils::add_json_member("isNonZeroUnlockTime", m_is_nonzero_unlock_time.get(), allocator, root);
  if (m_sanity_check_failed != boost::none) monero_utils::add_json_member("sanityCheckFailed", m_sanity_check_failed.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO OUTPUT DISTRIBUTION ENTRY ---------------------------

void monero_output_distribution_entry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output_distribution_entry>& entry) {
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

void monero_output_distribution_entry::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_output_distribution_entry>>& entries) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("distributions")) {
      auto node2 = it->second;
      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto entry = std::make_shared<monero_output_distribution_entry>();
        from_property_tree(it2->second, entry);
        entries.push_back(entry);
      }
    }
  }
}

rapidjson::Value monero_output_distribution_entry::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);
  if (m_base != boost::none) monero_utils::add_json_member("base", m_base.get(), allocator, root, value_num);
  if (m_start_height != boost::none) monero_utils::add_json_member("startHeight", m_start_height.get(), allocator, root, value_num);

  // set sub-arrays
  if (!m_distribution.empty()) root.AddMember("distribution", to_rapidjson_vector_int_val(allocator, m_distribution), allocator);

  // return root
  return root;
}

// --------------------------- MONERO OUTPUT HISTOGRAM ENTRY ---------------------------

void monero_output_histogram_entry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output_histogram_entry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("amount")) entry->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("total_instances")) entry->m_num_instances = it->second.get_value<uint64_t>();
    else if (key == std::string("unlocked_instances")) entry->m_unlocked_instances = it->second.get_value<uint64_t>();
    else if (key == std::string("recent_instances")) entry->m_recent_instances = it->second.get_value<uint64_t>();
  }
}

void monero_output_histogram_entry::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_output_histogram_entry>>& entries) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("histogram")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto entry = std::make_shared<monero_output_histogram_entry>();
        from_property_tree(it2->second, entry);
        entries.push_back(entry);
      }
    }
  }
}

rapidjson::Value monero_output_histogram_entry::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);
  if (m_num_instances != boost::none) monero_utils::add_json_member("numInstances", m_num_instances.get(), allocator, root, value_num);
  if (m_unlocked_instances != boost::none) monero_utils::add_json_member("unlockedInstances", m_unlocked_instances.get(), allocator, root, value_num);
  if (m_recent_instances != boost::none) monero_utils::add_json_member("recentInstances", m_recent_instances.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO TX POOL STATS ---------------------------

void monero_tx_pool_stats::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_tx_pool_stats>& stats) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("pool_stats")) {
      monero_tx_pool_stats::from_property_tree(it->second, stats);
      break;
    }
    else if (key == std::string("txs_total")) stats->m_num_txs = it->second.get_value<int>();
    else if (key == std::string("num_not_relayed")) stats->m_num_not_relayed = it->second.get_value<int>();
    else if (key == std::string("num_failing")) stats->m_num_failing = it->second.get_value<int>();
    else if (key == std::string("num_double_spends")) stats->m_num_double_spends = it->second.get_value<int>();
    else if (key == std::string("num_10m")) stats->m_num10m = it->second.get_value<int>();
    else if (key == std::string("fee_total")) stats->m_fee_total = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_max")) stats->m_bytes_max = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_med")) stats->m_bytes_med = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_min")) stats->m_bytes_min = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_total")) stats->m_bytes_total = it->second.get_value<uint64_t>();
    else if (key == std::string("histo_98pc")) stats->m_histo98pc = it->second.get_value<uint64_t>();
    else if (key == std::string("oldest")) stats->m_oldest_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("histo")) {
      for(const auto& elem : it->second) {
        uint64_t bytes, txs = 0;
        for(boost::property_tree::ptree::const_iterator elem_it = elem.second.begin(); elem_it != elem.second.end(); ++elem_it) {
          std::string elem_key = elem_it->first;
          if (elem_key == "bytes") bytes = elem_it->second.get_value<uint64_t>();
          else if (elem_key == "txs") txs = elem_it->second.get_value<uint64_t>();
        }

        stats->m_histo[bytes] = txs;
      }
    }
  }

  // uninitialize some stats if not applicable
  if (stats->m_histo98pc != boost::none && stats->m_histo98pc.get() == 0) stats->m_histo98pc = boost::none;
  if (stats->m_num_txs != boost::none && stats->m_num_txs.get() == 0) {
    stats->m_bytes_min = boost::none;
    stats->m_bytes_max = boost::none;
    stats->m_bytes_med = boost::none;
    stats->m_histo98pc = boost::none;
    stats->m_oldest_timestamp = boost::none;
  }
}

rapidjson::Value monero_tx_pool_stats::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_num_txs != boost::none) monero_utils::add_json_member("numTxs", m_num_txs.get(), allocator, root, value_num);
  if (m_num_not_relayed != boost::none) monero_utils::add_json_member("numNotRelayed", m_num_not_relayed.get(), allocator, root, value_num);
  if (m_num_failing != boost::none) monero_utils::add_json_member("numFailing", m_num_failing.get(), allocator, root, value_num);
  if (m_num_double_spends != boost::none) monero_utils::add_json_member("numDoubleSpends", m_num_double_spends.get(), allocator, root, value_num);
  if (m_num10m != boost::none) monero_utils::add_json_member("num10m", m_num10m.get(), allocator, root, value_num);
  if (m_fee_total != boost::none) monero_utils::add_json_member("feeTotal", m_fee_total.get(), allocator, root, value_num);
  if (m_bytes_max != boost::none) monero_utils::add_json_member("bytesMax", m_bytes_max.get(), allocator, root, value_num);
  if (m_bytes_med != boost::none) monero_utils::add_json_member("bytesMed", m_bytes_med.get(), allocator, root, value_num);
  if (m_bytes_min != boost::none) monero_utils::add_json_member("bytesMin", m_bytes_min.get(), allocator, root, value_num);
  if (m_bytes_total != boost::none) monero_utils::add_json_member("bytesTotal", m_bytes_total.get(), allocator, root, value_num);
  if (m_histo98pc != boost::none) monero_utils::add_json_member("histo98pc", m_histo98pc.get(), allocator, root, value_num);
  if (m_oldest_timestamp != boost::none) monero_utils::add_json_member("oldestTimestamp", m_oldest_timestamp.get(), allocator, root, value_num);

  // set object values
  rapidjson::Value histo(rapidjson::kObjectType);
  for(const auto& kv : m_histo) {
    std::string key = std::to_string(kv.first);
    rapidjson::Value field_key(key.c_str(), key.size(), allocator);
    histo.AddMember(field_key, kv.second, allocator);
  }
  root.AddMember("histo", histo, allocator);

  // return root
  return root;
}

// --------------------------- MONERO DAEMON UPDATE CHECK RESULT ---------------------------

void monero_daemon_update_check_result::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_update_check_result>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("update")) check->m_is_update_available = it->second.get_value<bool>();
    else if (key == std::string("version") && !it->second.data().empty()) check->m_version = it->second.data();
    else if (key == std::string("hash") && !it->second.data().empty()) check->m_hash = it->second.data();
    else if (key == std::string("auto_uri") && !it->second.data().empty()) check->m_auto_uri = it->second.data();
    else if (key == std::string("user_uri") && !it->second.data().empty()) check->m_user_uri = it->second.data();
  }
}

rapidjson::Value monero_daemon_update_check_result::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
  if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
  if (m_auto_uri != boost::none) monero_utils::add_json_member("autoUri", m_auto_uri.get(), allocator, root, value_str);
  if (m_user_uri != boost::none) monero_utils::add_json_member("userUri", m_user_uri.get(), allocator, root, value_str);

  // set bool values
  if (m_is_update_available != boost::none) monero_utils::add_json_member("isUpdateAvailable", m_is_update_available.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO DAEMON UPDATE DOWNLOAD RESULT ---------------------------

void monero_daemon_update_download_result::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_update_download_result>& check) {
  monero_daemon_update_check_result::from_property_tree(node, check);

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("download_path") && !it->second.data().empty()) check->m_download_path = it->second.data();
  }
}

rapidjson::Value monero_daemon_update_download_result::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root = monero_daemon_update_check_result::to_rapidjson_val(allocator);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_download_path != boost::none) monero_utils::add_json_member("downloadPath", m_download_path.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO FEE ESTIMATE ---------------------------

void monero_fee_estimate::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_fee_estimate>& estimate) {
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

rapidjson::Value monero_fee_estimate::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_fee != boost::none) monero_utils::add_json_member("fee", m_fee.get(), allocator, root, value_num);
  if (m_quantization_mask != boost::none) monero_utils::add_json_member("quantizationMask", m_quantization_mask.get(), allocator, root, value_num);

  // set sub-arrays
  if (!m_fees.empty()) root.AddMember("fees", monero_utils::to_rapidjson_val(allocator, m_fees), allocator);

  // return root
  return root;
}

// --------------------------- MONERO DAEMON INFO ---------------------------

void monero_daemon_info::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_info>& info) {
  monero_rpc_payment_info::from_property_tree(node, info);

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
    else if (key == std::string("tx_count")) info->m_num_txs = it->second.get_value<int>();
    else if (key == std::string("tx_pool_size")) info->m_num_txs_pool = it->second.get_value<int>();
    else if (key == std::string("was_bootstrap_ever_used")) info->m_was_bootstrap_ever_used = it->second.get_value<bool>();
    else if (key == std::string("database_size")) info->m_database_size = it->second.get_value<uint64_t>();
    else if (key == std::string("update_available")) info->m_update_available = it->second.get_value<bool>();
    else if (key == std::string("busy_syncing")) info->m_is_busy_syncing = it->second.get_value<bool>();
    else if (key == std::string("synchronized")) info->m_is_synchronized = it->second.get_value<bool>();
    else if (key == std::string("restricted")) info->m_is_restricted = it->second.get_value<bool>();
  }
}

rapidjson::Value monero_daemon_info::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
  if (m_bootstrap_daemon_address != boost::none) monero_utils::add_json_member("bootstrapDaemonAddress", m_bootstrap_daemon_address.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_num_alt_blocks != boost::none) monero_utils::add_json_member("numAltBlocks", m_num_alt_blocks.get(), allocator, root, value_num);
  if (m_block_size_limit != boost::none) monero_utils::add_json_member("blockSizeLimit", m_block_size_limit.get(), allocator, root, value_num);
  if (m_block_size_median != boost::none) monero_utils::add_json_member("blockSizeMedian", m_block_size_median.get(), allocator, root, value_num);
  if (m_block_weight_limit != boost::none) monero_utils::add_json_member("blockWeightLimit", m_block_weight_limit.get(), allocator, root, value_num);
  if (m_block_weight_median != boost::none) monero_utils::add_json_member("blockWeightMedian", m_block_weight_median.get(), allocator, root, value_num);
  if (m_difficulty != boost::none) monero_utils::add_json_member("difficulty", m_difficulty.get(), allocator, root, value_num);
  if (m_cumulative_difficulty != boost::none) monero_utils::add_json_member("cumulativeDifficulty", m_cumulative_difficulty.get(), allocator, root, value_num);
  if (m_free_space != boost::none) monero_utils::add_json_member("freeSpace", m_free_space.get(), allocator, root, value_num);
  if (m_num_offline_peers != boost::none) monero_utils::add_json_member("numOfflinePeers", m_num_offline_peers.get(), allocator, root, value_num);
  if (m_num_online_peers != boost::none) monero_utils::add_json_member("numOnlinePeers", m_num_online_peers.get(), allocator, root, value_num);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_height_without_bootstrap != boost::none) monero_utils::add_json_member("heightWithoutBootstrap", m_height_without_bootstrap.get(), allocator, root, value_num);
  if (m_network_type != boost::none) monero_utils::add_json_member("networkType", (uint8_t)m_network_type.get(), allocator, root, value_num);
  if (m_num_incoming_connections != boost::none) monero_utils::add_json_member("numIncomingConnections", m_num_incoming_connections.get(), allocator, root, value_num);
  if (m_num_outgoing_connections != boost::none) monero_utils::add_json_member("numOutgoingConnections", m_num_outgoing_connections.get(), allocator, root, value_num);
  if (m_num_rpc_connections != boost::none) monero_utils::add_json_member("numRpcConnections", m_num_rpc_connections.get(), allocator, root, value_num);
  if (m_start_timestamp != boost::none) monero_utils::add_json_member("startTimestamp", m_start_timestamp.get(), allocator, root, value_num);
  if (m_adjusted_timestamp != boost::none) monero_utils::add_json_member("adjustedTimestamp", m_adjusted_timestamp.get(), allocator, root, value_num);
  if (m_target != boost::none) monero_utils::add_json_member("target", m_target.get(), allocator, root, value_num);
  if (m_target_height != boost::none) monero_utils::add_json_member("targetHeight", m_target_height.get(), allocator, root, value_num);
  if (m_num_txs != boost::none) monero_utils::add_json_member("numTxs", m_num_txs.get(), allocator, root, value_num);
  if (m_num_txs_pool != boost::none) monero_utils::add_json_member("numTxsPool", m_num_txs_pool.get(), allocator, root, value_num);
  if (m_database_size != boost::none) monero_utils::add_json_member("databaseSize", m_database_size.get(), allocator, root, value_num);

  // set bool values
  if (m_is_offline != boost::none) monero_utils::add_json_member("isOffline", m_is_offline.get(), allocator, root);
  if (m_was_bootstrap_ever_used != boost::none) monero_utils::add_json_member("wasBootstrapEverUsed", m_was_bootstrap_ever_used.get(), allocator, root);
  if (m_update_available != boost::none) monero_utils::add_json_member("updateAvailable", m_update_available.get(), allocator, root);
  if (m_is_busy_syncing != boost::none) monero_utils::add_json_member("isBusySyncing", m_is_busy_syncing.get(), allocator, root);
  if (m_is_synchronized != boost::none) monero_utils::add_json_member("isSynchronized", m_is_synchronized.get(), allocator, root);
  if (m_is_restricted != boost::none) monero_utils::add_json_member("isRestricted", m_is_restricted.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO DAEMON SYNC INFO ---------------------------

void monero_daemon_sync_info::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_sync_info>& info) {
  monero_rpc_payment_info::from_property_tree(node, info);

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
    else if (key == std::string("next_needed_pruning_seed")) info->m_next_needed_pruning_seed = it->second.get_value<int>();
    else if (key == std::string("overview") && !it->second.data().empty() && it->second.data() != std::string("[]")) info->m_overview = it->second.data();
  }
}

rapidjson::Value monero_daemon_sync_info::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_overview != boost::none) monero_utils::add_json_member("overview", m_overview.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_target_height != boost::none) monero_utils::add_json_member("targetHeight", m_target_height.get(), allocator, root, value_num);
  if (m_next_needed_pruning_seed != boost::none) monero_utils::add_json_member("nextNeededPruningSeed", m_next_needed_pruning_seed.get(), allocator, root, value_num);

  // set sub-arrays
  if (!m_peers.empty()) root.AddMember("peers", monero_utils::to_rapidjson_val(allocator, m_peers), allocator);
  if (!m_spans.empty()) root.AddMember("spans", monero_utils::to_rapidjson_val(allocator, m_spans), allocator);

  // return root
  return root;
}

// --------------------------- MONERO HARD FORK INFO ---------------------------

void monero_hard_fork_info::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_hard_fork_info>& info) {
  monero_rpc_payment_info::from_property_tree(node, info);

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
  }
}

rapidjson::Value monero_hard_fork_info::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_earliest_height != boost::none) monero_utils::add_json_member("earliestHeight", m_earliest_height.get(), allocator, root, value_num);
  if (m_state != boost::none) monero_utils::add_json_member("state", m_state.get(), allocator, root, value_num);
  if (m_threshold != boost::none) monero_utils::add_json_member("threshold", m_threshold.get(), allocator, root, value_num);
  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_num);
  if (m_num_votes != boost::none) monero_utils::add_json_member("numVotes", m_num_votes.get(), allocator, root, value_num);
  if (m_window != boost::none) monero_utils::add_json_member("window", m_window.get(), allocator, root, value_num);
  if (m_voting != boost::none) monero_utils::add_json_member("voting", m_voting.get(), allocator, root, value_num);

  // set bool values
  if (m_is_enabled != boost::none) monero_utils::add_json_member("isEnabled", m_is_enabled.get(), allocator, root);

  // return root
  return root;
}
