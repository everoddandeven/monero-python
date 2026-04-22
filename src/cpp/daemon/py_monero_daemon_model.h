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

#include "common/py_monero_common.h"

// ------------------------------ Custom Data Model ---------------------------------

struct PyMoneroBlockHeader : public monero::monero_block_header {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block_header>& header);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_block_header>>& headers);
};

struct PyMoneroBlock : public PyMoneroBlockHeader {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block>& block);
  static void from_property_tree(const boost::property_tree::ptree& node, const std::vector<uint64_t>& heights, std::vector<std::shared_ptr<monero::monero_block>>& blocks);
};

struct PyMoneroOutput : public monero::monero_output {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output>& output);
};

struct PyMoneroTx : public monero::monero_tx {
public:
  inline static const std::string DEFAULT_ID = "0000000000000000000000000000000000000000000000000000000000000000";

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx>& tx);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_tx>>& txs);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& tx_hashes);
};

struct PyMoneroVersion : public monero::monero_version {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroVersion>& version);
};

// ------------------------------ Extended Data Model ---------------------------------

enum monero_key_image_spent_status : uint8_t {
  NOT_SPENT = 0,
  CONFIRMED,
  TX_POOL
};

/**
 * Models a Monero RPC payment information.
 */
struct monero_rpc_payment_info : public monero::serializable_struct {
public:
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_rpc_payment_info>& rpc_payment_info);
};

struct monero_alt_chain {
public:
  std::vector<std::string> m_block_hashes;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_length;
  boost::optional<std::string> m_main_chain_parent_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_alt_chain>& alt_chain);
};

struct monero_ban : public monero::serializable_struct {
public:
  boost::optional<std::string> m_host;
  boost::optional<int> m_ip;
  boost::optional<bool> m_is_banned;
  boost::optional<uint64_t> m_seconds;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_ban>& ban);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_ban>>& bans);
};

struct monero_prune_result {
public:
  boost::optional<bool> m_is_pruned;
  boost::optional<int> m_pruning_seed;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_prune_result>& result);
};

struct monero_mining_status {
public:
  boost::optional<bool> m_is_active;
  boost::optional<bool> m_is_background;
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_speed;
  boost::optional<int> m_num_threads;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_mining_status>& status);
};

struct monero_miner_tx_sum {
public:
  boost::optional<uint64_t> m_emission_sum;
  boost::optional<uint64_t> m_fee_sum;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_miner_tx_sum>& sum);
};

struct monero_block_template {
public:
  boost::optional<std::string> m_block_template_blob;
  boost::optional<std::string> m_block_hashing_blob;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_expected_reward;
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_prev_hash;
  boost::optional<uint64_t> m_reserved_offset;
  boost::optional<uint64_t> m_seed_height;
  boost::optional<std::string> m_seed_hash;
  boost::optional<std::string> m_next_seed_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_block_template>& tmplt);
};

struct monero_connection_span {
public:
  boost::optional<std::string> m_connection_id;
  boost::optional<uint64_t> m_num_blocks;
  boost::optional<std::string> m_remote_address;
  boost::optional<uint64_t> m_rate;
  boost::optional<uint64_t> m_speed;
  boost::optional<uint64_t> m_size;
  boost::optional<uint64_t> m_start_height;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_connection_span>& span);
};

struct monero_peer {
public:
  boost::optional<std::string> m_id;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_host;
  boost::optional<int> m_port;
  boost::optional<bool> m_is_online;
  boost::optional<uint64_t> m_last_seen_timestamp;
  boost::optional<int> m_pruning_seed;
  boost::optional<int> m_rpc_port;
  boost::optional<uint64_t> m_rpc_credits_per_hash;
  boost::optional<std::string> m_hash;
  boost::optional<uint64_t> m_avg_download;
  boost::optional<uint64_t> m_avg_upload;
  boost::optional<uint64_t> m_current_download;
  boost::optional<uint64_t> m_current_upload;
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_is_incoming;
  boost::optional<uint64_t> m_live_time;
  boost::optional<bool> m_is_local_ip;
  boost::optional<bool> m_is_local_host;
  boost::optional<int> m_num_receives;
  boost::optional<int> m_num_sends;
  boost::optional<uint64_t> m_receive_idle_time;
  boost::optional<uint64_t> m_send_idle_time;
  boost::optional<std::string> m_state;
  boost::optional<int> m_num_support_flags;
  boost::optional<monero_connection_type> m_connection_type;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_peer>& peer);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_peer>>& peers);
};

struct monero_submit_tx_result : public monero_rpc_payment_info {
public:
  boost::optional<bool> m_is_good;
  boost::optional<bool> m_is_relayed;
  boost::optional<bool> m_is_double_spend;
  boost::optional<bool> m_is_fee_too_low;
  boost::optional<bool> m_is_mixin_too_low;
  boost::optional<bool> m_has_invalid_input;
  boost::optional<bool> m_has_invalid_output;
  boost::optional<bool> m_has_too_few_outputs;
  boost::optional<bool> m_is_overspend;
  boost::optional<bool> m_is_too_big;
  boost::optional<bool> m_sanity_check_failed;
  boost::optional<std::string> m_reason;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;
  boost::optional<bool> m_is_tx_extra_too_big;
  boost::optional<bool> m_is_nonzero_unlock_time;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_submit_tx_result>& result);
};

