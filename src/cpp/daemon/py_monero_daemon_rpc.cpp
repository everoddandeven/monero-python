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
#include "py_monero_daemon_rpc.h"
#include "py_monero_daemon_rpc_model.h"
#include "utils/py_monero_utils.h"

static const uint64_t MAX_REQ_SIZE = 3000000;
static const uint64_t NUM_HEADERS_PER_REQ = 750;

/**
 * Polls daemon and sends notifications in order to notify external daemon listeners.
 */
class monero_daemon_poller: public thread_poller {
public:

  explicit monero_daemon_poller(monero_daemon* daemon, uint64_t poll_period_ms = 5000): m_daemon(daemon) {
    init_common("monero_daemon_rpc");
    m_poll_period_ms = poll_period_ms;
  }

  void poll() override {
    if (!m_last_header) {
      m_last_header = m_daemon->get_last_block_header();
      return;
    }

    auto header = m_daemon->get_last_block_header();
    if (header->m_hash != m_last_header->m_hash) {
      m_last_header = header;
      announce_block_header(header);
    }
  }

private:
  monero_daemon* m_daemon;
  std::shared_ptr<monero::monero_block_header> m_last_header;

  void announce_block_header(const std::shared_ptr<monero::monero_block_header>& header) {
    const auto& listeners = m_daemon->get_listeners();
    for (const auto& listener : listeners) {
      try {
        listener->on_block_header(header);

      } catch (const std::exception& e) {
        MERROR("Error calling listener on new block header: " << e.what());
      }
    }
  }
};

/**
 * Sends a notification on a condition variable when a block is added to blockchain.
 */
class block_notifier : public monero_daemon_listener {
public:
  block_notifier(boost::mutex* temp, boost::condition_variable* cv, bool* ready) { this->temp = temp; this->cv = cv; this->ready = ready; }

  void on_block_header(const std::shared_ptr<monero::monero_block_header>& header) override {
    boost::mutex::scoped_lock lock(*temp);
    m_last_header = header;
    *ready = true;
    cv->notify_one();
  }

private:
  boost::mutex* temp;
  boost::condition_variable* cv;
  bool* ready;
};

monero_daemon_rpc::monero_daemon_rpc(const std::shared_ptr<PyMoneroRpcConnection>& rpc): m_rpc(rpc) {
  if (!rpc->is_online() && rpc->m_uri != boost::none) rpc->check_connection();
}

monero_daemon_rpc::monero_daemon_rpc(const std::string& uri, const std::string& username, const std::string& password, const std::string& proxy_uri, const std::string& zmq_uri, uint64_t timeout):
  m_rpc(std::make_shared<PyMoneroRpcConnection>(uri, username, password, proxy_uri, zmq_uri, 0, timeout)) {
  if (!uri.empty()) m_rpc->check_connection();
}

std::vector<std::shared_ptr<monero_daemon_listener>> monero_daemon_rpc::get_listeners() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  return m_listeners;
}

void monero_daemon_rpc::add_listener(const std::shared_ptr<monero_daemon_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.push_back(listener);
  refresh_listening();
}

void monero_daemon_rpc::remove_listener(const std::shared_ptr<monero_daemon_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<monero_daemon_listener> iter){ return iter == listener; }), m_listeners.end());
  refresh_listening();
}

void monero_daemon_rpc::remove_listeners() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.clear();
  refresh_listening();
}

std::shared_ptr<PyMoneroRpcConnection> monero_daemon_rpc::get_rpc_connection() const {
  MTRACE("monero_daemon_rpc::get_rpc_connection()");
  return m_rpc;
}

bool monero_daemon_rpc::is_connected() {
  try {
    get_version();
    return true;
  }
  catch (...) {
    return false;
  }
}

monero::monero_version monero_daemon_rpc::get_version() {
  auto res = m_rpc->send_json_request("get_version");
  check_response_status(res);
  std::shared_ptr<PyMoneroVersion> info = std::make_shared<PyMoneroVersion>();
  PyMoneroVersion::from_property_tree(res, info);
  return *info;
}

