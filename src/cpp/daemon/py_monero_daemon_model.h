#pragma once

#include <boost/asio.hpp>
#include <iostream>
#include <sstream>
#include <thread>
#include <map>
#include <vector>
#include <stdexcept>
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

class PyMoneroRequestParams : public PySerializableStruct {
public:
  boost::optional<py::object> m_py_params;

  PyMoneroRequestParams() { }
  PyMoneroRequestParams(boost::optional<py::object> py_params) { m_py_params = py_params; }

  std::string serialize() const override;
  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroRequestEmptyParams : public PyMoneroRequestParams {
  public:
    PyMoneroRequestEmptyParams() {}
  
    rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
};

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

class PyMoneroJsonRequestParams : public PyMoneroRequestParams {
public:
  PyMoneroJsonRequestParams() { }
  PyMoneroJsonRequestParams(boost::optional<py::object> py_params) { m_py_params = py_params; }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroJsonRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroJsonRequestEmptyParams : public PyMoneroJsonRequestParams {
public:
  PyMoneroJsonRequestEmptyParams() {}

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
};

class PyMoneroRequest : public PySerializableStruct {
public:
  boost::optional<std::string> m_method;

  PyMoneroRequest() { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroRequest::to_rapid_json_value(): not implemented"); };
};

class PyMoneroPathRequest : public PyMoneroRequest {
public:
  boost::optional<std::shared_ptr<PyMoneroRequestParams>> m_params;

  PyMoneroPathRequest() { }
  
  PyMoneroPathRequest(std::string method, boost::optional<py::object> params = boost::none) {
    m_method = method;
    if (params != boost::none) m_params = std::make_shared<PyMoneroRequestParams>(params);
    m_params = std::make_shared<PyMoneroRequestEmptyParams>();
  }

