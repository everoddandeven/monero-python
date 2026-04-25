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


class monero_daemon_listener {
public:
  virtual void on_block_header(const std::shared_ptr<monero::monero_block_header>& header) {
    m_last_header = header;
  }

  std::shared_ptr<monero::monero_block_header> m_last_header;
};

class PyMoneroDaemonListener : public monero_daemon_listener {
public:
  virtual void on_block_header(const std::shared_ptr<monero::monero_block_header>& header) {
    PYBIND11_OVERRIDE(void, monero_daemon_listener, on_block_header, header);
  }
};

class monero_daemon {
public:
  /**
    * Virtual destructor.
    */
  virtual ~monero_daemon() {}
  monero_daemon() { }
  virtual void add_listener(monero_daemon_listener &listener) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void remove_listener(monero_daemon_listener &listener) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::set<monero_daemon_listener*> get_listeners() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void remove_listeners() { throw std::runtime_error("monero_daemon::remove_listeners(): not supported"); };
  virtual monero::monero_version get_version() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual bool is_trusted() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual uint64_t get_height() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::string get_block_hash(uint64_t height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_block_template> get_block_template(const std::string& wallet_address, const boost::optional<int>& reserve_size = boost::none) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> get_last_block_header() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_hash(const std::string& hash) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_height(uint64_t height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_height(uint64_t height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_height(const std::vector<uint64_t>& heights) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range_chunked(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height, boost::optional<uint64_t> max_chunk_size) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::string> get_block_hashes(const std::vector<std::string>& block_hashes, uint64_t start_height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual boost::optional<std::shared_ptr<monero::monero_tx>> get_tx(const std::string& tx_hash, bool prune = false) {
    std::vector<std::string> hashes;
    hashes.push_back(tx_hash);
    auto txs = get_txs(hashes, prune);
    boost::optional<std::shared_ptr<monero::monero_tx>> tx;

    if (txs.size() > 0) {
      tx = txs[0];
    }

    return tx;
  }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual boost::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false) {
    std::vector<std::string> hashes;
    hashes.push_back(tx_hash);
    auto hexes = get_tx_hexes(hashes, prune);
    boost::optional<std::string> hex;
    if (hexes.size() > 0) {
      hex = hexes[0];
    }

    return hex;
  }
  virtual std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_miner_tx_sum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_fee_estimate> get_fee_estimate(uint64_t grace_blocks = 0) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_submit_tx_result> submit_tx_hex(const std::string& tx_hex, bool do_not_relay = false) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void relay_tx_by_hash(const std::string& tx_hash) {
    std::vector<std::string> tx_hashes;
    tx_hashes.push_back(tx_hash);
    relay_txs_by_hash(tx_hashes);
  }
  virtual void relay_txs_by_hash(const std::vector<std::string>& tx_hashes) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_tx_pool() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::string> get_tx_pool_hashes() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<monero_tx_backlog_entry> get_tx_pool_backlog() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_tx_pool_stats> get_tx_pool_stats() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void flush_tx_pool() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void flush_tx_pool(const std::vector<std::string> &hashes) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void flush_tx_pool(const std::string &hash) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual monero_key_image_spent_status get_key_image_spent_status(const std::string& key_image) {
    std::vector<std::string> key_images;
    key_images.push_back(key_image);
    auto statuses = get_key_image_spent_statuses(key_images);
    if (statuses.empty()) throw std::runtime_error("Could not get key image spent status");
    return statuses[0];
  }
  virtual std::vector<monero_key_image_spent_status> get_key_image_spent_statuses(const std::vector<std::string>& key_images) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_output>> get_outputs(const std::vector<monero::monero_output>& outputs) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_output_histogram_entry>> get_output_histogram(const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_output_distribution_entry>> get_output_distribution(const std::vector<uint64_t>& amounts) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_output_distribution_entry>> get_output_distribution(const std::vector<uint64_t>& amounts, bool is_cumulative, uint64_t start_height, uint64_t end_height) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_daemon_info> get_info() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_daemon_sync_info> get_sync_info() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_hard_fork_info> get_hard_fork_info() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_alt_chain>> get_alt_chains() { throw std::runtime_error("monero_daemon::get_alt_chains(): not supported"); }
  virtual std::vector<std::string> get_alt_block_hashes() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual int get_download_limit() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual int set_download_limit(int limit) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual int reset_download_limit() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual int get_upload_limit() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual int set_upload_limit(int limit) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual int reset_upload_limit() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_peer>> get_peers() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_peer>> get_known_peers() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void set_outgoing_peer_limit(int limit) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void set_incoming_peer_limit(int limit) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero_ban>> get_peer_bans() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void set_peer_bans(const std::vector<std::shared_ptr<monero_ban>>& bans) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void set_peer_ban(const std::shared_ptr<monero_ban>& ban) {
    if (ban == nullptr) throw std::runtime_error("Ban is none");
    std::vector<std::shared_ptr<monero_ban>> bans;
    bans.push_back(ban);
    set_peer_bans(bans);
  }
  virtual void start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void stop_mining() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_mining_status> get_mining_status() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void submit_block(const std::string& block_blob) {
    std::vector<std::string> block_blobs;
    block_blobs.push_back(block_blob);
    return submit_blocks(block_blobs);
  }
  virtual void submit_blocks(const std::vector<std::string>& block_blobs) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_prune_result> prune_blockchain(bool check) { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_daemon_update_check_result> check_for_update() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero_daemon_update_download_result> download_update(const std::string& path = "") { throw std::runtime_error("monero_daemon: not supported"); }
  virtual void stop() { throw std::runtime_error("monero_daemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> wait_for_next_block_header() { throw std::runtime_error("monero_daemon: not supported"); }
};