bool monero_daemon_rpc::is_trusted() {
  auto res = m_rpc->send_path_request("get_height");
  check_response_status(res);
  auto get_height_response = std::make_shared<monero_get_block_result>();
  monero_get_block_result::from_property_tree(res, get_height_response);
  return !get_height_response->m_untrusted.get();
}

uint64_t monero_daemon_rpc::get_height() {
  auto res = m_rpc->send_json_request("get_block_count");
  check_response_status(res);
  std::shared_ptr<monero_get_block_result> result = std::make_shared<monero_get_block_result>();
  monero_get_block_result::from_property_tree(res, result);
  if (result->m_count == boost::none) throw std::runtime_error("Could not get height");
  return result->m_count.get();
}

std::string monero_daemon_rpc::get_block_hash(uint64_t height) {
  std::shared_ptr<monero_get_block_hash_params> params = std::make_shared<monero_get_block_hash_params>(height);
  auto res = m_rpc->send_json_request("on_get_block_hash", params);
  return res.data();
}

std::shared_ptr<monero_block_template> monero_daemon_rpc::get_block_template(const std::string& wallet_address, const boost::optional<int>& reserve_size) {
  MTRACE("monero_daemon_rpc::get_block_template()");
  auto params = std::make_shared<monero_get_block_params>(wallet_address, reserve_size);
  auto res = m_rpc->send_json_request("get_block_template", params);
  check_response_status(res);
  std::shared_ptr<monero_block_template> tmplt = std::make_shared<monero_block_template>();
  monero_block_template::from_property_tree(res, tmplt);
  return tmplt;
}

std::shared_ptr<monero::monero_block_header> monero_daemon_rpc::get_last_block_header() {
  auto res = m_rpc->send_json_request("get_last_block_header");
  check_response_status(res);
  std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
  PyMoneroBlockHeader::from_property_tree(res, header);
  return header;
}

std::shared_ptr<monero::monero_block_header> monero_daemon_rpc::get_block_header_by_hash(const std::string& hash) {
  std::shared_ptr<monero_get_block_params> params = std::make_shared<monero_get_block_params>(hash);
  auto res = m_rpc->send_json_request("get_block_header_by_hash", params);
  check_response_status(res);
  std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
  PyMoneroBlockHeader::from_property_tree(res, header);
  return header;
}

std::shared_ptr<monero::monero_block_header> monero_daemon_rpc::get_block_header_by_height(uint64_t height) {
  std::shared_ptr<monero_get_block_params> params = std::make_shared<monero_get_block_params>(height);
  auto res = m_rpc->send_json_request("get_block_header_by_height", params);
  check_response_status(res);
  std::shared_ptr<monero::monero_block_header> header = std::make_shared<monero::monero_block_header>();
  PyMoneroBlockHeader::from_property_tree(res, header);
  return header;
}

std::vector<std::shared_ptr<monero::monero_block_header>> monero_daemon_rpc::get_block_headers_by_range(uint64_t start_height, uint64_t end_height) {
  auto params = std::make_shared<monero_get_block_params>(start_height, end_height);
  auto res = m_rpc->send_json_request("get_block_headers_range", params);
  check_response_status(res);
  std::vector<std::shared_ptr<monero::monero_block_header>> headers;
  PyMoneroBlockHeader::from_property_tree(res, headers);
  return headers;
}

std::shared_ptr<monero::monero_block> monero_daemon_rpc::get_block_by_hash(const std::string& hash) {
  std::shared_ptr<monero_get_block_params> params = std::make_shared<monero_get_block_params>(hash);
  auto res = m_rpc->send_json_request("get_block", params);
  check_response_status(res);
  auto block = std::make_shared<monero::monero_block>();
  PyMoneroBlock::from_property_tree(res, block);
  return block;
}

