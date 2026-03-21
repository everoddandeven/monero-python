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

class PyMoneroBlockNotifier : public PyMoneroDaemonListener {
public:
  boost::mutex* temp;
  boost::condition_variable* cv;
  PyMoneroBlockNotifier(boost::mutex* temp, boost::condition_variable* cv) { this->temp = temp; this->cv = cv; }
  void on_block_header(const std::shared_ptr<monero::monero_block_header>& header) override {
    m_last_header = header;
    cv->notify_one();
  }
};

class PyMoneroDaemon {
public:
  PyMoneroDaemon() {}
  virtual void add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroDaemonListener>> get_listeners() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void remove_listeners() { throw std::runtime_error("PyMoneroDaemon::remove_listeners(): not supported"); };
  virtual monero::monero_version get_version() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual bool is_trusted() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual uint64_t get_height() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::string get_block_hash(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroBlockTemplate> get_block_template(const std::string& wallet_address) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroBlockTemplate> get_block_template(const std::string& wallet_address, int reserve_size) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> get_last_block_header() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_hash(const std::string& hash) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_height(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_height(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_height(const std::vector<uint64_t>& heights) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range_chunked(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height, boost::optional<uint64_t> max_chunk_size) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::string> get_block_hashes(const std::vector<std::string>& block_hashes, uint64_t start_height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
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
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
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
  virtual std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroMinerTxSum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroFeeEstimate> get_fee_estimate(uint64_t grace_blocks = 0) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroSubmitTxResult> submit_tx_hex(const std::string& tx_hex, bool do_not_relay = false) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void relay_tx_by_hash(const std::string& tx_hash) {
    std::vector<std::string> tx_hashes;
    tx_hashes.push_back(tx_hash);
    relay_txs_by_hash(tx_hashes);
  }
  virtual void relay_txs_by_hash(const std::vector<std::string>& tx_hashes) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_tx_pool() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::string> get_tx_pool_hashes() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<PyMoneroTxBacklogEntry> get_tx_pool_backlog() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroTxPoolStats> get_tx_pool_stats() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void flush_tx_pool() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void flush_tx_pool(const std::vector<std::string> &hashes) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void flush_tx_pool(const std::string &hash) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual PyMoneroKeyImageSpentStatus get_key_image_spent_status(const std::string& key_image) {
    std::vector<std::string> key_images;
    key_images.push_back(key_image);
    auto statuses = get_key_image_spent_statuses(key_images);
    if (statuses.empty()) throw std::runtime_error("Could not get key image spent status");
    return statuses[0];
  }
  virtual std::vector<PyMoneroKeyImageSpentStatus> get_key_image_spent_statuses(const std::vector<std::string>& key_images) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<monero::monero_output>> get_outputs(const std::vector<monero::monero_output>& outputs) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> get_output_histogram(const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputDistributionEntry>> get_output_distribution(const std::vector<uint64_t>& amounts) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputDistributionEntry>> get_output_distribution(const std::vector<uint64_t>& amounts, bool is_cumulative, uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroDaemonInfo> get_info() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroDaemonSyncInfo> get_sync_info() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroHardForkInfo> get_hard_fork_info() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() { throw std::runtime_error("PyMoneroDaemon::get_alt_chains(): not supported"); }
  virtual std::vector<std::string> get_alt_block_hashes() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual int get_download_limit() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual int set_download_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual int reset_download_limit() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual int get_upload_limit() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual int set_upload_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual int reset_upload_limit() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroPeer>> get_peers() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroPeer>> get_known_peers() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void set_outgoing_peer_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void set_incoming_peer_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::vector<std::shared_ptr<PyMoneroBan>> get_peer_bans() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void set_peer_bans(const std::vector<std::shared_ptr<PyMoneroBan>>& bans) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void set_peer_ban(const std::shared_ptr<PyMoneroBan>& ban) {
    if (ban == nullptr) throw std::runtime_error("Ban is none");
    std::vector<std::shared_ptr<PyMoneroBan>> bans;
    bans.push_back(ban);
    set_peer_bans(bans);
  }
  virtual void start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void stop_mining() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroMiningStatus> get_mining_status() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void submit_block(const std::string& block_blob) {
    std::vector<std::string> block_blobs;
    block_blobs.push_back(block_blob);
    return submit_blocks(block_blobs);
  }
  virtual void submit_blocks(const std::vector<std::string>& block_blobs) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroPruneResult> prune_blockchain(bool check) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateCheckResult> check_for_update() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update(const std::string& path) { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual void stop() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
  virtual std::shared_ptr<monero::monero_block_header> wait_for_next_block_header() { throw std::runtime_error("PyMoneroDaemon: not supported"); }
};
