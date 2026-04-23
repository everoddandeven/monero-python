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

#include "py_monero_daemon_model.h"

// ------------------------------ RPC Params ---------------------------------

struct monero_download_update_params : public monero::serializable_struct {
public:
  boost::optional<std::string> m_command;
  boost::optional<std::string> m_path;

  monero_download_update_params(const std::string& command = "download", const std::string& path = "");

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_submit_tx_params : public monero::serializable_struct {
public:
  boost::optional<std::string> m_tx_hex;
  boost::optional<bool> m_do_not_relay;
  std::vector<std::string> m_tx_hashes;

  monero_submit_tx_params(const std::vector<std::string>& tx_hashes): m_tx_hashes(tx_hashes) { }
  monero_submit_tx_params(const std::string& tx_hex, bool do_not_relay): m_tx_hex(tx_hex), m_do_not_relay(do_not_relay) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_peer_limits_params : public monero::serializable_struct {
public:
  boost::optional<int> m_in_peers;
  boost::optional<int> m_out_peers;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_txs_params : public monero::serializable_struct {
public:
  std::vector<std::string> m_tx_hashes;
  boost::optional<bool> m_decode_as_json;
  boost::optional<bool> m_prune;

  monero_get_txs_params(const std::vector<std::string> &tx_hashes, bool prune, bool decode_as_json = true): m_tx_hashes(tx_hashes), m_prune(prune), m_decode_as_json(decode_as_json) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_is_key_image_spent_params : public monero::serializable_struct {
public:
  std::vector<std::string> m_key_images;

  monero_is_key_image_spent_params(const std::vector<std::string>& key_images): m_key_images(key_images) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

// ------------------------------ JSON-RPC Params ---------------------------------

struct monero_start_mining_params : public monero::serializable_struct {
public:
  boost::optional<std::string> m_miner_address;
  boost::optional<int> m_num_threads;
  boost::optional<bool> m_is_background;
  boost::optional<bool> m_ignore_battery;

  monero_start_mining_params(const std::string& address, int num_threads, bool is_background, bool ignore_battery): m_miner_address(address), m_num_threads(num_threads), m_is_background(is_background), m_ignore_battery(ignore_battery) { }
  monero_start_mining_params(int num_threads, bool is_background, bool ignore_battery): m_num_threads(num_threads), m_is_background(is_background), m_ignore_battery(ignore_battery) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_prune_blockchain_params : public monero::serializable_struct {
public:
  boost::optional<bool> m_check;

  monero_prune_blockchain_params(bool check = true): m_check(check) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_submit_blocks_params : public monero::serializable_struct {
public:
  std::vector<std::string> m_block_blobs;

  monero_submit_blocks_params(const std::vector<std::string>& block_blobs): m_block_blobs(block_blobs) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_block_params : public monero::serializable_struct {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_hash;
  boost::optional<bool> m_fill_pow_hash;
  boost::optional<uint64_t> m_start_height;
  boost::optional<uint64_t> m_end_height;
  boost::optional<std::string> m_wallet_address;
  boost::optional<int> m_reserve_size;

  monero_get_block_params(uint64_t height, bool fill_pow_hash = false): m_height(height), m_fill_pow_hash(fill_pow_hash) { }
  monero_get_block_params(const std::string& hash, bool fill_pow_hash = false): m_hash(hash), m_fill_pow_hash(fill_pow_hash) { }
  monero_get_block_params(uint64_t start_height, uint64_t end_height): m_start_height(start_height), m_end_height(end_height) { }
  monero_get_block_params(const std::string& wallet_address, const boost::optional<int>& reserve_size): m_wallet_address(wallet_address), m_reserve_size(reserve_size) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_block_hash_params : public monero::serializable_struct {
public:
  boost::optional<uint64_t> m_height;

  monero_get_block_hash_params(uint64_t height): m_height(height) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_miner_tx_sum_params : public monero::serializable_struct {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_count;

  monero_get_miner_tx_sum_params(uint64_t height, uint64_t count): m_height(height), m_count(count) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_fee_estimate_params : public monero::serializable_struct {
public:
  boost::optional<uint64_t> m_grace_blocks;

  monero_get_fee_estimate_params(uint64_t grace_blocks = 0): m_grace_blocks(grace_blocks) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_set_bans_params : public monero::serializable_struct {
public:
  std::vector<std::shared_ptr<monero_ban>> m_bans;

  monero_set_bans_params(const std::vector<std::shared_ptr<monero_ban>>& bans): m_bans(bans) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_output_histogram_params : public monero::serializable_struct {
public:
  std::vector<uint64_t> m_amounts;
  boost::optional<int> m_min_count;
  boost::optional<int> m_max_count;
  boost::optional<bool> m_is_unlocked;
  boost::optional<int> m_recent_cutoff;

  monero_get_output_histogram_params(const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) : m_amounts(amounts), m_min_count(min_count), m_max_count(max_count), m_is_unlocked(is_unlocked), m_recent_cutoff(recent_cutoff) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

// ------------------------------ JSON-RPC Response ---------------------------------

struct monero_get_block_result {
public:
  boost::optional<uint64_t> m_count;
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_untrusted;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_block_result>& result);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes);
};