std::shared_ptr<monero::monero_block_header> monero_daemon_rpc::get_block_header_by_height_cached(uint64_t height, uint64_t max_height) {
  // get header from cache
  auto found = m_cached_headers.find(height);
  if (found != m_cached_headers.end()) return found->second;

  // fetch and cache headers if not in cache
  uint64_t end_height = std::min(max_height, height + NUM_HEADERS_PER_REQ - 1);
  auto headers = get_block_headers_by_range(height, end_height);

  for(const auto& header : headers) {
    m_cached_headers[header->m_height.get()] = header;
  }

  return m_cached_headers[height];
}

std::vector<std::shared_ptr<monero::monero_block>> monero_daemon_rpc::get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) {
  throw std::runtime_error("monero_daemon_rpc::get_blocks_by_hash(): not implemented");
}

std::shared_ptr<monero::monero_block> monero_daemon_rpc::get_block_by_height(uint64_t height) {
  std::shared_ptr<monero_get_block_params> params = std::make_shared<monero_get_block_params>(height);
  auto res = m_rpc->send_json_request("get_block", params);
  check_response_status(res);
  auto block = std::make_shared<monero::monero_block>();
  PyMoneroBlock::from_property_tree(res, block);
  return block;
}

std::vector<std::shared_ptr<monero::monero_block>> monero_daemon_rpc::get_blocks_by_height(const std::vector<uint64_t>& heights) {
  // fetch blocks in binary
  monero_get_blocks_by_height_request request(heights);
  auto response = m_rpc->send_binary_request(request);
  if (response.m_binary == boost::none) throw std::runtime_error("Invalid Monero Binary response");
  boost::property_tree::ptree node;
  PyMoneroUtils::binary_blocks_to_property_tree(response.m_binary.get(), node);
  check_response_status(node);
  std::vector<std::shared_ptr<monero::monero_block>> blocks;
  PyMoneroBlock::from_property_tree(node, heights, blocks);
  return blocks;
}

std::vector<std::shared_ptr<monero::monero_block>> monero_daemon_rpc::get_blocks_by_range(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height) {
  if (start_height == boost::none) {
    start_height = 0;
  }
  if (end_height == boost::none) {
    end_height = get_height() - 1;
  }

  std::vector<uint64_t> heights;
  for (uint64_t height = start_height.get(); height <= end_height.get(); height++) heights.push_back(height);

  return get_blocks_by_height(heights);
}

std::vector<std::shared_ptr<monero::monero_block>> monero_daemon_rpc::get_blocks_by_range_chunked(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height, boost::optional<uint64_t> max_chunk_size) {
  if (start_height == boost::none) start_height = 0;
  if (end_height == boost::none) end_height = get_height() - 1;
  uint64_t from_height = start_height.get();
  bool from_zero = from_height == 0;
  uint64_t last_height = (!from_zero) ? from_height - 1 : from_height;
  std::vector<std::shared_ptr<monero::monero_block>> blocks;
  while (last_height < end_height) {
    uint64_t height_to_get = last_height + 1;
    if (from_zero) {
      height_to_get = 0;
      from_zero = false;
    }
    auto max_blocks = get_max_blocks(height_to_get, end_height, max_chunk_size);
    if (!max_blocks.empty()) blocks.insert(blocks.end(), max_blocks.begin(), max_blocks.end());
    last_height = blocks[blocks.size() - 1]->m_height.get();
  }
  return blocks;
}

std::vector<std::shared_ptr<monero::monero_block>> monero_daemon_rpc::get_max_blocks(boost::optional<uint64_t> start_height, boost::optional<uint64_t> max_height, boost::optional<uint64_t> chunk_size) {
  if (start_height == boost::none) start_height = 0;
  if (max_height == boost::none) max_height = get_height() - 1;
  if (chunk_size == boost::none) chunk_size = MAX_REQ_SIZE;

  // determine end height to fetch
  uint64_t req_size = 0;
  uint64_t from_height = start_height.get();
  bool from_zero = from_height == 0;
  uint64_t end_height = (!from_zero) ? from_height - 1 : 0;

  while (req_size < chunk_size && end_height < max_height) {
    // get header of next block
    uint64_t height_to_get = end_height + 1;
    if (from_zero) {
      height_to_get = 0;
      from_zero = false;
    }
    auto header = get_block_header_by_height_cached(height_to_get, max_height.get());
    uint64_t header_size = header->m_size.get();
    // block cannot be bigger than max request size
    if (header_size > chunk_size) throw std::runtime_error("Block exceeds maximum request size: " + std::to_string(header_size));

    // done iterating if fetching block would exceed max request size
    if (req_size + header_size > chunk_size) break;

    // otherwise block is included
    req_size += header_size;
    end_height++;
  }

  if (end_height >= start_height) {
    return get_blocks_by_range(start_height, end_height);
  }

  return std::vector<std::shared_ptr<monero::monero_block>>();
}

