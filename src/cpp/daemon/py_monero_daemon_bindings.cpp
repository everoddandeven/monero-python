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
#include "py_monero_types.h"

void py_monero_bind_daemon(py::module_& m, PyMoneroTypes& t) {
  // monero_fee_estimate
  py::class_<monero_fee_estimate, serializable_struct, std::shared_ptr<monero_fee_estimate>>(m, "MoneroFeeEstimate")
    .def(py::init<>())
    .def_readwrite("fee", &monero_fee_estimate::m_fee)
    .def_readwrite("fees", &monero_fee_estimate::m_fees)
    .def_readwrite("quantization_mask", &monero_fee_estimate::m_quantization_mask);

  // monero_tx_backlog_entry
  py::class_<monero_tx_backlog_entry, std::shared_ptr<monero_tx_backlog_entry>>(m, "MoneroTxBacklogEntry")
    .def(py::init<>());

  // monero_version
  t.py_monero_version
    .def(py::init<>())
    .def_readwrite("number", &monero_version::m_number)
    .def_readwrite("is_release", &monero_version::m_is_release);

  // monero_block_header
  t.py_monero_block_header
    .def(py::init<>())
    .def("__str__", &monero_block_header::serialize)
    .def_readwrite("hash", &monero_block_header::m_hash)
    .def_readwrite("height", &monero_block_header::m_height)
    .def_readwrite("timestamp", &monero_block_header::m_timestamp)
    .def_readwrite("size", &monero_block_header::m_size)
    .def_readwrite("weight", &monero_block_header::m_weight)
    .def_readwrite("long_term_weight", &monero_block_header::m_long_term_weight)
    .def_readwrite("depth", &monero_block_header::m_depth)
    .def_readwrite("difficulty_high", &monero_block_header::m_difficulty_high)
    .def_readwrite("difficulty_low", &monero_block_header::m_difficulty_low)
    .def_readwrite("cumulative_difficulty_high", &monero_block_header::m_cumulative_difficulty_high)
    .def_readwrite("cumulative_difficulty_low", &monero_block_header::m_cumulative_difficulty_low)
    .def_readwrite("major_version", &monero_block_header::m_major_version)
    .def_readwrite("minor_version", &monero_block_header::m_minor_version)
    .def_readwrite("nonce", &monero_block_header::m_nonce)
    .def_readwrite("miner_tx_hash", &monero_block_header::m_miner_tx_hash)
    .def_readwrite("num_txs", &monero_block_header::m_num_txs)
    .def_readwrite("orphan_status", &monero_block_header::m_orphan_status)
    .def_readwrite("prev_hash", &monero_block_header::m_prev_hash)
    .def_readwrite("reward", &monero_block_header::m_reward)
    .def_readwrite("pow_hash", &monero_block_header::m_pow_hash)
    .def("copy", [](const std::shared_ptr<monero_block_header>& self) {
      auto tgt = std::make_shared<monero_block_header>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_block_header>& self, const std::shared_ptr<monero_block_header>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_block (needs: monero_tx)
  t.py_monero_block
    .def(py::init<>())
    .def("__str__", &monero_block::serialize)
    .def_readwrite("hex", &monero_block::m_hex)
    .def_readwrite("miner_tx", &monero_block::m_miner_tx)
    .def_readwrite("txs", &monero_block::m_txs)
    .def_readwrite("tx_hashes", &monero_block::m_tx_hashes)
    .def("copy", [](const std::shared_ptr<monero_block>& self) {
      auto tgt = std::make_shared<monero_block>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_block>& self, const std::shared_ptr<monero_block>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_block_template
  py::class_<monero_block_template, serializable_struct, std::shared_ptr<monero_block_template>>(m, "MoneroBlockTemplate")
    .def(py::init<>())
    .def_readwrite("block_template_blob", &monero_block_template::m_block_template_blob)
    .def_readwrite("block_hashing_blob", &monero_block_template::m_block_hashing_blob)
    .def_readwrite("difficulty_low", &monero_block_template::m_difficulty_low)
    .def_readwrite("difficulty_high", &monero_block_template::m_difficulty_high)
    .def_readwrite("expected_reward", &monero_block_template::m_expected_reward)
    .def_readwrite("height", &monero_block_template::m_height)
    .def_readwrite("prev_hash", &monero_block_template::m_prev_hash)
    .def_readwrite("reserved_offset", &monero_block_template::m_reserved_offset)
    .def_readwrite("seed_height", &monero_block_template::m_seed_height)
    .def_readwrite("seed_hash", &monero_block_template::m_seed_hash)
    .def_readwrite("next_seed_hash", &monero_block_template::m_next_seed_hash);

  // monero_connection_span
  py::class_<monero_connection_span, serializable_struct, std::shared_ptr<monero_connection_span>>(m, "MoneroConnectionSpan")
    .def(py::init<>())
    .def_readwrite("connection_id", &monero_connection_span::m_connection_id)
    .def_readwrite("num_blocks", &monero_connection_span::m_num_blocks)
    .def_readwrite("remote_address", &monero_connection_span::m_remote_address)
    .def_readwrite("rate", &monero_connection_span::m_rate)
    .def_readwrite("speed", &monero_connection_span::m_speed)
    .def_readwrite("size", &monero_connection_span::m_size)
    .def_readwrite("start_height", &monero_connection_span::m_start_height);

  // monero_peer
  py::class_<monero_peer, serializable_struct, std::shared_ptr<monero_peer>>(m, "MoneroPeer")
    .def(py::init<>())
    .def_readwrite("id", &monero_peer::m_id)
    .def_readwrite("address", &monero_peer::m_address)
    .def_readwrite("host", &monero_peer::m_host)
    .def_readwrite("port", &monero_peer::m_port)
    .def_readwrite("is_online", &monero_peer::m_is_online)
    .def_readwrite("last_seen_timestamp", &monero_peer::m_last_seen_timestamp)
    .def_readwrite("pruning_seed", &monero_peer::m_pruning_seed)
    .def_readwrite("rpc_port", &monero_peer::m_rpc_port)
    .def_readwrite("rpc_credits_per_hash", &monero_peer::m_rpc_credits_per_hash)
    .def_readwrite("hash", &monero_peer::m_hash)
    .def_readwrite("avg_download", &monero_peer::m_avg_download)
    .def_readwrite("avg_upload", &monero_peer::m_avg_upload)
    .def_readwrite("current_download", &monero_peer::m_current_download)
    .def_readwrite("current_upload", &monero_peer::m_current_upload)
    .def_readwrite("height", &monero_peer::m_height)
    .def_readwrite("is_incoming", &monero_peer::m_is_incoming)
    .def_readwrite("live_time", &monero_peer::m_live_time)
    .def_readwrite("is_local_ip", &monero_peer::m_is_local_ip)
    .def_readwrite("is_local_host", &monero_peer::m_is_local_host)
    .def_readwrite("num_receives", &monero_peer::m_num_receives)
    .def_readwrite("num_sends", &monero_peer::m_num_sends)
    .def_readwrite("receive_idle_time", &monero_peer::m_receive_idle_time)
    .def_readwrite("send_idle_time", &monero_peer::m_send_idle_time)
    .def_readwrite("state", &monero_peer::m_state)
    .def_readwrite("num_support_flags", &monero_peer::m_num_support_flags)
    .def_readwrite("connection_type", &monero_peer::m_connection_type);

  // monero_alt_chain
  py::class_<monero_alt_chain, serializable_struct, std::shared_ptr<monero_alt_chain>>(m, "MoneroAltChain")
    .def(py::init<>())
    .def_readwrite("block_hashes", &monero_alt_chain::m_block_hashes)
    .def_readwrite("difficulty_low", &monero_alt_chain::m_difficulty_low)
    .def_readwrite("difficulty_high", &monero_alt_chain::m_difficulty_high)
    .def_readwrite("height", &monero_alt_chain::m_height)
    .def_readwrite("length", &monero_alt_chain::m_length)
    .def_readwrite("main_chain_parent_block_hash", &monero_alt_chain::m_main_chain_parent_block_hash);

  // monero_ban
  py::class_<monero_ban, serializable_struct, std::shared_ptr<monero_ban>>(m, "MoneroBan")
    .def(py::init<>())
    .def_readwrite("host", &monero_ban::m_host)
    .def_readwrite("ip", &monero_ban::m_ip)
    .def_readwrite("is_banned", &monero_ban::m_is_banned)
    .def_readwrite("seconds", &monero_ban::m_seconds);

  // monero_output_distribution_entry
  py::class_<monero_output_distribution_entry, serializable_struct, std::shared_ptr<monero_output_distribution_entry>>(m, "MoneroOutputDistributionEntry")
    .def(py::init<>())
    .def_readwrite("amount", &monero_output_distribution_entry::m_amount)
    .def_readwrite("base", &monero_output_distribution_entry::m_base)
    .def_readwrite("distribution", &monero_output_distribution_entry::m_distribution)
    .def_readwrite("start_height", &monero_output_distribution_entry::m_start_height);

  // monero_output_histogram_entry
  py::class_<monero_output_histogram_entry, serializable_struct, std::shared_ptr<monero_output_histogram_entry>>(m, "MoneroOutputHistogramEntry")
    .def(py::init<>())
    .def_readwrite("amount", &monero_output_histogram_entry::m_amount)
    .def_readwrite("num_instances", &monero_output_histogram_entry::m_num_instances)
    .def_readwrite("unlocked_instances", &monero_output_histogram_entry::m_unlocked_instances)
    .def_readwrite("recent_instances", &monero_output_histogram_entry::m_recent_instances);

  // monero_hard_fork_info
  py::class_<monero_hard_fork_info, monero_rpc_payment_info, std::shared_ptr<monero_hard_fork_info>>(m, "MoneroHardForkInfo")
    .def(py::init<>())
    .def_readwrite("earliest_height", &monero_hard_fork_info::m_earliest_height)
    .def_readwrite("is_enabled", &monero_hard_fork_info::m_is_enabled)
    .def_readwrite("state", &monero_hard_fork_info::m_state)
    .def_readwrite("threshold", &monero_hard_fork_info::m_threshold)
    .def_readwrite("version", &monero_hard_fork_info::m_version)
    .def_readwrite("num_votes", &monero_hard_fork_info::m_num_votes)
    .def_readwrite("window", &monero_hard_fork_info::m_window)
    .def_readwrite("voting", &monero_hard_fork_info::m_voting);

  // monero_prune_result
  py::class_<monero_prune_result, serializable_struct, std::shared_ptr<monero_prune_result>>(m, "MoneroPruneResult")
    .def(py::init<>())
    .def_readwrite("is_pruned", &monero_prune_result::m_is_pruned)
    .def_readwrite("pruning_seed", &monero_prune_result::m_pruning_seed);

  // monero_daemon_sync_info
  py::class_<monero_daemon_sync_info, monero_rpc_payment_info, std::shared_ptr<monero_daemon_sync_info>>(m, "MoneroDaemonSyncInfo")
    .def(py::init<>())
    .def_readwrite("height", &monero_daemon_sync_info::m_height)
    .def_readwrite("peers", &monero_daemon_sync_info::m_peers)
    .def_readwrite("spans", &monero_daemon_sync_info::m_spans)
    .def_readwrite("target_height", &monero_daemon_sync_info::m_target_height)
    .def_readwrite("next_needed_pruning_seed", &monero_daemon_sync_info::m_next_needed_pruning_seed)
    .def_readwrite("overview", &monero_daemon_sync_info::m_overview);

  // monero_daemon_info
  py::class_<monero_daemon_info, monero_rpc_payment_info, std::shared_ptr<monero_daemon_info>>(m, "MoneroDaemonInfo")
    .def(py::init<>())
    .def_readwrite("version", &monero_daemon_info::m_version)
    .def_readwrite("num_alt_blocks", &monero_daemon_info::m_num_alt_blocks)
    .def_readwrite("block_size_limit", &monero_daemon_info::m_block_size_limit)
    .def_readwrite("block_size_median", &monero_daemon_info::m_block_size_median)
    .def_readwrite("block_weight_limit", &monero_daemon_info::m_block_weight_limit)
    .def_readwrite("block_weight_median", &monero_daemon_info::m_block_weight_median)
    .def_readwrite("bootstrap_daemon_address", &monero_daemon_info::m_bootstrap_daemon_address)
    .def_readwrite("difficulty_low", &monero_daemon_info::m_difficulty_low)
    .def_readwrite("difficulty_high", &monero_daemon_info::m_difficulty_high)
    .def_readwrite("cumulative_difficulty_low", &monero_daemon_info::m_cumulative_difficulty_low)
    .def_readwrite("cumulative_difficulty_high", &monero_daemon_info::m_cumulative_difficulty_high)
    .def_readwrite("free_space", &monero_daemon_info::m_free_space)
    .def_readwrite("num_offline_peers", &monero_daemon_info::m_num_offline_peers)
    .def_readwrite("num_online_peers", &monero_daemon_info::m_num_online_peers)
    .def_readwrite("height", &monero_daemon_info::m_height)
    .def_readwrite("height_without_bootstrap", &monero_daemon_info::m_height_without_bootstrap)
    .def_readwrite("network_type", &monero_daemon_info::m_network_type)
    .def_readwrite("is_offline", &monero_daemon_info::m_is_offline)
    .def_readwrite("num_incoming_connections", &monero_daemon_info::m_num_incoming_connections)
    .def_readwrite("num_outgoing_connections", &monero_daemon_info::m_num_outgoing_connections)
    .def_readwrite("num_rpc_connections", &monero_daemon_info::m_num_rpc_connections)
    .def_readwrite("start_timestamp", &monero_daemon_info::m_start_timestamp)
    .def_readwrite("adjusted_timestamp", &monero_daemon_info::m_adjusted_timestamp)
    .def_readwrite("target", &monero_daemon_info::m_target)
    .def_readwrite("target_height", &monero_daemon_info::m_target_height)
    .def_readwrite("num_txs", &monero_daemon_info::m_num_txs)
    .def_readwrite("num_txs_pool", &monero_daemon_info::m_num_txs_pool)
    .def_readwrite("was_bootstrap_ever_used", &monero_daemon_info::m_was_bootstrap_ever_used)
    .def_readwrite("database_size", &monero_daemon_info::m_database_size)
    .def_readwrite("update_available", &monero_daemon_info::m_update_available)
    .def_readwrite("is_busy_syncing", &monero_daemon_info::m_is_busy_syncing)
    .def_readwrite("is_synchronized", &monero_daemon_info::m_is_synchronized)
    .def_readwrite("is_restricted", &monero_daemon_info::m_is_restricted);

  // monero_daemon_update_check_result
  py::class_<monero_daemon_update_check_result, serializable_struct, std::shared_ptr<monero_daemon_update_check_result>>(m, "MoneroDaemonUpdateCheckResult")
    .def(py::init<>())
    .def_readwrite("is_update_available", &monero_daemon_update_check_result::m_is_update_available)
    .def_readwrite("version", &monero_daemon_update_check_result::m_version)
    .def_readwrite("hash", &monero_daemon_update_check_result::m_hash)
    .def_readwrite("auto_uri", &monero_daemon_update_check_result::m_auto_uri)
    .def_readwrite("user_uri", &monero_daemon_update_check_result::m_user_uri);

  // monero_daemon_update_check_result
  py::class_<monero_daemon_update_download_result, monero_daemon_update_check_result, std::shared_ptr<monero_daemon_update_download_result>>(m, "MoneroDaemonUpdateDownloadResult")
    .def(py::init<>())
    .def_readwrite("download_path", &monero_daemon_update_download_result::m_download_path);

  // monero_submit_tx_result
  py::class_<monero_submit_tx_result, monero_rpc_payment_info, std::shared_ptr<monero_submit_tx_result>>(m, "MoneroSubmitTxResult")
    .def(py::init<>())
    .def_readwrite("is_good", &monero_submit_tx_result::m_is_good)
    .def_readwrite("is_relayed", &monero_submit_tx_result::m_is_relayed)
    .def_readwrite("is_double_spend", &monero_submit_tx_result::m_is_double_spend)
    .def_readwrite("is_fee_too_low", &monero_submit_tx_result::m_is_fee_too_low)
    .def_readwrite("is_mixin_too_low", &monero_submit_tx_result::m_is_mixin_too_low)
    .def_readwrite("has_invalid_input", &monero_submit_tx_result::m_has_invalid_input)
    .def_readwrite("has_invalid_output", &monero_submit_tx_result::m_has_invalid_output)
    .def_readwrite("has_too_few_outputs", &monero_submit_tx_result::m_has_too_few_outputs)
    .def_readwrite("is_overspend", &monero_submit_tx_result::m_is_overspend)
    .def_readwrite("is_too_big", &monero_submit_tx_result::m_is_too_big)
    .def_readwrite("sanity_check_failed", &monero_submit_tx_result::m_sanity_check_failed)
    .def_readwrite("reason", &monero_submit_tx_result::m_reason)
    .def_readwrite("is_tx_extra_too_big", &monero_submit_tx_result::m_is_tx_extra_too_big)
    .def_readwrite("is_nonzero_unlock_time", &monero_submit_tx_result::m_is_nonzero_unlock_time);

  // monero_generate_blocks_result
  py::class_<monero_generate_blocks_result, serializable_struct, std::shared_ptr<monero_generate_blocks_result>>(m, "MoneroGenerateBlocksResult")
    .def(py::init<>())
    .def_readwrite("block_hashes", &monero_generate_blocks_result::m_block_hashes)
    .def_readwrite("height", &monero_generate_blocks_result::m_height);

  // monero_tx_pool_stats
  py::class_<monero_tx_pool_stats, serializable_struct, std::shared_ptr<monero_tx_pool_stats>>(m, "MoneroTxPoolStats")
    .def(py::init<>())
    .def_readwrite("num_txs", &monero_tx_pool_stats::m_num_txs)
    .def_readwrite("num_not_relayed", &monero_tx_pool_stats::m_num_not_relayed)
    .def_readwrite("num_failing", &monero_tx_pool_stats::m_num_failing)
    .def_readwrite("num_double_spends", &monero_tx_pool_stats::m_num_double_spends)
    .def_readwrite("num10m", &monero_tx_pool_stats::m_num10m)
    .def_readwrite("fee_total", &monero_tx_pool_stats::m_fee_total)
    .def_readwrite("bytes_max", &monero_tx_pool_stats::m_bytes_max)
    .def_readwrite("bytes_med", &monero_tx_pool_stats::m_bytes_med)
    .def_readwrite("bytes_min", &monero_tx_pool_stats::m_bytes_min)
    .def_readwrite("bytes_total", &monero_tx_pool_stats::m_bytes_total)
    .def_readwrite("histo98pc", &monero_tx_pool_stats::m_histo98pc)
    .def_readwrite("oldest_timestamp", &monero_tx_pool_stats::m_oldest_timestamp)
    .def_readwrite("histo", &monero_tx_pool_stats::m_histo, py::return_value_policy::reference_internal);

  // monero_mining_status
  py::class_<monero_mining_status, serializable_struct, std::shared_ptr<monero_mining_status>>(m, "MoneroMiningStatus")
    .def(py::init<>())
    .def_readwrite("is_active", &monero_mining_status::m_is_active)
    .def_readwrite("is_background", &monero_mining_status::m_is_background)
    .def_readwrite("address", &monero_mining_status::m_address)
    .def_readwrite("speed", &monero_mining_status::m_speed)
    .def_readwrite("num_threads", &monero_mining_status::m_num_threads);

  // monero_miner_tx_sum
  py::class_<monero_miner_tx_sum, serializable_struct, std::shared_ptr<monero_miner_tx_sum>>(m, "MoneroMinerTxSum")
    .def(py::init<>())
    .def_readwrite("emission_sum_low", &monero_miner_tx_sum::m_emission_sum_low)
    .def_readwrite("emission_sum_high", &monero_miner_tx_sum::m_emission_sum_high)
    .def_readwrite("fee_sum_low", &monero_miner_tx_sum::m_fee_sum_low)
    .def_readwrite("fee_sum_high", &monero_miner_tx_sum::m_fee_sum_high);

  // monero_tx
  t.py_monero_tx
    .def(py::init<>())
    .def_property_readonly_static("DEFAULT_PAYMENT_ID", [](py::object /* self */) { return monero_tx::DEFAULT_PAYMENT_ID; })
    .def_readwrite("block", &monero_tx::m_block)
    .def_readwrite("hash", &monero_tx::m_hash)
    .def_readwrite("version", &monero_tx::m_version)
    .def_readwrite("is_miner_tx", &monero_tx::m_is_miner_tx)
    .def_readwrite("payment_id", &monero_tx::m_payment_id)
    .def_readwrite("fee", &monero_tx::m_fee)
    .def_readwrite("ring_size", &monero_tx::m_ring_size)
    .def_readwrite("relay", &monero_tx::m_relay)
    .def_readwrite("is_relayed", &monero_tx::m_is_relayed)
    .def_readwrite("is_confirmed", &monero_tx::m_is_confirmed)
    .def_readwrite("in_tx_pool", &monero_tx::m_in_tx_pool)
    .def_readwrite("num_confirmations", &monero_tx::m_num_confirmations)
    .def_readwrite("unlock_time", &monero_tx::m_unlock_time)
    .def_readwrite("last_relayed_timestamp", &monero_tx::m_last_relayed_timestamp)
    .def_readwrite("received_timestamp", &monero_tx::m_received_timestamp)
    .def_readwrite("is_double_spend_seen", &monero_tx::m_is_double_spend_seen)
    .def_readwrite("key", &monero_tx::m_key)
    .def_readwrite("full_hex", &monero_tx::m_full_hex)
    .def_readwrite("pruned_hex", &monero_tx::m_pruned_hex)
    .def_readwrite("prunable_hex", &monero_tx::m_prunable_hex)
    .def_readwrite("prunable_hash", &monero_tx::m_prunable_hash)
    .def_readwrite("size", &monero_tx::m_size)
    .def_readwrite("weight", &monero_tx::m_weight)
    .def_readwrite("inputs", &monero_tx::m_inputs)
    .def_readwrite("outputs", &monero_tx::m_outputs)
    .def_readwrite("output_indices", &monero_tx::m_output_indices)
    .def_readwrite("metadata", &monero_tx::m_metadata)
    .def_readwrite("common_tx_sets", &monero_tx::m_common_tx_sets)
    .def_readwrite("extra", &monero_tx::m_extra)
    .def_readwrite("rct_signatures", &monero_tx::m_rct_signatures)
    .def_readwrite("rct_sig_prunable", &monero_tx::m_rct_sig_prunable)
    .def_readwrite("is_kept_by_block", &monero_tx::m_is_kept_by_block)
    .def_readwrite("is_failed", &monero_tx::m_is_failed)
    .def_readwrite("last_failed_height", &monero_tx::m_last_failed_height)
    .def_readwrite("last_failed_hash", &monero_tx::m_last_failed_hash)
    .def_readwrite("max_used_block_height", &monero_tx::m_max_used_block_height)
    .def_readwrite("max_used_block_hash", &monero_tx::m_max_used_block_hash)
    .def_readwrite("signatures", &monero_tx::m_signatures)
    .def("copy", [](const std::shared_ptr<monero_tx>& self) {
      auto tgt = std::make_shared<monero_tx>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_tx>& self, const std::shared_ptr<monero_tx>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"))
    .def("get_height", [](monero_tx& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    })
    .def("__lt__", [](const std::shared_ptr<monero_tx>& a, const std::shared_ptr<monero_tx>& b){
      monero_tx_height_comparator comp;
      return comp(a, b);
    });

  // monero_key_image
  t.py_monero_key_image
    .def(py::init<>())
    .def_static("deserialize_key_images", [](const std::string& key_images_json) {
      MONERO_CATCH_AND_RETHROW(monero_key_image::deserialize_key_images(key_images_json));
    }, py::arg("key_images_json"))
    .def_readwrite("hex", &monero_key_image::m_hex)
    .def_readwrite("signature", &monero_key_image::m_signature)
    .def("copy", [](const std::shared_ptr<monero_key_image>& self) {
      auto tgt = std::make_shared<monero_key_image>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_key_image>& self, const std::shared_ptr<monero_key_image>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_output
  t.py_monero_output
    .def(py::init<>())
    .def_readwrite("tx", &monero_output::m_tx)
    .def_readwrite("key_image", &monero_output::m_key_image)
    .def_readwrite("amount", &monero_output::m_amount)
    .def_readwrite("index", &monero_output::m_index)
    .def_readwrite("stealth_public_key", &monero_output::m_stealth_public_key)
    .def_readwrite("ring_output_indices", &monero_output::m_ring_output_indices)
    .def("copy", [](const std::shared_ptr<monero_output>& self) {
      auto tgt = std::make_shared<monero_output>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_output>& self, const std::shared_ptr<monero_output>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_daemon_listener
  t.py_monero_daemon_listener
    .def(py::init<>())
    .def_readwrite("last_header", &monero_daemon_listener::m_last_header)
    .def("on_block_header", [](monero_daemon_listener& self, const std::shared_ptr<monero_block_header>& header) {
      MONERO_CATCH_AND_RETHROW(self.on_block_header(header));
    }, py::arg("header"));

  // monero_daemon
  t.py_monero_daemon
    .def(py::init<>())
    .def("add_listener", [](monero_daemon& self, monero_daemon_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("remove_listener", [](monero_daemon& self, monero_daemon_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("get_listeners", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_listeners());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_version", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_version());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_trusted", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.is_trusted());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_height", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_block_hash", [](monero_daemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_hash(height));
    }, py::arg("height"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_template", [](monero_daemon& self, const std::string& wallet_address, const boost::optional<int>& reserve_size) {
      MONERO_CATCH_AND_RETHROW(self.get_block_template(wallet_address, reserve_size));
    }, py::arg("wallet_address"), py::arg("reserve_size") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_last_block_header", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_last_block_header());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_block_header_by_hash", [](monero_daemon& self, const std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.get_block_header_by_hash(hash));
    }, py::arg("hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_header_by_height", [](monero_daemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_header_by_height(height));
    }, py::arg("height"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_headers_by_range", [](monero_daemon& self, uint64_t start_height, uint64_t end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_headers_by_range(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_by_hash", [](monero_daemon& self, const std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.get_block_by_hash(hash));
    }, py::arg("hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_hash", [](monero_daemon& self, const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_hash(block_hashes, start_height, prune));
    }, py::arg("block_hashes"), py::arg("start_height"), py::arg("prune"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_by_height", [](monero_daemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_by_height(height));
    }, py::arg("height"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_height", [](monero_daemon& self, const std::vector<uint64_t>& heights) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_height(heights));
    }, py::arg("heights"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_range", [](monero_daemon& self, const boost::optional<uint64_t>& start_height, const boost::optional<uint64_t>& end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_range_chunked", [](monero_daemon& self, const boost::optional<uint64_t>& start_height, const boost::optional<uint64_t>& end_height, const boost::optional<uint64_t>& max_chunk_size) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range_chunked(start_height, end_height, max_chunk_size));
    }, py::arg("start_height"), py::arg("end_height"), py::arg("max_chunk_size") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_block_hashes", [](monero_daemon& self, const std::vector<std::string>& block_hashes, uint64_t start_height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_hashes(block_hashes, start_height));
    }, py::arg("block_hashes"), py::arg("start_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx", [](monero_daemon& self, const std::string& tx_hash, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx(tx_hash, prune));
    }, py::arg("tx_hash"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_txs", [](monero_daemon& self, const std::vector<std::string>& tx_hashes, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_txs(tx_hashes, prune));
    }, py::arg("tx_hashes"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_hex", [](monero_daemon& self, const std::string& tx_hash, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_hex(tx_hash, prune));
    }, py::arg("tx_hash"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_hexes", [](monero_daemon& self, const std::vector<std::string>& tx_hashes, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_hexes(tx_hashes, prune));
    }, py::arg("tx_hashes"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_miner_tx_sum", [](monero_daemon& self, uint64_t height, uint64_t num_blocks) {
      MONERO_CATCH_AND_RETHROW(self.get_miner_tx_sum(height, num_blocks));
    }, py::arg("height"), py::arg("num_blocks"), py::call_guard<py::gil_scoped_release>())
    .def("get_fee_estimate", [](monero_daemon& self, uint64_t grace_blocks) {
      MONERO_CATCH_AND_RETHROW(self.get_fee_estimate(grace_blocks));
    }, py::arg("grace_blocks") = 0, py::call_guard<py::gil_scoped_release>())
    .def("submit_tx_hex", [](monero_daemon& self, const std::string& tx_hex, bool do_not_relay) {
      MONERO_CATCH_AND_RETHROW(self.submit_tx_hex(tx_hex, do_not_relay));
    }, py::arg("tx_hex"), py::arg("do_not_relay") = false, py::call_guard<py::gil_scoped_release>())
    .def("relay_tx_by_hash", [](monero_daemon& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx_by_hash(tx_hash));
    }, py::arg("tx_hash"), py::call_guard<py::gil_scoped_release>())
    .def("relay_txs_by_hash", [](monero_daemon& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs_by_hash(tx_hashes));
    }, py::arg("tx_hashes"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool_hashes", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_hashes());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool_backlog", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_backlog());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool_stats", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_stats());
    }, py::call_guard<py::gil_scoped_release>())
    .def("flush_tx_pool", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool());
    }, py::call_guard<py::gil_scoped_release>())
    .def("flush_tx_pool", [](monero_daemon& self, const std::vector<std::string>& hashes) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool(hashes));
    }, py::arg("hashes"), py::call_guard<py::gil_scoped_release>())
    .def("flush_tx_pool", [](monero_daemon& self, const std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool(hash));
    }, py::arg("hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_key_image_spent_status", [](monero_daemon& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.get_key_image_spent_status(key_image));
    }, py::arg("key_image"), py::call_guard<py::gil_scoped_release>())
    .def("get_key_image_spent_statuses", [](monero_daemon& self, const std::vector<std::string>& key_images) {
      MONERO_CATCH_AND_RETHROW(self.get_key_image_spent_statuses(key_images));
    }, py::arg("key_images"), py::call_guard<py::gil_scoped_release>())
    .def("get_outputs", [](monero_daemon& self, const std::vector<monero_output>& outputs) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs(outputs));
    }, py::arg("outputs"), py::call_guard<py::gil_scoped_release>())
    .def("get_output_histogram", [](monero_daemon& self, const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) {
      MONERO_CATCH_AND_RETHROW(self.get_output_histogram(amounts, min_count, max_count, is_unlocked, recent_cutoff));
    }, py::arg("amounts"), py::arg("min_count"), py::arg("max_count"), py::arg("is_unlocked"), py::arg("recent_cutoff"), py::call_guard<py::gil_scoped_release>())
    .def("get_output_distribution", [](monero_daemon& self, const std::vector<uint64_t>& amounts, const boost::optional<bool>& is_cumulative, const boost::optional<uint64_t>& start_height, const boost::optional<uint64_t>& end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_output_distribution(amounts, is_cumulative, start_height, end_height));
    }, py::arg("amounts"), py::arg("is_cumulative") = py::none(), py::arg("start_height") = py::none(), py::arg("end_height") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_info", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_sync_info", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_sync_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_hard_fork_info", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_hard_fork_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_alt_chains", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_alt_chains());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_alt_block_hashes", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_alt_block_hashes());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_download_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_download_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_download_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_download_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("reset_download_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.reset_download_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_upload_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_upload_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_upload_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_upload_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("reset_upload_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.reset_upload_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_peers", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peers());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_known_peers", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_known_peers());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_outgoing_peer_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_outgoing_peer_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("set_incoming_peer_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_incoming_peer_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("get_peer_bans", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peer_bans());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_peer_bans", [](monero_daemon& self, const std::vector<std::shared_ptr<monero_ban>>& bans) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_bans(bans));
    }, py::arg("bans"), py::call_guard<py::gil_scoped_release>())
    .def("set_peer_ban", [](monero_daemon& self, const std::shared_ptr<monero_ban>& ban) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_ban(ban));
    }, py::arg("ban"), py::call_guard<py::gil_scoped_release>())
    .def("start_mining", [](monero_daemon& self, const std::string& address, const boost::optional<uint64_t>& num_threads, const boost::optional<bool>& is_background, const boost::optional<bool>& ignore_battery) {
      MONERO_CATCH_AND_RETHROW(self.start_mining(address, num_threads, is_background, ignore_battery));
    }, py::arg("address"), py::arg("num_threads"), py::arg("is_background"), py::arg("ignore_battery"), py::call_guard<py::gil_scoped_release>())
    .def("stop_mining", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_mining());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_mining_status", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_mining_status());
    }, py::call_guard<py::gil_scoped_release>())
    .def("generate_blocks", [](monero_daemon& self,const std::string& wallet_address, uint64_t num_blocks, const boost::optional<std::string>& prev_block_hash, const boost::optional<uint32_t>& starting_nonce) {
      MONERO_CATCH_AND_RETHROW(self.generate_blocks(wallet_address, num_blocks, prev_block_hash, starting_nonce));
    }, py::arg("wallet_address"), py::arg("num_blocks"), py::arg("prev_block_hash") = py::none(), py::arg("starting_nonce") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("submit_block", [](monero_daemon& self, const std::string& block_blob) {
      MONERO_CATCH_AND_RETHROW(self.submit_block(block_blob));
    }, py::arg("block_blob"), py::call_guard<py::gil_scoped_release>())
    .def("submit_blocks", [](monero_daemon& self, const std::vector<std::string>& block_blobs) {
      MONERO_CATCH_AND_RETHROW(self.submit_blocks(block_blobs));
    }, py::arg("block_blobs"), py::call_guard<py::gil_scoped_release>())
    .def("prune_blockchain", [](monero_daemon& self, bool check) {
      MONERO_CATCH_AND_RETHROW(self.prune_blockchain(check));
    }, py::arg("check"), py::call_guard<py::gil_scoped_release>())
    .def("check_for_update", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.check_for_update());
    }, py::call_guard<py::gil_scoped_release>())
    .def("download_update", [](monero_daemon& self, const std::string& path) {
      MONERO_CATCH_AND_RETHROW(self.download_update(path));
    }, py::arg("path") = "", py::call_guard<py::gil_scoped_release>())
    .def("stop", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.stop());
    }, py::call_guard<py::gil_scoped_release>())
    .def("wait_for_next_block_header", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.wait_for_next_block_header());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_daemon_rpc
  t.py_monero_daemon_rpc
    .def(py::init<const std::shared_ptr<monero_rpc_connection>&>(), py::arg("rpc"), py::call_guard<py::gil_scoped_release>())
    .def(py::init<const std::string&, const std::string&, const std::string&, const std::string&, const std::string&, const boost::optional<uint32_t>&>(), py::arg("uri"), py::arg("username") = "", py::arg("password") = "", py::arg("proxy_uri") = "", py::arg("zmq_uri") = "", py::arg("timeout_ms") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_rpc_connection", [](const monero_daemon_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    })
    .def("is_connected", [](monero_daemon_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected());
    }, py::call_guard<py::gil_scoped_release>());

}
