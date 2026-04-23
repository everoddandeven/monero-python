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
#include "py_monero_daemon_rpc_model.h"
#include "utils/monero_utils.h"

// --------------------------- MONERO DOWNLOAD UPDATE PARAMS ---------------------------

monero_download_update_params::monero_download_update_params(const std::string& command, const std::string& path): m_command(command) {
  if (!path.empty()) m_path = path;
}

rapidjson::Value monero_download_update_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
  if (m_path != boost::none) monero_utils::add_json_member("path", m_path.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- MONERO BANDWITH LIMITS PARAMS ---------------------------

void monero_bandwidth_limits::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_bandwidth_limits>& limits) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("limit_up")) limits->m_up = it->second.get_value<int>();
    else if (key == std::string("limit_down")) limits->m_down = it->second.get_value<int>();
  }
}

rapidjson::Value monero_bandwidth_limits::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_up != boost::none) monero_utils::add_json_member("limit_up", m_up.get(), allocator, root, value_num);
  if (m_down != boost::none) monero_utils::add_json_member("limit_down", m_down.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO SUBMIT TX PARAMS ---------------------------

rapidjson::Value monero_submit_tx_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tx_hex != boost::none) monero_utils::add_json_member("tx_as_hex", m_tx_hex.get(), allocator, root, value_str);

  // set bool values
  if (m_do_not_relay != boost::none) monero_utils::add_json_member("do_not_relay", m_do_not_relay.get(), allocator, root);

  // set sub-arrays
  if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);

  // return root
  return root;
}

// --------------------------- MONERO PEER LIMITS PARAMS ---------------------------

rapidjson::Value monero_peer_limits_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_in_peers != boost::none) monero_utils::add_json_member("in_peers", m_in_peers.get(), allocator, root, value_num);
  if (m_out_peers != boost::none) monero_utils::add_json_member("out_peers", m_out_peers.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO GET TXS PARAMS ---------------------------

rapidjson::Value monero_get_txs_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set bool values
  if (m_prune != boost::none) monero_utils::add_json_member("prune", m_prune.get(), allocator, root);
  if (m_decode_as_json != boost::none) monero_utils::add_json_member("decode_as_json", m_decode_as_json.get(), allocator, root);

  // set sub-arrays
  if (!m_tx_hashes.empty()) root.AddMember("txs_hashes", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);

  // return root
  return root;
}

// --------------------------- MONERO IS KEY IMAGE SPENT PARAMS ---------------------------

rapidjson::Value monero_is_key_image_spent_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set sub-arrays
  if (!m_key_images.empty()) root.AddMember("key_images", monero_utils::to_rapidjson_val(allocator, m_key_images), allocator);

  // return root
  return root;
}

// --------------------------- MONERO START MINING PARAMS ---------------------------

rapidjson::Value monero_start_mining_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_miner_address != boost::none) monero_utils::add_json_member("miner_address", m_miner_address.get(), allocator, root, value_str);

  // set number values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);

  // set bool values
  if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
  if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO PRUNE BLOCKCHAIN PARAMS ---------------------------

rapidjson::Value monero_prune_blockchain_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set bool values
  if (m_check != boost::none) monero_utils::add_json_member("check", m_check.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO SUBMIT BLOCKS PARAMS ---------------------------

rapidjson::Value monero_submit_blocks_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  return monero_utils::to_rapidjson_val(allocator, m_block_blobs);
}

// --------------------------- MONERO GET BLOCK PARAMS ---------------------------

rapidjson::Value monero_get_block_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_num(rapidjson::kNumberType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
  if (m_wallet_address != boost::none) monero_utils::add_json_member("wallet_address", m_wallet_address.get(), allocator, root, value_str);

  // set num values
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);
  if (m_end_height != boost::none) monero_utils::add_json_member("end_height", m_end_height.get(), allocator, root, value_num);
  if (m_reserve_size != boost::none) monero_utils::add_json_member("reserve_size", m_reserve_size.get(), allocator, root, value_num);

  // set bool values
  if (m_fill_pow_hash != boost::none) monero_utils::add_json_member("fill_pow_hash", m_fill_pow_hash.get(), allocator, root);

  // return root
  return root;
}

// --------------------------- MONERO GET BLOCK HASH PARAMS ---------------------------

rapidjson::Value monero_get_block_hash_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  std::vector<uint64_t> params;
  if (m_height != boost::none) params.push_back(m_height.get());
  return monero_utils::to_rapidjson_val(allocator, params);
}

// --------------------------- MONERO GET MINER TX SUM PARAMS ---------------------------

rapidjson::Value monero_get_miner_tx_sum_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set num values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_count != boost::none) monero_utils::add_json_member("count", m_count.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO GET FEE ESTIMATE PARAMS ---------------------------

rapidjson::Value monero_get_fee_estimate_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set num values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_grace_blocks != boost::none) monero_utils::add_json_member("grace_blocks", m_grace_blocks.get(), allocator, root, value_num);

  // return root
  return root;
}

// --------------------------- MONERO SET BANS PARAMS ---------------------------

rapidjson::Value monero_set_bans_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set sub-arrays
  if (!m_bans.empty()) root.AddMember("bans", monero_utils::to_rapidjson_val(allocator, m_bans), allocator);

  // return root
  return root;
}

// --------------------------- MONERO GET OUTPUT HISTOGRAM PARAMS ---------------------------

rapidjson::Value monero_get_output_histogram_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set num values
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_min_count != boost::none) monero_utils::add_json_member("min_count", m_min_count.get(), allocator, root, value_num);
  if (m_max_count != boost::none) monero_utils::add_json_member("max_count", m_max_count.get(), allocator, root, value_num);
  if (m_recent_cutoff != boost::none) monero_utils::add_json_member("recent_cutoff", m_recent_cutoff.get(), allocator, root, value_num);

  // set bool values
  if (m_is_unlocked != boost::none) monero_utils::add_json_member("is_unlocked", m_is_unlocked.get(), allocator, root);

  // set sub-array values
  if (!m_amounts.empty()) root.AddMember("amounts", monero_utils::to_rapidjson_val(allocator, m_amounts), allocator);

  // return root
  return root;
}

// --------------------------- MONERO GET BLOCK RESULT ---------------------------

void monero_get_block_result::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_block_result>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("count")) result->m_count = it->second.get_value<uint64_t>();
    else if (key == std::string("height")) result->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("untrusted")) result->m_untrusted = it->second.get_value<bool>();
  }
}

void monero_get_block_result::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes) {
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