std::vector<std::string> monero_daemon_rpc::get_block_hashes(const std::vector<std::string>& block_hashes, uint64_t start_height) {
  throw std::runtime_error("monero_daemon_rpc::get_block_hashes(): not implemented");
}

std::vector<std::shared_ptr<monero::monero_tx>> monero_daemon_rpc::get_txs(const std::vector<std::string>& tx_hashes, bool prune) {
  MTRACE("monero_daemon_rpc::get_txs()");
  if (tx_hashes.empty()) throw std::runtime_error("Must provide an array of transaction hashes");
  auto params = std::make_shared<monero_get_txs_params>(tx_hashes, prune);
  auto res = m_rpc->send_path_request("get_transactions", params);
  try { check_response_status(res); }
  catch (const std::exception& ex) {
    if (std::string(ex.what()).find("Failed to parse hex representation of transaction hash") != std::string::npos) {
      throw std::runtime_error("Invalid transaction hash");
    }
    throw;
  }
  std::vector<std::shared_ptr<monero::monero_tx>> txs;
  PyMoneroTx::from_property_tree(res, txs);
  return txs;
}

std::vector<std::string> monero_daemon_rpc::get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune) {
  MTRACE("monero_daemon_rpc::get_tx_hexes()");
  std::vector<std::string> hexes;
  for(const auto& tx : get_txs(tx_hashes, prune)) {
    // tx may be pruned regardless of configuration
    if (tx->m_pruned_hex == boost::none) {
      if (tx->m_full_hex == boost::none) throw std::runtime_error("Tx has no hex");
      hexes.push_back(tx->m_full_hex.get());
    } else {
      hexes.push_back(tx->m_pruned_hex.get());
    }
  }
  return hexes;
}

std::shared_ptr<monero_miner_tx_sum> monero_daemon_rpc::get_miner_tx_sum(uint64_t height, uint64_t num_blocks) {
  auto params = std::make_shared<monero_get_miner_tx_sum_params>(height, num_blocks);
  auto res = m_rpc->send_json_request("get_coinbase_tx_sum", params);
  check_response_status(res);
  auto sum = std::make_shared<monero_miner_tx_sum>();
  monero_miner_tx_sum::from_property_tree(res, sum);
  return sum;
}

std::shared_ptr<monero_fee_estimate> monero_daemon_rpc::get_fee_estimate(uint64_t grace_blocks) {
  auto params = std::make_shared<monero_get_fee_estimate_params>(grace_blocks);
  auto res = m_rpc->send_json_request("get_fee_estimate", params);
  check_response_status(res);
  auto estimate = std::make_shared<monero_fee_estimate>();
  monero_fee_estimate::from_property_tree(res, estimate);
  return estimate;
}

std::shared_ptr<monero_submit_tx_result> monero_daemon_rpc::submit_tx_hex(const std::string& tx_hex, bool do_not_relay) {
  MTRACE("monero_daemon_rpc::submit_tx_hex()");
  auto params = std::make_shared<monero_submit_tx_params>(tx_hex, do_not_relay);
  auto res = m_rpc->send_path_request("send_raw_transaction", params);
  auto sum = std::make_shared<monero_submit_tx_result>();
  monero_submit_tx_result::from_property_tree(res, sum);

  // set m_is_good based on status
  try {
    check_response_status(res);
    sum->m_is_good = true;
  } catch (...) {
    sum->m_is_good = false;
  }
  return sum;
}

