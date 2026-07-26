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

#include <pybind11/stl_bind.h>
#include <pybind11/eval.h>
#include "common/py_monero_common.h"
#include "daemon/monero_daemon.h"

class PyMoneroDaemonListener : public monero_daemon_listener {
public:
  void on_block_header(const std::shared_ptr<monero_block_header>& header) override {
    PYBIND11_OVERRIDE(void, monero_daemon_listener, on_block_header, header);
  }
};

class PyMoneroDaemon : public monero_daemon {
public:
  /**
    * Virtual destructor.
    */
  ~PyMoneroDaemon() = default;
  PyMoneroDaemon() { }

  void add_listener(monero_daemon_listener &listener) override {
    PYBIND11_OVERRIDE(void, monero_daemon, add_listener, listener);
  }

  void remove_listener(monero_daemon_listener &listener) override {
    PYBIND11_OVERRIDE(void, monero_daemon, remove_listener, listener);
  }

  std::set<monero_daemon_listener*> get_listeners() override {
    PYBIND11_OVERRIDE(std::set<monero_daemon_listener*>, monero_daemon, get_listeners);
  }

  void remove_listeners() override {
    PYBIND11_OVERRIDE(void, monero_daemon, remove_listeners);
  }

  monero_version get_version() override {
    PYBIND11_OVERRIDE(monero_version, monero_daemon, get_version);
  }

  bool is_trusted() override {
    PYBIND11_OVERRIDE(bool, monero_daemon, is_trusted);
  }

  uint64_t get_height() override {
    PYBIND11_OVERRIDE(uint64_t, monero_daemon, get_height);
  }

  std::string get_block_hash(uint64_t height) override {
    PYBIND11_OVERRIDE(std::string, monero_daemon, get_block_hash, height);
  }

