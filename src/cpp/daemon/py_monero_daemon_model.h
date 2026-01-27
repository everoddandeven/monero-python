#pragma once

#include "common/py_monero_common.h"

enum PyMoneroKeyImageSpentStatus : uint8_t {
  NOT_SPENT = 0,
  CONFIRMED,
  TX_POOL
};

class PyMoneroBlockHeader : public monero::monero_block_header {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block_header>& header);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_block_header>>& headers);
};

class PyMoneroBlock : public PyMoneroBlockHeader {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block>& block);
  static void from_property_tree(const boost::property_tree::ptree& node, const std::vector<uint64_t>& heights, std::vector<std::shared_ptr<monero::monero_block>>& blocks);
};

class PyMoneroOutput : public monero::monero_output {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output>& output);
};

class PyMoneroTx : public monero::monero_tx {
public:
  inline static const std::string DEFAULT_ID = "0000000000000000000000000000000000000000000000000000000000000000";

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx>& tx);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_tx>>& txs);
};

class PyMoneroTxHashes {
public:
  static std::vector<std::string> from_property_tree(const boost::property_tree::ptree& node);
};

// #region JSON-RPC

class PyMoneroDownloadUpdateParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_command;
  boost::optional<std::string> m_path;

  PyMoneroDownloadUpdateParams() {
    m_command = "download";
  }

  PyMoneroDownloadUpdateParams(std::string path) {
    m_command = "download";
    m_path = m_path;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroCheckUpdateParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_command;

  PyMoneroCheckUpdateParams() {
    m_command = "check";
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroStartMiningParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<int> m_num_threads;
  boost::optional<bool> m_is_background;
  boost::optional<bool> m_ignore_battery;

  PyMoneroStartMiningParams() {}

  PyMoneroStartMiningParams(std::string address, int num_threads, bool is_background, bool ignore_battery) {
    m_address = address;
    m_num_threads = num_threads;
    m_is_background = is_background;
    m_ignore_battery = ignore_battery;
  }

  PyMoneroStartMiningParams(int num_threads, bool is_background, bool ignore_battery) {
    m_num_threads = num_threads;
    m_is_background = is_background;
    m_ignore_battery = ignore_battery;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroPruneBlockchainParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_check;

  PyMoneroPruneBlockchainParams(bool check = true) {
    m_check = check;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSubmitBlocksParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_block_blobs;

  PyMoneroSubmitBlocksParams() { }
  PyMoneroSubmitBlocksParams(const std::vector<std::string>& block_blobs) {
    m_block_blobs = block_blobs;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetBlockParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_hash;
  boost::optional<bool> m_fill_pow_hash;

  PyMoneroGetBlockParams(uint64_t height, bool fill_pow_hash = false) {
    m_height = height;
    m_fill_pow_hash = fill_pow_hash;
  }

  PyMoneroGetBlockParams(std::string hash, bool fill_pow_hash = false) {
    m_hash = hash;
    m_fill_pow_hash = fill_pow_hash;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetBlockRangeParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_start_height;
  boost::optional<uint64_t> m_end_height;

  PyMoneroGetBlockRangeParams() { }

  PyMoneroGetBlockRangeParams(uint64_t start_height, uint64_t end_height) {
    m_start_height = start_height;
    m_end_height = end_height;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetBlockHashParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_height;

  PyMoneroGetBlockHashParams() {}

  PyMoneroGetBlockHashParams(uint64_t height) {
    m_height = height;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetBlockTemplateParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_wallet_address;
  boost::optional<int> m_reserve_size;

  PyMoneroGetBlockTemplateParams() { }
  
  PyMoneroGetBlockTemplateParams(std::string wallet_address) {
    m_wallet_address = wallet_address;
  }

  PyMoneroGetBlockTemplateParams(std::string wallet_address, int reserve_size) {
    m_wallet_address = wallet_address;
    m_reserve_size = reserve_size;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetBlocksByHeightRequest : public PyMoneroBinaryRequest {
public:
  std::vector<uint64_t> m_heights;

  PyMoneroGetBlocksByHeightRequest(const std::vector<uint64_t>& heights) {
    m_method = "get_blocks_by_height.bin";
    m_heights = heights;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroVersion : public monero::monero_version {
public:
  PyMoneroVersion() {}

  PyMoneroVersion(uint32_t number, bool is_release) {
    m_number = number;
    m_is_release = is_release;
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroVersion>& version);
};

class PyMoneroAltChain {
public:
  std::vector<std::string> m_block_hashes;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_length;
  boost::optional<std::string> m_main_chain_parent_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAltChain>& alt_chain);
};

class PyMoneroGetBlockCountResult {
public:
  boost::optional<uint64_t> m_count;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBlockCountResult>& result);
};

class PyMoneroBan : public PySerializableStruct {
public:
  boost::optional<std::string> m_host;
  boost::optional<int> m_ip;
  boost::optional<bool> m_is_banned;
  boost::optional<uint64_t> m_seconds;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBan>& ban);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroBan>>& bans);
};

class PyMoneroPruneResult {
public:
  boost::optional<bool> m_is_pruned;
  boost::optional<int> m_pruning_seed;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPruneResult>& result);
};

class PyMoneroMiningStatus {
public:
  boost::optional<bool> m_is_active;
  boost::optional<bool> m_is_background;
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_speed;
  boost::optional<int> m_num_threads;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMiningStatus>& status);
};

class PyMoneroMinerTxSum {
public:
  boost::optional<uint64_t> m_emission_sum;
  boost::optional<uint64_t> m_fee_sum;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMinerTxSum>& sum);
};

class PyMoneroBlockTemplate {
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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBlockTemplate>& tmplt);
};

class PyMoneroConnectionSpan {
public:
  boost::optional<std::string> m_connection_id;
  boost::optional<uint64_t> m_num_blocks;
  boost::optional<std::string> m_remote_address;
  boost::optional<uint64_t> m_rate;
  boost::optional<uint64_t> m_speed;
  boost::optional<uint64_t> m_size;
  boost::optional<uint64_t> m_start_height;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroConnectionSpan>& span);
};

class PyMoneroPeer {
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
  boost::optional<PyMoneroConnectionType> m_connection_type;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPeer>& peer);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroPeer>>& peers);
};