void monero_daemon_rpc::relay_txs_by_hash(const std::vector<std::string>& tx_hashes) {
  MTRACE("monero_daemon_rpc::relay_txs_by_hash()");
  auto params = std::make_shared<monero_submit_tx_params>(tx_hashes);
  auto res = m_rpc->send_json_request("relay_tx", params);
  check_response_status(res);
}

std::shared_ptr<monero_tx_pool_stats> monero_daemon_rpc::get_tx_pool_stats() {
  auto res = m_rpc->send_path_request("get_transaction_pool_stats");
  check_response_status(res);
  auto stats = std::make_shared<monero_tx_pool_stats>();
  monero_tx_pool_stats::from_property_tree(res, stats);
  return stats;
}

std::vector<std::shared_ptr<monero::monero_tx>> monero_daemon_rpc::get_tx_pool() {
  auto res = m_rpc->send_path_request("get_transaction_pool");
  check_response_status(res);
  std::vector<std::shared_ptr<monero::monero_tx>> pool;
  PyMoneroTx::from_property_tree(res, pool);
  return pool;
}

std::vector<std::string> monero_daemon_rpc::get_tx_pool_hashes() {
  auto res = m_rpc->send_path_request("get_transaction_pool_hashes");
  check_response_status(res);
  std::vector<std::string> tx_hashes;
  PyMoneroTx::from_property_tree(res, tx_hashes);
  return tx_hashes;
}

void monero_daemon_rpc::flush_tx_pool(const std::vector<std::string> &hashes) {
  MTRACE("monero_daemon_rpc::flush_tx_pool()");
  auto params = std::make_shared<monero_submit_tx_params>(hashes);
  auto res = m_rpc->send_json_request("flush_txpool", params);
  check_response_status(res);
}

void monero_daemon_rpc::flush_tx_pool() {
  std::vector<std::string> hashes;
  flush_tx_pool(hashes);
}

void monero_daemon_rpc::flush_tx_pool(const std::string &hash) {
  std::vector<std::string> hashes;
  hashes.push_back(hash);
  flush_tx_pool(hashes);
}

std::vector<monero_key_image_spent_status> monero_daemon_rpc::get_key_image_spent_statuses(const std::vector<std::string>& key_images) {
  if (key_images.empty()) throw std::runtime_error("Must provide key images to check the status of");
  auto params = std::make_shared<monero_is_key_image_spent_params>(key_images);
  auto res = m_rpc->send_path_request("is_key_image_spent", params);
  check_response_status(res);
  std::vector<monero_key_image_spent_status> statuses;
  for (auto it = res.begin(); it != res.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("spent_status")) {
      auto spent_status_node = it->second;
      for (auto it2 = spent_status_node.begin(); it2 != spent_status_node.end(); ++it2) {
        auto value = it2->second.get_value<uint8_t>();
        if (value == 0) {
          statuses.push_back(monero_key_image_spent_status::NOT_SPENT);
        }
        else if (value == 1) {
          statuses.push_back(monero_key_image_spent_status::CONFIRMED);
        }
        else if (value == 2) {
          statuses.push_back(monero_key_image_spent_status::TX_POOL);
        }
      }
    }
  }
  return statuses;
}

std::vector<std::shared_ptr<monero::monero_output>> monero_daemon_rpc::get_outputs(const std::vector<monero::monero_output>& outputs) {
  throw std::runtime_error("monero_daemon_rpc::get_outputs(): not implemented");
}

std::vector<std::shared_ptr<monero_output_histogram_entry>> monero_daemon_rpc::get_output_histogram(const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) {
  MTRACE("monero_daemon_rpc::get_output_histogram()");

  auto params = std::make_shared<monero_get_output_histogram_params>(amounts, min_count, max_count, is_unlocked, recent_cutoff);
  auto res = m_rpc->send_json_request("get_output_histogram", params);
  check_response_status(res);
  std::vector<std::shared_ptr<monero_output_histogram_entry>> entries;
  monero_output_histogram_entry::from_property_tree(res, entries);
  return entries;
}