  std::shared_ptr<monero_block_template> get_block_template(const std::string& wallet_address, const boost::optional<int>& reserve_size = boost::none) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block_template>, monero_daemon, get_block_template, wallet_address, reserve_size);
  }

  std::shared_ptr<monero_block_header> get_last_block_header() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block_header>, monero_daemon, get_last_block_header);
  }

  std::shared_ptr<monero_block_header> get_block_header_by_hash(const std::string& hash) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block_header>, monero_daemon, get_block_header_by_hash, hash);
  }

  std::shared_ptr<monero_block_header> get_block_header_by_height(uint64_t height) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block_header>, monero_daemon, get_block_header_by_height, height);
  }

  std::vector<std::shared_ptr<monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_block_header>>, monero_daemon, get_block_headers_by_range, start_height, end_height);
  }

  std::shared_ptr<monero_block> get_block_by_hash(const std::string& hash) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block>, monero_daemon, get_block_by_hash, hash);
  }

  std::vector<std::shared_ptr<monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_block>>, monero_daemon, get_blocks_by_hash, block_hashes, start_height, prune);
  }

  std::shared_ptr<monero_block> get_block_by_height(uint64_t height) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block>, monero_daemon, get_block_by_height, height);
  }

  std::vector<std::shared_ptr<monero_block>> get_blocks_by_height(const std::vector<uint64_t>& heights) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_block>>, monero_daemon, get_blocks_by_height, heights);
  }

  std::vector<std::shared_ptr<monero_block>> get_blocks_by_range(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_block>>, monero_daemon, get_blocks_by_range, start_height, end_height);
  }

  std::vector<std::shared_ptr<monero_block>> get_blocks_by_range_chunked(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height, boost::optional<uint64_t> max_chunk_size) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_block>>, monero_daemon, get_blocks_by_range_chunked, start_height, end_height, max_chunk_size);
  }

  std::vector<std::string> get_block_hashes(const std::vector<std::string>& block_hashes, uint64_t start_height) override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_daemon, get_block_hashes, block_hashes, start_height);
  }

  std::shared_ptr<monero_tx> get_tx(const std::string& tx_hash, bool prune = false) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_tx>, monero_daemon, get_tx, tx_hash, prune);
  }

  std::vector<std::shared_ptr<monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx>>, monero_daemon, get_txs, tx_hashes, prune);
  }

  boost::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false) override {
    PYBIND11_OVERRIDE(boost::optional<std::string>, monero_daemon, get_tx_hex, tx_hash, prune);
  }

  std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_daemon, get_tx_hexes, tx_hashes, prune);
  }

  std::shared_ptr<monero_miner_tx_sum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_miner_tx_sum>, monero_daemon, get_miner_tx_sum, height, num_blocks);
  }

  std::shared_ptr<monero_fee_estimate> get_fee_estimate(uint64_t grace_blocks = 0) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_fee_estimate>, monero_daemon, get_fee_estimate, grace_blocks);
  }

  std::shared_ptr<monero_submit_tx_result> submit_tx_hex(const std::string& tx_hex, bool do_not_relay = false) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_submit_tx_result>, monero_daemon, submit_tx_hex, tx_hex, do_not_relay);
  }

  void relay_tx_by_hash(const std::string& tx_hash) override {
    PYBIND11_OVERRIDE(void, monero_daemon, relay_tx_by_hash, tx_hash);
  }

  void relay_txs_by_hash(const std::vector<std::string>& tx_hashes) override {
    PYBIND11_OVERRIDE(void, monero_daemon, relay_txs_by_hash, tx_hashes);
  }

  std::vector<std::shared_ptr<monero_tx>> get_tx_pool() override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_tx>>, monero_daemon, get_tx_pool);
  }

  std::vector<std::string> get_tx_pool_hashes() override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_daemon, get_tx_pool_hashes);
  }

  std::vector<monero_tx_backlog_entry> get_tx_pool_backlog() override {
    PYBIND11_OVERRIDE(std::vector<monero_tx_backlog_entry>, monero_daemon, get_tx_pool_backlog);
  }

  std::shared_ptr<monero_tx_pool_stats> get_tx_pool_stats() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_tx_pool_stats>, monero_daemon, get_tx_pool_stats);
  }

  void flush_tx_pool() override {
    PYBIND11_OVERRIDE(void, monero_daemon, flush_tx_pool);
  }

  void flush_tx_pool(const std::vector<std::string> &hashes) override {
    PYBIND11_OVERRIDE(void, monero_daemon, flush_tx_pool, hashes);
  }

  void flush_tx_pool(const std::string &hash) override {
    PYBIND11_OVERRIDE(void, monero_daemon, flush_tx_pool, hash);
  }

  monero_key_image_spent_status get_key_image_spent_status(const std::string& key_image) override {
    PYBIND11_OVERRIDE(monero_key_image_spent_status, monero_daemon, get_key_image_spent_status, key_image);
  }

  std::vector<monero_key_image_spent_status> get_key_image_spent_statuses(const std::vector<std::string>& key_images) override {
    PYBIND11_OVERRIDE(std::vector<monero_key_image_spent_status>, monero_daemon, get_key_image_spent_statuses, key_images);
  }

  std::vector<std::shared_ptr<monero_output>> get_outputs(const std::vector<monero_output>& outputs) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_output>>, monero_daemon, get_outputs, outputs);
  }

  std::vector<std::shared_ptr<monero_output_histogram_entry>> get_output_histogram(const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_output_histogram_entry>>, monero_daemon, get_output_histogram, amounts, min_count, max_count, is_unlocked, recent_cutoff);
  }

  std::vector<std::shared_ptr<monero_output_distribution_entry>> get_output_distribution(const std::vector<uint64_t>& amounts, const boost::optional<bool>& is_cumulative = boost::none, const boost::optional<uint64_t>& start_height = boost::none, const boost::optional<uint64_t>& end_height = boost::none) override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_output_distribution_entry>>, monero_daemon, get_output_distribution, amounts, is_cumulative, start_height, end_height);
  }

  std::shared_ptr<monero_daemon_info> get_info() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_daemon_info>, monero_daemon, get_info);
  }

  std::shared_ptr<monero_daemon_sync_info> get_sync_info() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_daemon_sync_info>, monero_daemon, get_sync_info);
  }

  std::shared_ptr<monero_hard_fork_info> get_hard_fork_info() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_hard_fork_info>, monero_daemon, get_hard_fork_info);
  }

  std::vector<std::shared_ptr<monero_alt_chain>> get_alt_chains() override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_alt_chain>>, monero_daemon, get_alt_chains);
  }

  std::vector<std::string> get_alt_block_hashes() override {
    PYBIND11_OVERRIDE(std::vector<std::string>, monero_daemon, get_alt_block_hashes);
  }

  int get_download_limit() override {
    PYBIND11_OVERRIDE(int, monero_daemon, get_download_limit);
  }

  int set_download_limit(int limit) override {
    PYBIND11_OVERRIDE(int, monero_daemon, set_download_limit, limit);
  }

  int reset_download_limit() override {
    PYBIND11_OVERRIDE(int, monero_daemon, reset_download_limit);
  }

  int get_upload_limit() override {
    PYBIND11_OVERRIDE(int, monero_daemon, get_upload_limit);
  }

  int set_upload_limit(int limit) override {
    PYBIND11_OVERRIDE(int, monero_daemon, set_upload_limit, limit);
  }

  int reset_upload_limit() override {
    PYBIND11_OVERRIDE(int, monero_daemon, reset_upload_limit);
  }

  std::vector<std::shared_ptr<monero_peer>> get_peers() override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_peer>>, monero_daemon, get_peers);
  }

  std::vector<std::shared_ptr<monero_peer>> get_known_peers() override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_peer>>, monero_daemon, get_known_peers);
  }

  void set_outgoing_peer_limit(int limit) override {
    PYBIND11_OVERRIDE(void, monero_daemon, set_outgoing_peer_limit, limit);
  }

  void set_incoming_peer_limit(int limit) override {
    PYBIND11_OVERRIDE(void, monero_daemon, set_incoming_peer_limit, limit);
  }

  std::vector<std::shared_ptr<monero_ban>> get_peer_bans() override {
    PYBIND11_OVERRIDE(std::vector<std::shared_ptr<monero_ban>>, monero_daemon, get_peer_bans);
  }

  void set_peer_bans(const std::vector<std::shared_ptr<monero_ban>>& bans) override {
    PYBIND11_OVERRIDE(void, monero_daemon, set_peer_bans, bans);
  }

  void set_peer_ban(const std::shared_ptr<monero_ban>& ban) override {
    PYBIND11_OVERRIDE(void, monero_daemon, set_peer_ban, ban);
  }

  void start_mining(const std::string &address, boost::optional<uint64_t> num_threads, boost::optional<bool> is_background, boost::optional<bool> ignore_battery) override {
    PYBIND11_OVERRIDE(void, monero_daemon, start_mining, address, num_threads, is_background, ignore_battery);
  }

  void stop_mining() override {
    PYBIND11_OVERRIDE(void, monero_daemon, stop_mining);
  }

  std::shared_ptr<monero_mining_status> get_mining_status() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_mining_status>, monero_daemon, get_mining_status);
  }

  std::shared_ptr<monero_generate_blocks_result> generate_blocks(const std::string& wallet_address, uint64_t num_blocks, const boost::optional<std::string>& prev_block_hash = boost::none, const boost::optional<uint32_t>& starting_nonce = boost::none) {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_generate_blocks_result>, monero_daemon, generate_blocks, wallet_address, num_blocks, prev_block_hash, starting_nonce);
  }

  void submit_block(const std::string& block_blob) override {
    PYBIND11_OVERRIDE(void, monero_daemon, submit_block, block_blob);
  }

  void submit_blocks(const std::vector<std::string>& block_blobs) override {
    PYBIND11_OVERRIDE(void, monero_daemon, submit_blocks, block_blobs);
  }

  std::shared_ptr<monero_prune_result> prune_blockchain(bool check) override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_prune_result>, monero_daemon, prune_blockchain, check);
  }

  std::shared_ptr<monero_daemon_update_check_result> check_for_update() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_daemon_update_check_result>, monero_daemon, check_for_update);
  }

  std::shared_ptr<monero_daemon_update_download_result> download_update(const std::string& path = "") override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_daemon_update_download_result>, monero_daemon, download_update, path);
  }

  void stop() override {
    PYBIND11_OVERRIDE(void, monero_daemon, stop);
  }

  std::shared_ptr<monero_block_header> wait_for_next_block_header() override {
    PYBIND11_OVERRIDE(std::shared_ptr<monero_block_header>, monero_daemon, wait_for_next_block_header);
  }
};
