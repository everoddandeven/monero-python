from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAltChain,
    MoneroConnectionSpan,
    MoneroDaemonInfo,
    MoneroDaemonNetworkStats,
    MoneroDaemonSyncInfo,
    MoneroDaemonUpdateCheckResult,
    MoneroDaemonUpdateDownloadResult,
    MoneroFeeEstimate,
    MoneroHardForkInfo,
    MoneroNetworkType,
    MoneroPeer,
    MoneroPruneResult,
)

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelInfo")


@pytest.mark.unit
class TestMoneroDaemonModelInfo(BaseTestClass):
    """Daemon info model unit tests."""

    def test_alt_chain_deserialize(self) -> None:
        alt_chain: MoneroAltChain = MoneroAltChain()
        alt_chain.block_hashes = ["a" * 64, "b" * 64]
        alt_chain.difficulty_low = 100
        alt_chain.difficulty_high = 0
        alt_chain.height = 12345
        alt_chain.length = 3
        alt_chain.main_chain_parent_block_hash = "c" * 64
        AssertUtils.assert_serialization_integrity(alt_chain)

    def test_prune_result_deserialize(self) -> None:
        result: MoneroPruneResult = MoneroPruneResult()
        result.pruning_seed = 387
        # is_pruned is deliberately not set here: to_rapidjson_val() serializes it
        # under "isPruned" but from_property_tree() looks for "pruned" instead, so
        # it never round trips (see test below)
        AssertUtils.assert_serialization_integrity(result)

    def test_prune_result_is_pruned_deserialize(self) -> None:
        result: MoneroPruneResult = MoneroPruneResult()
        result.is_pruned = True
        json_str: str = result.serialize()
        logger.debug(f"Serialized prune result: {json_str}")
        assert '"isPruned"' in json_str
        restored: MoneroPruneResult = MoneroPruneResult.deserialize(json_str)
        logger.debug(f"Deserialized prune result re-serialized: {restored.serialize()}")
        assert restored.is_pruned == result.is_pruned

    def test_fee_estimate_deserialize(self) -> None:
        estimate: MoneroFeeEstimate = MoneroFeeEstimate()
        estimate.fee = 20000
        estimate.quantization_mask = 10000
        estimate.fees = [10000, 20000, 30000, 40000]
        AssertUtils.assert_serialization_integrity(estimate)

    def test_daemon_info_deserialize(self) -> None:
        info: MoneroDaemonInfo = MoneroDaemonInfo()
        info.credits = 0
        info.top_block_hash = "a" * 64
        info.version = "0.18.5.1"
        info.num_alt_blocks = 1
        info.block_size_limit = 600000
        info.block_size_median = 300000
        info.block_weight_limit = 600000
        info.block_weight_median = 300000
        info.bootstrap_daemon_address = "node.example.com"
        info.difficulty_low = 123456
        info.difficulty_high = 0
        info.cumulative_difficulty_low = 987654
        info.cumulative_difficulty_high = 0
        info.free_space = 1000000000
        info.num_offline_peers = 1
        info.num_online_peers = 10
        info.height = 3000000
        info.height_without_bootstrap = 3000000
        info.network_type = MoneroNetworkType.TESTNET
        info.is_offline = False
        info.num_incoming_connections = 5
        info.num_outgoing_connections = 8
        info.num_rpc_connections = 2
        info.start_timestamp = 1600000000
        info.adjusted_timestamp = 1700000000
        info.target = 120
        info.target_height = 0
        info.num_txs = 100
        info.num_txs_pool = 3
        info.was_bootstrap_ever_used = False
        info.database_size = 100000000
        info.update_available = False
        info.is_busy_syncing = False
        info.is_synchronized = True
        info.is_restricted = False
        info.is_regtest = True
        AssertUtils.assert_serialization_integrity(info)

    def test_daemon_info_invalid_network_type(self) -> None:
        with pytest.raises(RuntimeError, match="invalid network type"):
            MoneroDaemonInfo.deserialize('{"networkType":9}')

    def test_daemon_sync_info_deserialize(self) -> None:
        info: MoneroDaemonSyncInfo = MoneroDaemonSyncInfo()
        info.credits = 0
        info.top_block_hash = "a" * 64
        info.height = 3000000
        info.target_height = 3000010
        info.next_needed_pruning_seed = 0
        info.overview = "syncing"
        # peers/spans are serialized as sub-arrays but from_property_tree() never
        # reads them back (see test below)
        AssertUtils.assert_serialization_integrity(info)

    def test_daemon_sync_info_peers_and_spans_deserialize(self) -> None:
        info: MoneroDaemonSyncInfo = MoneroDaemonSyncInfo()
        info.peers = [MoneroPeer()]
        info.spans = [MoneroConnectionSpan()]
        json_str: str = info.serialize()
        logger.debug(f"Serialized daemon sync info: {json_str}")
        assert "peers" in json_str and "spans" in json_str
        restored: MoneroDaemonSyncInfo = MoneroDaemonSyncInfo.deserialize(json_str)
        logger.debug(f"Deserialized daemon sync info re-serialized: {restored.serialize()}")
        assert len(restored.peers) == len(info.peers)
        assert len(restored.spans) == len(info.spans)

    def test_hard_fork_info_deserialize(self) -> None:
        info: MoneroHardForkInfo = MoneroHardForkInfo()
        info.credits = 0
        info.top_block_hash = "a" * 64
        info.earliest_height = 100000
        info.is_enabled = True
        info.state = 0
        info.threshold = 0
        info.version = 16
        info.num_votes = 5000
        info.window = 10080
        info.voting = 16
        AssertUtils.assert_serialization_integrity(info)

    def test_daemon_network_stats_deserialize(self) -> None:
        stats: MoneroDaemonNetworkStats = MoneroDaemonNetworkStats()
        stats.credits = 0
        stats.top_block_hash = "a" * 64
        stats.start_time = 1700000000
        stats.total_packets_in = 1234
        stats.total_bytes_in = 567890
        stats.total_packets_out = 4321
        stats.total_bytes_out = 98765
        AssertUtils.assert_serialization_integrity(stats)

    def test_daemon_update_check_result_deserialize(self) -> None:
        result: MoneroDaemonUpdateCheckResult = MoneroDaemonUpdateCheckResult()
        result.is_update_available = True
        result.version = "0.18.5.1"
        result.hash = "a" * 64
        result.auto_uri = "https://example.com/auto"
        result.user_uri = "https://example.com/user"
        AssertUtils.assert_serialization_integrity(result)

    def test_daemon_update_download_result_deserialize(self) -> None:
        result: MoneroDaemonUpdateDownloadResult = MoneroDaemonUpdateDownloadResult()
        result.is_update_available = True
        result.version = "0.18.5.1"
        result.hash = "a" * 64
        result.auto_uri = "https://example.com/auto"
        result.user_uri = "https://example.com/user"
        result.download_path = "/tmp/update.bin"
        AssertUtils.assert_serialization_integrity(result)