std::shared_ptr<monero_daemon_info> monero_daemon_rpc::get_info() {
  auto res = m_rpc->send_json_request("get_info");
  check_response_status(res);
  std::shared_ptr<monero_daemon_info> info = std::make_shared<monero_daemon_info>();
  monero_daemon_info::from_property_tree(res, info);
  return info;
}

std::shared_ptr<monero_daemon_sync_info> monero_daemon_rpc::get_sync_info() {
  auto res = m_rpc->send_json_request("sync_info");
  check_response_status(res);
  std::shared_ptr<monero_daemon_sync_info> info = std::make_shared<monero_daemon_sync_info>();
  monero_daemon_sync_info::from_property_tree(res, info);
  return info;
}

std::shared_ptr<monero_hard_fork_info> monero_daemon_rpc::get_hard_fork_info() {
  auto res = m_rpc->send_json_request("hard_fork_info");
  check_response_status(res);
  std::shared_ptr<monero_hard_fork_info> info = std::make_shared<monero_hard_fork_info>();
  monero_hard_fork_info::from_property_tree(res, info);
  return info;
}

std::vector<std::shared_ptr<monero_alt_chain>> monero_daemon_rpc::get_alt_chains() {
  std::vector<std::shared_ptr<monero_alt_chain>> result;
  auto res = m_rpc->send_json_request("get_alternate_chains");
  check_response_status(res);
  for (boost::property_tree::ptree::const_iterator it = res.begin(); it != res.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("chains")) {
      boost::property_tree::ptree chains = it->second;
      for (boost::property_tree::ptree::const_iterator it2 = chains.begin(); it2 != chains.end(); ++it2) {
        std::shared_ptr<monero_alt_chain> alt_chain = std::make_shared<monero_alt_chain>();
        monero_alt_chain::from_property_tree(it2->second, alt_chain);
        result.push_back(alt_chain);
      }
    }
  }

  return result;
}

std::vector<std::string> monero_daemon_rpc::get_alt_block_hashes() {
  auto res = m_rpc->send_path_request("get_alt_blocks_hashes");
  check_response_status(res);
  std::vector<std::string> hashes;
  monero_get_block_result::from_property_tree(res, hashes);
  return hashes;
}

int monero_daemon_rpc::get_download_limit() {
  MTRACE("monero_daemon_rpc::get_download_limit()");
  auto limits = get_bandwidth_limits();
  if (limits->m_down != boost::none) return limits->m_down.get();
  throw std::runtime_error("Could not get download limit");
}

int monero_daemon_rpc::set_download_limit(int limit) {
  MTRACE("monero_daemon_rpc::set_download_limit()");
  if (limit == -1) return reset_download_limit();
  if (limit <= 0) throw std::runtime_error("Download limit must be an integer greater than 0");
  auto res = set_bandwidth_limits(0, limit);
  if (res->m_down != boost::none) return res->m_down.get();
  throw std::runtime_error("Could not set download limit");
}

int monero_daemon_rpc::reset_download_limit() {
  MTRACE("monero_daemon_rpc::reset_download_limit()");
  auto res = set_bandwidth_limits(0, -1);
  if (res->m_down != boost::none) return res->m_down.get();
  throw std::runtime_error("Could not set download limit");
}

int monero_daemon_rpc::get_upload_limit() {
  MTRACE("monero_daemon_rpc::get_upload_limit()");
  auto limits = get_bandwidth_limits();
  if (limits->m_up != boost::none) return limits->m_up.get();
  throw std::runtime_error("Could not get upload limit");
}

int monero_daemon_rpc::set_upload_limit(int limit) {
  MTRACE("monero_daemon_rpc::set_upload_limit()");
  if (limit == -1) return reset_upload_limit();
  if (limit <= 0) throw std::runtime_error("Upload limit must be an integer greater than 0");
  auto res = set_bandwidth_limits(limit, 0);
  if (res->m_up != boost::none) return res->m_up.get();
  throw std::runtime_error("Could not set download limit");
}

