#pragma once

#include "py_monero_daemon_model.h"


class monero_daemon_listener {
public:
  virtual void on_block_header(const std::shared_ptr<monero::monero_block_header> &header) {
    m_last_header = header;
  }

  std::shared_ptr<monero::monero_block_header> m_last_header;
};

class PyMoneroDaemonListener : public monero_daemon_listener {
public:
  virtual void on_block_header(const std::shared_ptr<monero::monero_block_header> &header) {
    PYBIND11_OVERRIDE(
      void,                               
      monero_daemon_listener,
      on_block_header,
      header
    );
  }
};

class PyMoneroBlockNotifier : public PyMoneroDaemonListener {
public:
  boost::mutex* temp;
  boost::condition_variable* cv;
  PyMoneroBlockNotifier(boost::mutex* temp, boost::condition_variable* cv) { this->temp = temp; this->cv = cv; }
  void on_block_header(const std::shared_ptr<monero::monero_block_header> &header) override {
    m_last_header = header;
    cv->notify_one();
  }
};

class PyMoneroDaemon {
public:
  PyMoneroDaemon() {}
  virtual void add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroDaemonListener>> get_listeners() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void remove_listeners() { throw std::runtime_error("PyMoneroDaemon::remove_listeners(): not implemented"); };
  virtual monero::monero_version get_version() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual bool is_trusted() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual uint64_t get_height() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::string get_block_hash(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address, int reserve_size) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> get_last_block_header() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_hash(const std::string& hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> get_block_header_by_height(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_height(uint64_t height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_height(const std::vector<uint64_t>& heights) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range_chunked(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height, boost::optional<uint64_t> max_chunk_size) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::string> get_block_hashes(std::vector<std::string> block_hashes, uint64_t start_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::optional<std::shared_ptr<monero::monero_tx>> get_tx(const std::string& tx_hash, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroMinerTxSum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroFeeEstimate> get_fee_estimate(uint64_t grace_blocks = 0) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroSubmitTxResult> submit_tx_hex(std::string& tx_hex, bool do_not_relay = false) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void relay_tx_by_hash(std::string& tx_hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void relay_txs_by_hash(std::vector<std::string>& tx_hashes) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_tx>> get_tx_pool() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::string> get_tx_pool_hashes() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<PyMoneroTxBacklogEntry> get_tx_pool_backlog() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroTxPoolStats> get_tx_pool_stats() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void flush_tx_pool() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void flush_tx_pool(const std::vector<std::string> &hashes) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void flush_tx_pool(const std::string &hash) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual PyMoneroKeyImageSpentStatus get_key_image_spent_status(std::string& key_image) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<PyMoneroKeyImageSpentStatus> get_key_image_spent_statuses(std::vector<std::string>& key_images) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_output>> get_outputs(std::vector<monero::monero_output>& outputs) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> get_output_histogram(std::vector<uint64_t> amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputDistributionEntry>> get_output_distribution(std::vector<uint64_t> amounts) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroOutputDistributionEntry>> get_output_distribution(std::vector<uint64_t> amounts, bool is_cumulative, uint64_t start_height, uint64_t end_height) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonInfo> get_info() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonSyncInfo> get_sync_info() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroHardForkInfo> get_hard_fork_info() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() { throw std::runtime_error("PyMoneroDaemon::get_alt_chains(): not implemented"); }
  virtual std::vector<std::string> get_alt_block_hashes() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int get_download_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int set_download_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int reset_download_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int get_upload_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int set_upload_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual int reset_upload_limit() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroPeer>> get_peers() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroPeer>> get_known_peers() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_outgoing_peer_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_incoming_peer_limit(int limit) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroBan>> get_peer_bans() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_peer_bans(const std::vector<std::shared_ptr<PyMoneroBan>>& bans) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void set_peer_ban(const std::shared_ptr<PyMoneroBan>& ban) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void stop_mining() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroMiningStatus> get_mining_status() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void submit_block(const std::string& block_blob) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void submit_blocks(const std::vector<std::string>& block_blobs) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroPruneResult> prune_blockchain(bool check) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateCheckResult> check_for_update() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update(const std::string& path) { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual void stop() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
  virtual std::shared_ptr<monero::monero_block_header> wait_for_next_block_header() { throw std::runtime_error("PyMoneroDaemon: not implemented"); }
};

class PyMoneroDaemonDefault : public PyMoneroDaemon {
public:

  std::vector<std::shared_ptr<PyMoneroDaemonListener>> get_listeners() override { return m_listeners; }
  void add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) override;
  void remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) override;
  void remove_listeners() override;
  std::optional<std::shared_ptr<monero::monero_tx>> get_tx(const std::string& tx_hash, bool prune = false) override;
  void relay_tx_by_hash(std::string& tx_hash) override;
  PyMoneroKeyImageSpentStatus get_key_image_spent_status(std::string& key_image) override;
  std::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false);
  void submit_block(const std::string& block_blob) override;
  void set_peer_ban(const std::shared_ptr<PyMoneroBan>& ban) override;

protected:
  mutable boost::recursive_mutex m_listeners_mutex;
  std::vector<std::shared_ptr<PyMoneroDaemonListener>> m_listeners;

  virtual void refresh_listening() { }
};

class PyMoneroDaemonPoller {
public:
  explicit PyMoneroDaemonPoller(PyMoneroDaemon* daemon, uint64_t poll_period_ms = 5000): m_poll_period_ms(poll_period_ms), m_is_polling(false) {
    m_daemon = daemon;
  }

  ~PyMoneroDaemonPoller();
  void set_is_polling(bool is_polling);

private:
  PyMoneroDaemon* m_daemon;
  std::shared_ptr<monero::monero_block_header> m_last_header;
  uint64_t m_poll_period_ms;
  std::atomic<bool> m_is_polling;
  std::thread m_thread;

  void loop();
  void poll();
  void announce_block_header(const std::shared_ptr<monero::monero_block_header>& header);
};


class PyMoneroDaemonRpc : public PyMoneroDaemonDefault {
public:
  PyMoneroDaemonRpc() {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroDaemonRpc(std::shared_ptr<PyMoneroRpcConnection> rpc) {
    m_rpc = rpc;
    if (!rpc->is_online() && !rpc->m_uri->empty()) rpc->check_connection();
  }

  PyMoneroDaemonRpc(const std::string& uri, const std::string& username = "", const std::string& password = "") {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
    m_rpc->m_uri = uri;
    if (!username.empty() && !password.empty()) m_rpc->set_credentials(username, password);
    if (!uri.empty()) m_rpc->check_connection();
  }

  ~PyMoneroDaemonRpc();

  std::shared_ptr<PyMoneroRpcConnection> get_rpc_connection() const;
  bool is_connected();
  monero::monero_version get_version() override;
  bool is_trusted() override;
  uint64_t get_height() override;
  std::string get_block_hash(uint64_t height) override;
  std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address, int reserve_size) override;
  std::shared_ptr<PyMoneroBlockTemplate> get_block_template(std::string& wallet_address) override;
  std::shared_ptr<monero::monero_block_header> get_last_block_header() override;
  std::shared_ptr<monero::monero_block_header> get_block_header_by_hash(const std::string& hash) override;
  std::shared_ptr<monero::monero_block_header> get_block_header_by_height(uint64_t height) override;
  std::vector<std::shared_ptr<monero::monero_block_header>> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) override;
  std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) override;
  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) override;
  std::shared_ptr<monero::monero_block> get_block_by_height(uint64_t height) override;
  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_height(const std::vector<uint64_t>& heights) override;
  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height) override;
  std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_range_chunked(boost::optional<uint64_t> start_height, boost::optional<uint64_t> end_height, boost::optional<uint64_t> max_chunk_size) override;
  std::vector<std::string> get_block_hashes(std::vector<std::string> block_hashes, uint64_t start_height) override;
  std::vector<std::shared_ptr<monero::monero_tx>> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) override;
  std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) override;
  std::shared_ptr<PyMoneroMinerTxSum> get_miner_tx_sum(uint64_t height, uint64_t num_blocks) override;
  std::shared_ptr<PyMoneroFeeEstimate> get_fee_estimate(uint64_t grace_blocks = 0) override;
  std::shared_ptr<PyMoneroSubmitTxResult> submit_tx_hex(std::string& tx_hex, bool do_not_relay = false) override;
  void relay_txs_by_hash(std::vector<std::string>& tx_hashes) override;
  std::shared_ptr<PyMoneroTxPoolStats> get_tx_pool_stats() override;
  std::vector<std::shared_ptr<monero::monero_tx>> get_tx_pool() override;
  std::vector<std::string> get_tx_pool_hashes() override;
  void flush_tx_pool(const std::vector<std::string> &hashes) override;
  void flush_tx_pool() override;
  void flush_tx_pool(const std::string &hash) override;
  std::vector<PyMoneroKeyImageSpentStatus> get_key_image_spent_statuses(std::vector<std::string>& key_images) override;
  std::vector<std::shared_ptr<monero::monero_output>> get_outputs(std::vector<monero::monero_output>& outputs) override;
  std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>> get_output_histogram(std::vector<uint64_t> amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) override;
  std::shared_ptr<PyMoneroDaemonInfo> get_info() override;
  std::shared_ptr<PyMoneroDaemonSyncInfo> get_sync_info() override;
  std::shared_ptr<PyMoneroHardForkInfo> get_hard_fork_info() override;
  std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() override;
  std::vector<std::string> get_alt_block_hashes() override;
  int get_download_limit() override;
  int set_download_limit(int limit) override;
  int reset_download_limit() override;
  int get_upload_limit() override;
  int set_upload_limit(int limit) override;
  int reset_upload_limit() override;
  std::vector<std::shared_ptr<PyMoneroPeer>> get_peers() override;
  std::vector<std::shared_ptr<PyMoneroPeer>> get_known_peers() override;
  void set_outgoing_peer_limit(int limit) override;
  void set_incoming_peer_limit(int limit) override;
  std::vector<std::shared_ptr<PyMoneroBan>> get_peer_bans() override;
  void set_peer_bans(const std::vector<std::shared_ptr<PyMoneroBan>>& bans) override;
  void start_mining(const std::string &address, int num_threads, bool is_background, bool ignore_battery) override;
  void stop_mining() override;
  std::shared_ptr<PyMoneroMiningStatus> get_mining_status() override;
  void submit_blocks(const std::vector<std::string>& block_blobs) override;
  std::shared_ptr<PyMoneroPruneResult> prune_blockchain(bool check) override;
  std::shared_ptr<PyMoneroDaemonUpdateCheckResult> check_for_update() override;
  std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update(const std::string& path) override;
  std::shared_ptr<PyMoneroDaemonUpdateDownloadResult> download_update() override;
  void stop() override;
  std::shared_ptr<monero::monero_block_header> wait_for_next_block_header();
  static void check_response_status(std::shared_ptr<PyMoneroPathResponse> response);
  static void check_response_status(std::shared_ptr<PyMoneroJsonResponse> response);

protected:
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;
  std::shared_ptr<PyMoneroDaemonPoller> m_poller;
  std::unordered_map<uint64_t, std::shared_ptr<monero::monero_block_header>> m_cached_headers;

  std::vector<std::shared_ptr<monero::monero_block>> get_max_blocks(boost::optional<uint64_t> start_height, boost::optional<uint64_t> max_height, boost::optional<uint64_t> chunk_size);
  std::shared_ptr<monero::monero_block_header> get_block_header_by_height_cached(uint64_t height, uint64_t max_height);
  std::shared_ptr<PyMoneroBandwithLimits> get_bandwidth_limits();
  std::shared_ptr<PyMoneroBandwithLimits> set_bandwidth_limits(int up, int down);
  void refresh_listening() override;
  static void check_response_status(const boost::property_tree::ptree& node);
};