struct monero_tx_backlog_entry {
  // TODO
};

struct monero_output_distribution_entry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<int> m_base;
  std::vector<int> m_distribution;
  boost::optional<uint64_t> m_start_height;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output_distribution_entry>& entry);
};

struct monero_output_histogram_entry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<uint64_t> m_num_instances;
  boost::optional<uint64_t> m_unlocked_instances;
  boost::optional<uint64_t> m_recent_instances;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output_histogram_entry>& entry);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero_output_histogram_entry>>& entries);
};

struct monero_tx_pool_stats {
public:
  boost::optional<int> m_num_txs;
  boost::optional<int> m_num_not_relayed;
  boost::optional<int> m_num_failing;
  boost::optional<int> m_num_double_spends;
  boost::optional<int> m_num10m;
  boost::optional<uint64_t> m_fee_total;
  boost::optional<uint64_t> m_bytes_max;
  boost::optional<uint64_t> m_bytes_med;
  boost::optional<uint64_t> m_bytes_min;
  boost::optional<uint64_t> m_bytes_total;
  //private Map<Long, Integer> histo;
  boost::optional<uint64_t> m_histo98pc;
  boost::optional<uint64_t> m_oldest_timestamp;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_tx_pool_stats>& stats);
};

struct monero_daemon_update_check_result {
public:
  boost::optional<bool> m_is_update_available;
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_hash;
  boost::optional<std::string> m_auto_uri;
  boost::optional<std::string> m_user_uri;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_update_check_result>& check);
};

struct monero_daemon_update_download_result : public monero_daemon_update_check_result {
public:
  boost::optional<std::string> m_download_path;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_update_download_result>& check);
};

struct monero_fee_estimate {
public:
  boost::optional<uint64_t> m_fee;
  std::vector<uint64_t> m_fees;
  boost::optional<uint64_t> m_quantization_mask;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_fee_estimate>& estimate);
};

struct monero_daemon_info : public monero_rpc_payment_info {
public:
  boost::optional<std::string> m_version;
  boost::optional<uint64_t> m_num_alt_blocks;
  boost::optional<uint64_t> m_block_size_limit;
  boost::optional<uint64_t> m_block_size_median;
  boost::optional<uint64_t> m_block_weight_limit;
  boost::optional<uint64_t> m_block_weight_median;
  boost::optional<std::string> m_bootstrap_daemon_address;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_cumulative_difficulty;
  boost::optional<uint64_t> m_free_space;
  boost::optional<int> m_num_offline_peers;
  boost::optional<int> m_num_online_peers;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_height_without_bootstrap;
  boost::optional<monero::monero_network_type> m_network_type;
  boost::optional<bool> m_is_offline;
  boost::optional<int> m_num_incoming_connections;
  boost::optional<int> m_num_outgoing_connections;
  boost::optional<int> m_num_rpc_connections;
  boost::optional<uint64_t> m_start_timestamp;
  boost::optional<uint64_t> m_adjusted_timestamp;
  boost::optional<uint64_t> m_target;
  boost::optional<uint64_t> m_target_height;
  boost::optional<std::string> m_top_block_hash;
  boost::optional<int> m_num_txs;
  boost::optional<int> m_num_txs_pool;
  boost::optional<bool> m_was_bootstrap_ever_used;
  boost::optional<uint64_t> m_database_size;
  boost::optional<bool> m_update_available;
  boost::optional<uint64_t> m_credits;
  boost::optional<bool> m_is_busy_syncing;
  boost::optional<bool> m_is_synchronized;
  boost::optional<bool> m_is_restricted;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_info>& info);
};

struct monero_daemon_sync_info : public monero_rpc_payment_info {
public:
  boost::optional<uint64_t> m_height;
  std::vector<monero_peer> m_peers;
  std::vector<monero_connection_span> m_spans;
  boost::optional<uint64_t> m_target_height;
  boost::optional<int> m_next_needed_pruning_seed;
  boost::optional<std::string> m_overview;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_daemon_sync_info>& info);
};

struct monero_hard_fork_info : public monero_rpc_payment_info {
public:
  boost::optional<uint64_t> m_earliest_height;
  boost::optional<bool> m_is_enabled;
  boost::optional<int> m_state;
  boost::optional<int> m_threshold;
  boost::optional<int> m_version;
  boost::optional<int> m_num_votes;
  boost::optional<int> m_window;
  boost::optional<int> m_voting;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_hard_fork_info>& info);
};

// ------------------------------ RPC Params ---------------------------------