int monero_daemon_rpc::reset_upload_limit() {
  MTRACE("monero_daemon_rpc::reset_upload_limit()");
  auto res = set_bandwidth_limits(-1, 0);
  if (res->m_up != boost::none) return res->m_up.get();
  throw std::runtime_error("Could not set download limit");
}

std::vector<std::shared_ptr<monero_peer>> monero_daemon_rpc::get_peers() {
  auto res = m_rpc->send_json_request("get_connections");
  check_response_status(res);
  std::vector<std::shared_ptr<monero_peer>> peers;
  monero_peer::from_property_tree(res, peers);
  return peers;
}

std::vector<std::shared_ptr<monero_peer>> monero_daemon_rpc::get_known_peers() {
  auto res = m_rpc->send_path_request("get_peer_list");
  check_response_status(res);
  std::vector<std::shared_ptr<monero_peer>> peers;
  monero_peer::from_property_tree(res, peers);
  return peers;
}

void monero_daemon_rpc::set_outgoing_peer_limit(int limit) {
  MTRACE("monero_daemon_rpc::set_outgoing_peer_limit()");
  if (limit < 0) throw std::runtime_error("Outgoing peer limit must be >= 0");
  auto params = std::make_shared<monero_peer_limits_params>();
  params->m_out_peers = limit;
  auto res = m_rpc->send_path_request("out_peers", params);
  check_response_status(res);
}

void monero_daemon_rpc::set_incoming_peer_limit(int limit) {
  MTRACE("monero_daemon_rpc::set_incoming_peer_limit()");
  if (limit < 0) throw std::runtime_error("Incoming peer limit must be >= 0");
  auto params = std::make_shared<monero_peer_limits_params>();
  params->m_in_peers = limit;
  auto res = m_rpc->send_path_request("in_peers", params);
  check_response_status(res);
}

std::vector<std::shared_ptr<monero_ban>> monero_daemon_rpc::get_peer_bans() {
  MTRACE("monero_daemon_rpc::get_peer_bans()");
  auto res = m_rpc->send_json_request("get_bans");
  check_response_status(res);
  std::vector<std::shared_ptr<monero_ban>> bans;
  monero_ban::from_property_tree(res, bans);
  return bans;
}

void monero_daemon_rpc::set_peer_bans(const std::vector<std::shared_ptr<monero_ban>>& bans) {
  MTRACE("monero_daemon_rpc::set_peer_bans()");
  auto params = std::make_shared<monero_set_bans_params>(bans);
  auto res = m_rpc->send_json_request("set_bans", params);
  check_response_status(res);
}

void monero_daemon_rpc::start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) {
  MTRACE("monero_daemon_rpc::start_mining()");
  if (address.empty()) throw std::runtime_error("Must provide address to mine to");
  if (num_threads <= 0) throw std::runtime_error("Number of threads must be an integer greater than 0");
  auto params = std::make_shared<monero_start_mining_params>(address, num_threads, is_background, ignore_battery);
  auto res = m_rpc->send_path_request("start_mining", params);
  check_response_status(res);
}

void monero_daemon_rpc::stop_mining() {
  MTRACE("monero_daemon_rpc::stop_mining()");
  auto res = m_rpc->send_path_request("stop_mining");
  check_response_status(res);
}

std::shared_ptr<monero_mining_status> monero_daemon_rpc::get_mining_status() {
  MTRACE("monero_daemon_rpc::get_mining_status()");
  auto res = m_rpc->send_path_request("mining_status");
  check_response_status(res);
  auto result = std::make_shared<monero_mining_status>();
  monero_mining_status::from_property_tree(res, result);
  return result;
}

void monero_daemon_rpc::submit_blocks(const std::vector<std::string>& block_blobs) {
  MTRACE("monero_daemon_rpc::submit_blocks()");
  if (block_blobs.empty()) throw std::runtime_error("Must provide an array of mined block blobs to submit");
  auto params = std::make_shared<monero_submit_blocks_params>(block_blobs);
  auto res = m_rpc->send_json_request("submit_block", params);
  check_response_status(res);
}