class PyMoneroSubmitTxResult {
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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroSubmitTxResult>& result);
};

class PyMoneroSubmitTxParams : public PyMoneroRequestParams {
public:
  boost::optional<std::string> m_tx_hex;
  boost::optional<bool> m_do_not_relay;

  PyMoneroSubmitTxParams() {}
  PyMoneroSubmitTxParams(std::string tx_hex, bool do_not_relay) {
    m_tx_hex = tx_hex;
    m_do_not_relay = do_not_relay;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroRelayTxParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;

  PyMoneroRelayTxParams() {}
  PyMoneroRelayTxParams(const std::vector<std::string> tx_hashes) {
    m_tx_hashes = tx_hashes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroTxBacklogEntry {
  // TODO
};

class PyMoneroOutputDistributionEntry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<int> m_base;
  std::vector<int> m_distribution;
  boost::optional<uint64_t> m_start_height;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputDistributionEntry>& entry);
};

class PyMoneroOutputHistogramEntry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<uint64_t> m_num_instances;
  boost::optional<uint64_t> m_unlocked_instances;
  boost::optional<uint64_t> m_recent_instances;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputHistogramEntry>& entry);
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>>& entries);
};

class PyMoneroTxPoolStats {
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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroTxPoolStats>& stats);
};

class PyMoneroDaemonUpdateCheckResult {
public:
  boost::optional<bool> m_is_update_available;
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_hash;
  boost::optional<std::string> m_auto_uri;
  boost::optional<std::string> m_user_uri;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateCheckResult>& check);
};