struct monero_download_update_params : public monero_request_params {
public:
  boost::optional<std::string> m_command;
  boost::optional<std::string> m_path;

  monero_download_update_params(const std::string& command = "download", const std::string& path = "");

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_submit_tx_params : public monero_request_params {
public:
  boost::optional<std::string> m_tx_hex;
  boost::optional<bool> m_do_not_relay;

  monero_submit_tx_params(const std::string& tx_hex, bool do_not_relay): m_tx_hex(tx_hex), m_do_not_relay(do_not_relay) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_bandwith_limits_params : public monero_request_params {
public:
  boost::optional<int> m_up;
  boost::optional<int> m_down;

  monero_bandwith_limits_params() { }
  monero_bandwith_limits_params(int up, int down): m_up(up), m_down(down) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_bandwith_limits_params>& limits);
};

struct monero_peer_limits_params : public monero_request_params {
public:
  boost::optional<int> m_in_peers;
  boost::optional<int> m_out_peers;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_txs_params : public monero_request_params {
public:
  std::vector<std::string> m_tx_hashes;
  boost::optional<bool> m_decode_as_json;
  boost::optional<bool> m_prune;

  monero_get_txs_params(const std::vector<std::string> &tx_hashes, bool prune, bool decode_as_json = true): m_tx_hashes(tx_hashes), m_prune(prune), m_decode_as_json(decode_as_json) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_is_key_image_spent_params : public monero_request_params {
public:
  std::vector<std::string> m_key_images;

  monero_is_key_image_spent_params(const std::vector<std::string>& key_images): m_key_images(key_images) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

// ------------------------------ JSON-RPC Params ---------------------------------

struct monero_start_mining_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_miner_address;
  boost::optional<int> m_num_threads;
  boost::optional<bool> m_is_background;
  boost::optional<bool> m_ignore_battery;

  monero_start_mining_params(const std::string& address, int num_threads, bool is_background, bool ignore_battery): m_miner_address(address), m_num_threads(num_threads), m_is_background(is_background), m_ignore_battery(ignore_battery) { }
  monero_start_mining_params(int num_threads, bool is_background, bool ignore_battery): m_num_threads(num_threads), m_is_background(is_background), m_ignore_battery(ignore_battery) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_prune_blockchain_params : public monero_json_request_params {
public:
  boost::optional<bool> m_check;

  monero_prune_blockchain_params(bool check = true): m_check(check) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_submit_blocks_params : public monero_json_request_params {
public:
  std::vector<std::string> m_block_blobs;

  monero_submit_blocks_params(const std::vector<std::string>& block_blobs): m_block_blobs(block_blobs) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_block_params : public monero_json_request_params {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_hash;
  boost::optional<bool> m_fill_pow_hash;
  boost::optional<uint64_t> m_start_height;
  boost::optional<uint64_t> m_end_height;

  monero_get_block_params(uint64_t height, bool fill_pow_hash = false): m_height(height), m_fill_pow_hash(fill_pow_hash) { }
  monero_get_block_params(const std::string& hash, bool fill_pow_hash = false): m_hash(hash), m_fill_pow_hash(fill_pow_hash) { }
  monero_get_block_params(uint64_t start_height, uint64_t end_height): m_start_height(start_height), m_end_height(end_height) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_block_hash_params : public monero_json_request_params {
public:
  boost::optional<uint64_t> m_height;

  monero_get_block_hash_params(uint64_t height): m_height(height) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_block_template_params : public monero_json_request_params {
public:
  boost::optional<std::string> m_wallet_address;
  boost::optional<int> m_reserve_size;

  monero_get_block_template_params(const std::string& wallet_address, const boost::optional<int>& reserve_size = boost::none): m_wallet_address(wallet_address), m_reserve_size(reserve_size) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_relay_tx_params : public monero_json_request_params {
public:
  std::vector<std::string> m_tx_hashes;

  monero_relay_tx_params(const std::vector<std::string>& tx_hashes): m_tx_hashes(tx_hashes) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_miner_tx_sum_params : public monero_json_request_params {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_count;

  monero_get_miner_tx_sum_params(uint64_t height, uint64_t count): m_height(height), m_count(count) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_fee_estimate_params : public monero_json_request_params {
public:
  boost::optional<uint64_t> m_grace_blocks;

  monero_get_fee_estimate_params(uint64_t grace_blocks = 0): m_grace_blocks(grace_blocks) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_set_bans_params : public monero_json_request_params {
public:
  std::vector<std::shared_ptr<monero_ban>> m_bans;

  monero_set_bans_params(const std::vector<std::shared_ptr<monero_ban>>& bans): m_bans(bans) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_output_histogram_params : public monero_json_request_params {
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

struct monero_get_block_count_result {
public:
  boost::optional<uint64_t> m_count;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_block_count_result>& result);
};

struct monero_get_alt_block_hashes_response {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes);
};

struct monero_get_height_response {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_untrusted;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_get_height_response>& response);
};