std::shared_ptr<monero_prune_result> monero_daemon_rpc::prune_blockchain(bool check) {
  MTRACE("monero_daemon_rpc::prune_blockchain()");
  auto params = std::make_shared<monero_prune_blockchain_params>(check);
  auto res = m_rpc->send_json_request("prune_blockchain", params);
  check_response_status(res);
  std::shared_ptr<monero_prune_result> result = std::make_shared<monero_prune_result>();
  monero_prune_result::from_property_tree(res, result);
  return result;
}

std::shared_ptr<monero_daemon_update_check_result> monero_daemon_rpc::check_for_update() {
  MTRACE("monero_daemon_rpc::check_for_update()");
  auto params = std::make_shared<monero_download_update_params>("check");
  auto res = m_rpc->send_path_request("update", params);
  check_response_status(res);
  auto result = std::make_shared<monero_daemon_update_check_result>();
  monero_daemon_update_check_result::from_property_tree(res, result);
  return result;
}

std::shared_ptr<monero_daemon_update_download_result> monero_daemon_rpc::download_update(const std::string& path) {
  MTRACE("monero_daemon_rpc::download_update()");
  auto params = std::make_shared<monero_download_update_params>("download", path);
  auto res = m_rpc->send_path_request("update", params);
  check_response_status(res);
  auto result = std::make_shared<monero_daemon_update_download_result>();
  monero_daemon_update_download_result::from_property_tree(res, result);
  return result;
}

void monero_daemon_rpc::stop() {
  MTRACE("monero_daemon_rpc::stop()");
  auto res = m_rpc->send_path_request("stop_daemon");
  check_response_status(res);
}

std::shared_ptr<monero::monero_block_header> monero_daemon_rpc::wait_for_next_block_header() {
  MTRACE("monero_daemon_rpc::wait_for_next_block_header()");

  // use mutex and condition variable with predicate to wait for block
  boost::mutex temp;
  boost::condition_variable cv;
  bool ready = false;

  // create listener which notifies condition variable when block is added
  auto block_listener = std::make_shared<block_notifier>(&temp, &cv, &ready);

  // register the listener
  add_listener(block_listener);

  // wait until condition variable is notified
  boost::mutex::scoped_lock lock(temp);
  cv.wait(lock, [&]() { return ready; });

  // unregister the listener
  remove_listener(block_listener);

  // return last height
  return block_listener->m_last_header;
}

std::shared_ptr<monero_bandwidth_limits> monero_daemon_rpc::get_bandwidth_limits() {
  MTRACE("monero_daemon_rpc::get_bandwidth_limits()");
  auto res = m_rpc->send_path_request("get_limit");
  check_response_status(res);
  auto limits = std::make_shared<monero_bandwidth_limits>();
  monero_bandwidth_limits::from_property_tree(res, limits);
  return limits;
}

std::shared_ptr<monero_bandwidth_limits> monero_daemon_rpc::set_bandwidth_limits(int up, int down) {
  MTRACE("monero_daemon_rpc::set_bandwidth_limits()");
  auto limits = std::make_shared<monero_bandwidth_limits>(up, down);
  auto res = m_rpc->send_path_request("set_limit", limits);
  check_response_status(res);
  monero_bandwidth_limits::from_property_tree(res, limits);
  return limits;
}

void monero_daemon_rpc::refresh_listening() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  if (!m_poller && m_listeners.size() > 0) {
    m_poller = std::make_shared<monero_daemon_poller>(this);
  }
  if (m_poller) m_poller->set_is_polling(m_listeners.size() > 0);
}

void monero_daemon_rpc::check_response_status(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("status")) {
      std::string status = it->second.data();

      // TODO monero-project empty string status is returned for download update response when an update is available
      if (status == std::string("OK") || status == std::string("")) {
        return;
      }
      else throw monero_rpc_error(status);
    }
  }

  throw std::runtime_error("Could not get JSON RPC response status");
}

monero_daemon_rpc::~monero_daemon_rpc() {
  MTRACE("~monero_daemon_rpc()");
  remove_listeners();
}