class PyMoneroDaemonUpdateDownloadResult : public PyMoneroDaemonUpdateCheckResult {
public:
  boost::optional<std::string> m_download_path;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateDownloadResult>& check);
};

class PyMoneroFeeEstimate {
public:
  boost::optional<uint64_t> m_fee;
  std::vector<uint64_t> m_fees;
  boost::optional<uint64_t> m_quantization_mask;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroFeeEstimate>& estimate);
};

class PyMoneroDaemonInfo {
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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonInfo>& info);
};

class PyMoneroDaemonSyncInfo {
public:
  boost::optional<uint64_t> m_height;
  std::vector<PyMoneroPeer> m_peers;
  std::vector<PyMoneroConnectionSpan> m_spans;
  boost::optional<uint64_t> m_target_height;
  boost::optional<int> m_next_needed_pruning_seed;
  boost::optional<std::string> m_overview;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonSyncInfo>& info);
};

class PyMoneroHardForkInfo {
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

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroHardForkInfo>& info);
};

class PyMoneroGetAltBlocksHashesResponse {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes);
};

class PyMoneroBandwithLimits : public PyMoneroRequestParams {
public:
  boost::optional<int> m_up;
  boost::optional<int> m_down;

  PyMoneroBandwithLimits() {}
  PyMoneroBandwithLimits(int up, int down) {
    m_up = up;
    m_down = down;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBandwithLimits>& limits);
};

class PyMoneroPeerLimits : public PyMoneroRequestParams {
public:
  boost::optional<int> m_in_peers;
  boost::optional<int> m_out_peers;

  PyMoneroPeerLimits() {}
  PyMoneroPeerLimits(int in, int out) {
    m_in_peers = in;
    m_out_peers = out;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetHeightResponse {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_untrusted;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetHeightResponse>& response);
};

class PyMoneroGetMinerTxSumParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_count;
  
  PyMoneroGetMinerTxSumParams() {}
  PyMoneroGetMinerTxSumParams(uint64_t height, uint64_t count) {
    m_height = height;
    m_count = count;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetFeeEstimateParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_grace_blocks;
  
  PyMoneroGetFeeEstimateParams(uint64_t grace_blocks = 0) {
    m_grace_blocks = grace_blocks;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroSetBansParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::shared_ptr<PyMoneroBan>> m_bans;

  PyMoneroSetBansParams() {}
  PyMoneroSetBansParams(const std::vector<std::shared_ptr<PyMoneroBan>>& bans) {
    m_bans = bans;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetTxsParams : public PyMoneroRequestParams {
public:
  std::vector<std::string> m_tx_hashes;
  boost::optional<bool> m_decode_as_json;
  boost::optional<bool> m_prune;

  PyMoneroGetTxsParams(const std::vector<std::string> &tx_hashes, bool prune, bool decode_as_json = true) {
    m_tx_hashes = tx_hashes;
    m_prune = prune;
    m_decode_as_json = decode_as_json;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroGetOutputHistrogramParams : public PyMoneroJsonRequestParams {
public:
  std::vector<uint64_t> m_amounts;
  boost::optional<int> m_min_count;
  boost::optional<int> m_max_count;
  boost::optional<bool> m_is_unlocked;
  boost::optional<int> m_recent_cutoff;

  PyMoneroGetOutputHistrogramParams(const std::vector<uint64_t> &amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) {
    m_amounts = amounts;
    m_min_count = min_count;
    m_max_count = max_count;
    m_is_unlocked = is_unlocked;
    m_recent_cutoff = recent_cutoff;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroIsKeyImageSpentParams : public PyMoneroRequestParams {
public:
  std::vector<std::string> m_key_images;

  PyMoneroIsKeyImageSpentParams(const std::vector<std::string> & key_images) {
    m_key_images = key_images;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};