  PyMoneroPathRequest(std::string method, std::shared_ptr<PyMoneroRequestParams> params) {
    m_method = method;
    m_params = params;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroBinaryRequest : public PyMoneroPathRequest {
public:
  PyMoneroBinaryRequest() {}

  PyMoneroBinaryRequest(std::string method, boost::optional<py::object> params = boost::none) {
    m_method = method;
    if (params != boost::none) m_params = std::make_shared<PyMoneroRequestParams>(params);
    m_params = std::make_shared<PyMoneroRequestEmptyParams>();
  }

  PyMoneroBinaryRequest(std::string method, std::shared_ptr<PyMoneroRequestParams> params) {
    m_method = method;
    m_params = params;
  }

  std::string to_binary_val() const;
};

class PyMoneroJsonRequest : public PyMoneroRequest {
public:
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_id;
  boost::optional<std::shared_ptr<PyMoneroJsonRequestParams>> m_params;

  PyMoneroJsonRequest() {
    m_version = "2.0";
    m_id = "0";
    m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
  }

  PyMoneroJsonRequest(const PyMoneroJsonRequest& request) {
    m_version = request.m_version;
    m_id = request.m_id;
    m_method = request.m_method;
    m_params = request.m_params;
  }

  PyMoneroJsonRequest(std::string method, boost::optional<py::object> params = boost::none) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    if (params != boost::none) {
      m_params = std::make_shared<PyMoneroJsonRequestParams>(params);
    }
    else m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
  }

  PyMoneroJsonRequest(std::string method, std::shared_ptr<PyMoneroJsonRequestParams> params) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    m_params = params;
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

class PyMoneroJsonResponse {
public:
  boost::optional<std::string> m_jsonrpc;
  boost::optional<std::string> m_id;
  boost::optional<boost::property_tree::ptree> m_result;

  static std::shared_ptr<PyMoneroJsonResponse> deserialize(const std::string& response_json);

  PyMoneroJsonResponse() {
    m_jsonrpc = "2.0";
    m_id = "0";
  }

  PyMoneroJsonResponse(const PyMoneroJsonResponse& response) {
    m_jsonrpc = response.m_jsonrpc;
    m_id = response.m_id;
    m_result = response.m_result;
  }

  PyMoneroJsonResponse(boost::optional<boost::property_tree::ptree> &result) {
    m_jsonrpc = "2.0";
    m_id = "0";
    m_result = result;
  }

  std::optional<py::object> get_result() const;
};

class PyMoneroPathResponse {
public:
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroPathResponse() { }

  PyMoneroPathResponse(const PyMoneroPathResponse& response) {
    m_response = response.m_response;
  }

  PyMoneroPathResponse(boost::optional<boost::property_tree::ptree> &response) {
    m_response = response;
  }

  std::optional<py::object> get_response() const;
  static std::shared_ptr<PyMoneroPathResponse> deserialize(const std::string& response_json);
};

class PyMoneroBinaryResponse {
public:
  boost::optional<std::string> m_binary;
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroBinaryResponse() {}

  PyMoneroBinaryResponse(const std::string &binary) {
    m_binary = binary;
  }

  PyMoneroBinaryResponse(const PyMoneroBinaryResponse& response) {
    m_binary = response.m_binary;
    m_response = response.m_response;
  }

  static std::shared_ptr<PyMoneroBinaryResponse> deserialize(const std::string& response_binary);
  std::optional<py::object> get_response() const;
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

class PyMoneroSetBansParams : public PyMoneroRequestParams {
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

class PyMoneroRpcConnection : public monero_rpc_connection {
public:
  boost::optional<std::string> m_zmq_uri;
  int m_priority;
  uint64_t m_timeout;
  boost::optional<long> m_response_time;

  static int compare(std::shared_ptr<PyMoneroRpcConnection> c1, std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection);

  PyMoneroRpcConnection(const std::string& uri = "", const std::string& username = "", const std::string& password = "", const std::string& proxy_uri = "", const std::string& zmq_uri = "", int priority = 0, uint64_t timeout = 0) {
    m_uri = uri;
    m_username = username; 
    m_password = password;
    m_zmq_uri = zmq_uri;
    m_priority = priority;
    m_timeout = timeout;
    m_proxy_uri = proxy_uri;
    set_credentials(username, password);
  }

  PyMoneroRpcConnection(const PyMoneroRpcConnection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_zmq_uri = rpc.m_zmq_uri;
    m_proxy_uri = rpc.m_proxy_uri;
    m_is_authenticated = rpc.m_is_authenticated;
    set_credentials(m_username.value_or(""), m_password.value_or(""));
  }

  PyMoneroRpcConnection(const monero::monero_rpc_connection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_proxy_uri = rpc.m_proxy_uri;
    set_credentials(m_username.value_or(""), m_password.value_or(""));
  }

  bool is_onion() const;
  bool is_i2p() const;
  void set_credentials(const std::string& username, const std::string& password);
  void set_attribute(const std::string& key, const std::string& val);
  std::string get_attribute(const std::string& key);
  bool is_online() const;
  bool is_authenticated() const;
  bool is_connected() const;
  bool check_connection(int timeout_ms = 2000);

  template<class t_request, class t_response>
  inline int invoke_post(const boost::string_ref uri, const t_request& request, t_response& res, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    if (!m_http_client) throw std::runtime_error("http client not set");

    rapidjson::Document document(rapidjson::Type::kObjectType);
    rapidjson::Value req = request.to_rapidjson_val(document.GetAllocator());
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    req.Accept(writer);
    std::string body = sb.GetString();

    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);

    int status_code = response->m_response_code;

    if (status_code == 200) {
      res = *t_response::deserialize(response->m_body);
    }

    return status_code;
  }

  inline const epee::net_utils::http::http_response_info* invoke_post(const boost::string_ref uri, const std::string& body, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    if (!m_http_client) throw std::runtime_error("http client not set");

    std::shared_ptr<epee::net_utils::http::http_response_info> _res = std::make_shared<epee::net_utils::http::http_response_info>();
    const epee::net_utils::http::http_response_info* response = _res.get();
    boost::lock_guard<boost::recursive_mutex> lock(m_mutex);

    if (!m_http_client->invoke_post(uri, body, timeout, &response)) throw std::runtime_error("Network error");

    return response;
  }

  inline const std::shared_ptr<PyMoneroJsonResponse> send_json_request(const PyMoneroJsonRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroJsonResponse response;

    int result = invoke_post("/json_rpc", request, response, timeout);

    if (result != 200) throw std::runtime_error("HTTP error: code " + std::to_string(result));

    return std::make_shared<PyMoneroJsonResponse>(response);
  }

  inline const std::shared_ptr<PyMoneroPathResponse> send_path_request(const PyMoneroPathRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroPathResponse response;

    if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in path request");
    int result = invoke_post(std::string("/") + request.m_method.get(), request, response, timeout);

    if (result != 200) throw std::runtime_error("HTTP error: code " + std::to_string(result));

    return std::make_shared<PyMoneroPathResponse>(response);
  }

  inline const std::shared_ptr<PyMoneroBinaryResponse> send_binary_request(const PyMoneroBinaryRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in binary request");
    if (!m_http_client) throw std::runtime_error("http client not set");

    std::string uri = std::string("/") + request.m_method.get();
    std::string body = request.to_binary_val();

    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);

    int result = response->m_response_code;

    if (result != 200) throw std::runtime_error("HTTP error: code " + std::to_string(result));

    return PyMoneroBinaryResponse::deserialize(response->m_body);
  }

  // exposed python methods

  inline std::optional<py::object> send_json_request(const std::string method, boost::optional<py::object> parameters) {
    PyMoneroJsonRequest request(method, parameters);
    auto response = send_json_request(request);

    return response->get_result();
  }

  inline std::optional<py::object> send_path_request(const std::string method, boost::optional<py::object> parameters) {
    PyMoneroPathRequest request(method, parameters);
    auto response = send_path_request(request);

    return response->get_response();
  }

  inline std::optional<py::object> send_binary_request(const std::string method, boost::optional<py::object> parameters) {
    PyMoneroBinaryRequest request(method, parameters);
    auto response = send_binary_request(request);

    return response->get_response();
  }

protected:
  mutable boost::recursive_mutex m_mutex;
  std::string m_server;
  boost::optional<epee::net_utils::http::login> m_credentials;
  std::unique_ptr<epee::net_utils::http::abstract_http_client> m_http_client;
  serializable_unordered_map<std::string, std::string> m_attributes;
  boost::optional<bool> m_is_online;
  boost::optional<bool> m_is_authenticated;
};

struct monero_connection_manager_listener {
public:
  virtual void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection) {
    throw std::runtime_error("monero_connection_manager_listener::on_connection_changed(): not implemented");
  }
};

class PyMoneroConnectionManagerListener : public monero_connection_manager_listener {
public:
  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection) override {
    PYBIND11_OVERRIDE_PURE(
      void,
      monero_connection_manager_listener,
      on_connection_changed,
      connection
    );
  }
};

class PyMoneroConnectionManager {
public:

  PyMoneroConnectionManager() { }

  PyMoneroConnectionManager(const PyMoneroConnectionManager &connection_manager) {
    m_listeners = connection_manager.get_listeners();
    m_connections = connection_manager.get_connections();
    m_current_connection = connection_manager.get_connection();
    m_auto_switch = connection_manager.get_auto_switch();
    m_timeout = connection_manager.get_timeout();
  }

  void add_listener(const std::shared_ptr<monero_connection_manager_listener> &listener);
  void remove_listener(const std::shared_ptr<monero_connection_manager_listener> &listener);
  void remove_listeners();
  std::vector<std::shared_ptr<monero_connection_manager_listener>> get_listeners() const;
  std::shared_ptr<PyMoneroRpcConnection> get_connection_by_uri(const std::string &uri);
  void add_connection(std::shared_ptr<PyMoneroRpcConnection> connection);
  void add_connection(const std::string &uri);
  void remove_connection(const std::string &uri);
  void set_connection(std::shared_ptr<PyMoneroRpcConnection> connection);
  void set_connection(const std::string& uri);
  bool has_connection(const std::string& uri);
  std::shared_ptr<PyMoneroRpcConnection> get_connection() const { return m_current_connection; }
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_connections() const { return m_connections; }
  bool get_auto_switch() const { return m_auto_switch; }
  void set_timeout(uint64_t timeout_ms) { m_timeout = timeout_ms; }
  uint64_t get_timeout() const { return m_timeout; }
  bool is_connected() const;
  void check_connection();
  void set_auto_switch(bool auto_switch);
  void stop_polling();
  void start_polling(std::optional<uint64_t> period_ms, std::optional<bool> auto_switch, std::optional<uint64_t> timeout_ms, std::optional<PyMoneroConnectionPollType> poll_type, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> &excluded_connections);
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_peer_connections() const { throw std::runtime_error("PyMoneroConnectionManager::get_peer_connections(): not implemented"); }
  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {});
  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(std::shared_ptr<PyMoneroRpcConnection>& excluded_connection);
  void check_connections();
  void disconnect();
  void clear();
  void reset();

private:
  // static variables
  inline static const uint64_t DEFAULT_TIMEOUT = 5000;
  inline static const uint64_t DEFAULT_POLL_PERIOD = 20000;
  inline static const bool DEFAULT_AUTO_SWITCH = true;
  inline static const int MIN_BETTER_RESPONSES = 3;
  mutable boost::recursive_mutex m_listeners_mutex;
  mutable boost::recursive_mutex m_connections_mutex;
  std::vector<std::shared_ptr<monero_connection_manager_listener>> m_listeners;
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> m_connections;
  std::shared_ptr<PyMoneroRpcConnection> m_current_connection;
  bool m_auto_switch = true;
  uint64_t m_timeout = 5000;
  std::map<std::shared_ptr<PyMoneroRpcConnection>, std::vector<boost::optional<long>>> m_response_times;
  bool m_is_polling = false;
  std::thread m_thread;

  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection);
  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> get_connections_in_ascending_priority();
  void start_polling_connection(uint64_t period_ms);
  void start_polling_connections(uint64_t period_ms);
  void start_polling_prioritized_connections(uint64_t period_ms, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections);
  bool check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {});
  void check_prioritized_connections(std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections);
  std::shared_ptr<PyMoneroRpcConnection> process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses);
  std::shared_ptr<PyMoneroRpcConnection> get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses);
  std::shared_ptr<PyMoneroRpcConnection> update_best_connection_in_priority();
};
