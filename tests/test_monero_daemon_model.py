import pytest
import logging
import subprocess
import sys

from typing import LiteralString

from monero import (
    MoneroVersion, MoneroRpcPaymentInfo, MoneroRpcConnection, MoneroAltChain,
    MoneroBan, MoneroPruneResult, MoneroMiningStatus, MoneroMinerTxSum,
    MoneroBlockTemplate, MoneroConnectionSpan, MoneroPeer, MoneroConnectionType,
    MoneroSubmitTxResult, MoneroOutputDistributionEntry, MoneroOutputHistogramEntry,
    MoneroTxPoolStats, MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroFeeEstimate, MoneroDaemonInfo, MoneroNetworkType, MoneroDaemonSyncInfo,
    MoneroHardForkInfo, MoneroGenerateBlocksResult, MoneroTx, MoneroKeyImage,
    MoneroOutput, MoneroBlockHeader, MoneroBlock, TxHeightComparator,
    MoneroMinerData, MoneroDaemonNetworkStats, MoneroAuxiliaryPow,
    MoneroAddAuxiliaryPowResult, MoneroGetBlocksByHashResult, MoneroGetBlockHashesResult
)
from utils import BaseTestClass, AssertUtils

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModel")


@pytest.mark.unit
class TestMoneroDaemonModel(BaseTestClass):
    """Test monero daemon data models' deserialize() (from_property_tree) round trips."""

    #region Common / rpc models

    def test_version_deserialize(self) -> None:
        version: MoneroVersion = MoneroVersion()
        version.number = 65552
        version.is_release = True
        AssertUtils.assert_serialization_integrity(version)

    def test_rpc_payment_info_deserialize(self) -> None:
        info: MoneroRpcPaymentInfo = MoneroRpcPaymentInfo()
        info.credits = 42
        info.top_block_hash = "a" * 64
        AssertUtils.assert_serialization_integrity(info)

    def test_rpc_connection_deserialize(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection("http://127.0.0.1:18081", "user", "pass", "127.0.0.1:9050", "tcp://127.0.0.1:18083", 2, 5000)
        json_str: str = connection.serialize()
        logger.debug(f"Serialized rpc connection: {json_str}")
        restored: MoneroRpcConnection = MoneroRpcConnection.deserialize(json_str)
        assert restored.uri == connection.uri
        assert restored.username == connection.username
        assert restored.password == connection.password
        assert restored.proxy_uri == connection.proxy_uri
        assert restored.zmq_uri == connection.zmq_uri

    def test_rpc_connection_priority_and_timeout_deserialize(self) -> None:
        # to_rapidjson_val() emits "priority" and "timeoutMs" but
        # from_property_tree() never read either back
        connection: MoneroRpcConnection = MoneroRpcConnection("http://127.0.0.1:18081", priority=2, timeout_ms=5000)
        json_str: str = connection.serialize()
        logger.debug(f"Serialized rpc connection: {json_str}")
        assert '"priority"' in json_str and '"timeoutMs"' in json_str
        restored: MoneroRpcConnection = MoneroRpcConnection.deserialize(json_str)
        logger.debug(f"Deserialized rpc connection re-serialized: {restored.serialize()}")
        assert restored.priority == connection.priority
        assert restored.timeout_ms == connection.timeout_ms

    #endregion

    #region Blockchain / mining models

    def test_alt_chain_deserialize(self) -> None:
        alt_chain: MoneroAltChain = MoneroAltChain()
        alt_chain.block_hashes = ["a" * 64, "b" * 64]
        alt_chain.difficulty_low = 100
        alt_chain.difficulty_high = 0
        alt_chain.height = 12345
        alt_chain.length = 3
        alt_chain.main_chain_parent_block_hash = "c" * 64
        AssertUtils.assert_serialization_integrity(alt_chain)

    def test_ban_deserialize(self) -> None:
        ban: MoneroBan = MoneroBan()
        ban.host = "127.0.0.1"
        ban.ip = 2130706433
        ban.is_banned = True
        ban.seconds = 3600
        AssertUtils.assert_serialization_integrity(ban)

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

    def test_mining_status_deserialize(self) -> None:
        status: MoneroMiningStatus = MoneroMiningStatus()
        status.is_active = True
        status.is_background = False
        status.address = "9" + "a" * 94
        status.speed = 500
        status.num_threads = 4
        AssertUtils.assert_serialization_integrity(status)

    def test_miner_tx_sum_deserialize(self) -> None:
        summ: MoneroMinerTxSum = MoneroMinerTxSum()
        summ.emission_sum_low = 1000
        summ.emission_sum_high = 0
        summ.fee_sum_low = 10
        summ.fee_sum_high = 0
        AssertUtils.assert_serialization_integrity(summ)

    def test_block_template_deserialize(self) -> None:
        template: MoneroBlockTemplate = MoneroBlockTemplate()
        template.block_template_blob = "abcd"
        template.block_hashing_blob = "ef01"
        template.prev_hash = "a" * 64
        template.seed_hash = "b" * 64
        template.next_seed_hash = "c" * 64
        template.difficulty_low = 5000
        template.difficulty_high = 0
        template.expected_reward = 600000000000
        template.height = 12345
        template.reserved_offset = 130
        template.seed_height = 0
        AssertUtils.assert_serialization_integrity(template)

    def test_block_header_deserialize(self) -> None:
        header: MoneroBlockHeader = MoneroBlockHeader()
        header.hash = "a" * 64
        header.height = 12345
        header.timestamp = 1600000000
        header.size = 2048
        header.weight = 2048
        header.long_term_weight = 2048
        header.depth = 10
        header.difficulty_low = 5000
        header.difficulty_high = 0
        header.cumulative_difficulty_low = 900000
        header.cumulative_difficulty_high = 0
        header.major_version = 16
        header.minor_version = 16
        header.nonce = 42
        header.miner_tx_hash = "b" * 64
        header.num_txs = 3
        header.orphan_status = False
        header.prev_hash = "c" * 64
        header.reward = 600000000000
        header.pow_hash = "d" * 64
        AssertUtils.assert_serialization_integrity(header)

    def test_block_deserialize(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.hash = "a" * 64
        block.height = 12345
        block.hex = "deadbeef"
        block.tx_hashes = ["b" * 64, "c" * 64]
        AssertUtils.assert_serialization_integrity(block)

    def test_connection_span_deserialize(self) -> None:
        span: MoneroConnectionSpan = MoneroConnectionSpan()
        span.connection_id = "deadbeef"
        span.remote_address = "127.0.0.1:18080"
        span.num_blocks = 10
        span.rate = 100
        span.speed = 200
        span.size = 1024
        span.start_height = 1000
        AssertUtils.assert_serialization_integrity(span)

    def test_peer_deserialize(self) -> None:
        peer: MoneroPeer = MoneroPeer()
        peer.id = "1122334455667788"
        peer.address = "127.0.0.1:18080"
        peer.host = "127.0.0.1"
        peer.port = 18080
        peer.last_seen_timestamp = 1700000000
        peer.pruning_seed = 0
        peer.rpc_port = 18081
        peer.rpc_credits_per_hash = 0
        peer.hash = "a" * 64
        peer.avg_download = 10
        peer.avg_upload = 20
        peer.current_download = 30
        peer.current_upload = 40
        peer.height = 12345
        peer.is_incoming = True
        peer.live_time = 3600
        peer.is_local_ip = False
        peer.is_local_host = False
        peer.num_receives = 5
        peer.num_sends = 6
        peer.receive_idle_time = 7
        peer.send_idle_time = 8
        peer.state = "normal"
        peer.num_support_flags = 1
        # is_online and connection_type are serialized (isOnline/addressType) but
        # monero_peer::from_property_tree() never reads them back, so they are
        # deliberately excluded from this round trip (see test below).
        AssertUtils.assert_serialization_integrity(peer)

    def test_peer_is_online_deserialize(self) -> None:
        peer: MoneroPeer = MoneroPeer()
        peer.is_online = True
        json_str: str = peer.serialize()
        logger.debug(f"Serialized peer: {json_str}")
        assert "isOnline" in json_str
        restored: MoneroPeer = MoneroPeer.deserialize(json_str)
        logger.debug(f"Deserialized peer re-serialized: {restored.serialize()}")
        assert restored.is_online == peer.is_online

    def test_peer_connection_serialization_integrity(self) -> None:
        peer: MoneroPeer = MoneroPeer()
        peer.connection_type = MoneroConnectionType.IPV6
        json_str: str = peer.serialize()
        logger.debug(f"Serialized peer: {json_str}")
        assert "addressType" in json_str
        restored: MoneroPeer = MoneroPeer.deserialize(json_str)
        logger.debug(f"Deserialized peer re-serialized: {restored.serialize()}")
        assert restored.connection_type == peer.connection_type

    def test_peer_connection_type_deserialize(self) -> None:
        # connection_type is likewise never serialized by to_rapidjson_val(), so it
        # can only be exercised by handing from_property_tree a raw "addressType" field
        for value, expected in [
            (0, MoneroConnectionType.INVALID),
            (1, MoneroConnectionType.IPV4),
            (2, MoneroConnectionType.IPV6),
            (3, MoneroConnectionType.TOR),
            (4, MoneroConnectionType.I2P),
        ]:
            peer: MoneroPeer = MoneroPeer.deserialize(f'{{"addressType":{value}}}')
            assert peer.connection_type == expected

    def test_peer_connection_type_invalid(self) -> None:
        # TODO throws RuntimeError rather than MoneroError
        with pytest.raises(RuntimeError, match="Invalid RPC peer type"):
            MoneroPeer.deserialize('{"addressType":5}')

    def test_submit_tx_result_deserialize(self) -> None:
        result: MoneroSubmitTxResult = MoneroSubmitTxResult()
        result.credits = 1
        result.top_block_hash = "a" * 64
        result.is_relayed = True
        result.is_double_spend = False
        result.is_fee_too_low = False
        result.has_invalid_input = False
        result.has_invalid_output = False
        result.has_too_few_outputs = False
        result.is_mixin_too_low = False
        result.is_overspend = False
        result.reason = "ok"
        result.is_too_big = False
        result.sanity_check_failed = False
        result.is_tx_extra_too_big = False
        result.is_nonzero_unlock_time = False
        # is_good is serialized but never read back by from_property_tree()
        AssertUtils.assert_serialization_integrity(result)

    def test_submit_tx_result_is_good_deserialize(self) -> None:
        result: MoneroSubmitTxResult = MoneroSubmitTxResult()
        result.is_good = True
        json_str: str = result.serialize()
        logger.debug(f"Serialized submit tx result: {json_str}")
        assert "isGood" in json_str
        restored: MoneroSubmitTxResult = MoneroSubmitTxResult.deserialize(json_str)
        logger.debug(f"Deserialized submit tx result re-serialized: {restored.serialize()}")
        assert restored.is_good == result.is_good

    def test_output_distribution_entry_deserialize(self) -> None:
        entry: MoneroOutputDistributionEntry = MoneroOutputDistributionEntry()
        entry.amount = 0
        entry.base = 100
        entry.distribution = [1, 2, 3, 4]
        entry.start_height = 0
        AssertUtils.assert_serialization_integrity(entry)

    def test_output_histogram_entry_deserialize(self) -> None:
        entry: MoneroOutputHistogramEntry = MoneroOutputHistogramEntry()
        entry.amount = 0
        entry.num_instances = 10
        entry.unlocked_instances = 8
        entry.recent_instances = 2
        AssertUtils.assert_serialization_integrity(entry)

    def test_tx_pool_stats_deserialize(self) -> None:
        stats: MoneroTxPoolStats = MoneroTxPoolStats()
        stats.num_txs = 5
        stats.num_not_relayed = 1
        stats.num_failing = 0
        stats.num_double_spends = 0
        stats.num10m = 2
        stats.fee_total = 1000
        stats.bytes_max = 2000
        stats.bytes_med = 1500
        stats.bytes_min = 1000
        stats.bytes_total = 5000
        stats.histo98pc = 1800
        stats.oldest_timestamp = 1700000000
        # histo is serialized as an object but from_property_tree() has a TODO
        # and never reads it back into the map
        AssertUtils.assert_serialization_integrity(stats)

    def test_tx_pool_stats_histo_deserialize(self) -> None:
        stats: MoneroTxPoolStats = MoneroTxPoolStats()
        stats.histo = {100: 1, 200: 2}
        json_str: str = stats.serialize()
        logger.debug(f"Serialized tx pool stats: {json_str}")
        assert "histo" in json_str
        restored: MoneroTxPoolStats = MoneroTxPoolStats.deserialize(json_str)
        logger.debug(f"Deserialized tx pool stats re-serialized: {restored.serialize()}")
        assert dict(restored.histo) == dict(stats.histo)

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

    def test_generate_blocks_result_deserialize(self) -> None:
        result: MoneroGenerateBlocksResult = MoneroGenerateBlocksResult()
        result.block_hashes = ["a" * 64, "b" * 64]
        result.height = 12345
        AssertUtils.assert_serialization_integrity(result)

    def test_miner_data_deserialize(self) -> None:
        data: MoneroMinerData = MoneroMinerData()
        data.credits = 0
        data.top_block_hash = "a" * 64
        data.major_version = 16
        data.height = 3000000
        data.prev_hash = "b" * 64
        data.seed_hash = "c" * 64
        data.difficulty = "0x1f4"  # daemon reports difficulty as a hex string
        data.median_weight = 300000
        data.already_generated_coins = 5646232813355588
        tx: MoneroTx = MoneroTx()
        tx.hash = "d" * 64
        tx.fee = 10000
        data.tx_pool_backlog = [tx]
        AssertUtils.assert_serialization_integrity(data)

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

    def test_auxiliary_pow_deserialize(self) -> None:
        aux_pow: MoneroAuxiliaryPow = MoneroAuxiliaryPow("a" * 64, "b" * 64)
        assert aux_pow.id == "a" * 64
        assert aux_pow.hash == "b" * 64
        AssertUtils.assert_serialization_integrity(aux_pow)

    def test_add_auxiliary_pow_result_deserialize(self) -> None:
        result: MoneroAddAuxiliaryPowResult = MoneroAddAuxiliaryPowResult()
        result.credits = 0
        result.top_block_hash = "a" * 64
        result.block_template_blob = "abcd"
        result.block_hashing_blob = "ef01"
        result.merkle_root = "b" * 64
        result.merkle_tree_depth = 2
        result.aux_pow = [MoneroAuxiliaryPow("c" * 64, "d" * 64)]
        AssertUtils.assert_serialization_integrity(result)

    def test_get_block_hashes_result_deserialize(self) -> None:
        result: MoneroGetBlockHashesResult = MoneroGetBlockHashesResult()
        result.hashes = ["a" * 64, "b" * 64]
        result.start_height = 100
        result.current_height = 3000000
        AssertUtils.assert_serialization_integrity(result)

    def test_get_blocks_by_hash_result_deserialize(self) -> None:
        result: MoneroGetBlocksByHashResult = MoneroGetBlocksByHashResult()
        result.current_height = 3000000
        # blocks are serialized but from_property_tree() never reads them back
        # (monero_block has no from_property_tree of its own); see test below
        AssertUtils.assert_serialization_integrity(result)

    def test_get_blocks_by_hash_result_blocks_deserialize(self) -> None:
        result: MoneroGetBlocksByHashResult = MoneroGetBlocksByHashResult()
        block: MoneroBlock = MoneroBlock()
        block.hash = "a" * 64
        block.height = 100
        result.blocks = [block]
        json_str: str = result.serialize()
        logger.debug(f"Serialized get blocks by hash result: {json_str}")
        assert '"blocks"' in json_str
        restored: MoneroGetBlocksByHashResult = MoneroGetBlocksByHashResult.deserialize(json_str)
        assert len(restored.blocks) == 0

    #endregion

    #region Tx / output / key image

    def test_key_image_deserialize(self) -> None:
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        AssertUtils.assert_serialization_integrity(key_image)

    def test_key_image_deserialize_key_images(self) -> None:
        json_str: str = (
            '{"keyImages": ['
            '{"hex": "' + "a" * 64 + '", "signature": "' + "b" * 128 + '"}, '
            '{"hex": "' + "c" * 64 + '"}'
            ']}'
        )
        key_images: list[MoneroKeyImage] = MoneroKeyImage.deserialize_key_images(json_str)
        assert len(key_images) == 2
        assert key_images[0].hex == "a" * 64
        assert key_images[0].signature == "b" * 128
        assert key_images[1].hex == "c" * 64
        assert key_images[1].signature is None

        # a missing or empty keyImages array yields no key images
        assert MoneroKeyImage.deserialize_key_images("{}") == []
        assert MoneroKeyImage.deserialize_key_images('{"keyImages": []}') == []

        # an empty string is not valid json
        with pytest.raises(Exception):
            MoneroKeyImage.deserialize_key_images("")

    def test_output_deserialize(self) -> None:
        output: MoneroOutput = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        output.key_image = key_image
        AssertUtils.assert_serialization_integrity(output)

    def test_output_ring_output_indices_and_stealth_public_key_deserialize(self) -> None:
        output: MoneroOutput = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        output.ring_output_indices = [10, 20, 30]
        output.stealth_public_key = "a" * 64
        output.mask = "b" * 64
        AssertUtils.assert_serialization_integrity(output)

    def test_tx_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_miner_tx = False
        tx.payment_id = "b" * 16
        tx.fee = 7500000
        tx.relay = True
        tx.is_relayed = True
        tx.is_confirmed = True
        tx.in_tx_pool = False
        tx.is_locked = False
        tx.num_confirmations = 10
        tx.unlock_time = 0
        tx.last_relayed_timestamp = 1700000000
        tx.received_timestamp = 1700000000
        tx.is_double_spend_seen = False
        tx.key = "c" * 64
        tx.full_hex = "deadbeef"
        tx.pruned_hex = "deadbeef"
        tx.prunable_hex = "deadbeef"
        tx.prunable_hash = "d" * 64
        tx.size = 1500
        tx.weight = 1500
        tx.metadata = "meta"
        tx.is_kept_by_block = False
        tx.is_failed = False
        tx.last_failed_hash = "e" * 64
        tx.max_used_block_hash = "f" * 64
        # mixin, rctSignatures, rctSigPrunable and signatures are still left
        # unimplemented in from_property_tree() (see below)
        AssertUtils.assert_serialization_integrity(tx)

    @pytest.mark.parametrize("json_fragment", [
        '{"mixin":5}',
        '{"rctSignatures":"x"}',
        '{"rctSigPrunable":"x"}',
        '{"signatures":["x"]}',
    ])
    def test_tx_unimplemented_fields(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroTx.deserialize(json_fragment)

    def test_tx_version_common_tx_sets_last_failed_and_max_used_block_height_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.version = 2
        tx.common_tx_sets = "sets"
        tx.last_failed_height = 100
        tx.max_used_block_height = 200
        AssertUtils.assert_serialization_integrity(tx)

    def test_tx_ring_size_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.ring_size = 16
        AssertUtils.assert_serialization_integrity(tx)

    def test_tx_extra_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.extra = [1, 2, 3, 255]
        AssertUtils.assert_serialization_integrity(tx)

    def test_tx_inputs_outputs_and_output_indices_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.output_indices = [100, 101]
        vin: MoneroOutput = MoneroOutput()
        vin.amount = 1
        vin.key_image = MoneroKeyImage()
        vin.key_image.hex = "a" * 64
        tx.inputs = [vin]
        vout: MoneroOutput = MoneroOutput()
        vout.amount = 2
        vout.index = 0
        tx.outputs = [vout]
        AssertUtils.assert_serialization_integrity(tx)

    #endregion

    #region Copy / merge / comparators

    def test_block_header_copy(self) -> None:
        header: MoneroBlockHeader = MoneroBlockHeader()
        header.hash = "a" * 64
        header.height = 100
        header.timestamp = 1700000000
        header.size = 1000
        header.weight = 1000
        header.major_version = 16
        header.minor_version = 16
        header.nonce = 12345
        header.reward = 600000000000

        copy: MoneroBlockHeader = header.copy()
        assert copy is not header
        assert copy.serialize() == header.serialize()

        # copy is independent of the original
        copy.height = 999
        assert header.height == 100

    def test_block_header_merge(self) -> None:
        a: MoneroBlockHeader = MoneroBlockHeader()
        a.hash = "a" * 64
        a.height = 100
        a.timestamp = 1700000000

        b: MoneroBlockHeader = a.copy()
        b.height = 200             # height can increase -> resolves to the higher value
        b.timestamp = 1800000000   # timestamp can increase -> resolves to the higher value
        b.size = 2000              # a.size is unset -> merge fills the gap

        a.merge(b)
        assert a.height == 200
        assert a.timestamp == 1800000000
        assert a.size == 2000
        assert a.hash == "a" * 64

    def test_block_header_merge_conflict_raises(self) -> None:
        # fields without special reconciliation (e.g. hash) must match on both
        # sides, or merge() raises rather than silently picking one
        a: MoneroBlockHeader = MoneroBlockHeader()
        a.hash = "a" * 64
        b: MoneroBlockHeader = MoneroBlockHeader()
        b.hash = "b" * 64
        with pytest.raises(Exception, match="[Cc]annot reconcile"):
            a.merge(b)

    def test_block_copy(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.hash = "a" * 64
        block.height = 100
        block.hex = "deadbeef"
        block.tx_hashes = ["b" * 64, "c" * 64]

        copy: MoneroBlock = block.copy()
        assert copy is not block
        assert copy.serialize() == block.serialize()

    def test_block_merge(self) -> None:
        a: MoneroBlock = MoneroBlock()
        a.hash = "a" * 64
        a.height = 100
        b: MoneroBlock = a.copy()
        b.hex = "deadbeef"  # a.hex is unset -> merge fills the gap
        a.merge(b)
        assert a.hex == "deadbeef"

    def test_block_merge_txs_with_unset_hash_are_kept_distinct(self) -> None:
        script: LiteralString = (
            "import monero, sys\n"
            "a = monero.MoneroBlock()\n"
            "a.height = 100\n"
            "tx_a = monero.MoneroTx()\n"  # hash intentionally left unset
            "a.txs = [tx_a]\n"
            "b = monero.MoneroBlock()\n"
            "b.height = 100\n"
            "tx_b = monero.MoneroTx()\n"  # hash intentionally left unset
            "b.txs = [tx_b]\n"
            "a.merge(b)\n"
            "n = len(a.txs) if a.txs else 0\n"
            "sys.exit(0 if n == 2 else f'txs not kept distinct: len={n}')\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"Block.merge() did not keep unset-hash txs distinct (exit code {result.returncode}): "
            f"{result.stderr.strip()[-300:]}"
        )

    def test_tx_copy(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_confirmed = True
        tx.fee = 7500000

        copy: MoneroTx = tx.copy()
        assert copy is not tx
        assert copy.serialize() == tx.serialize()

    def test_tx_merge(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        a.fee = 7500000

        b: MoneroTx = a.copy()
        b.num_confirmations = 5  # a.num_confirmations is unset -> merge fills the gap
        a.merge(b)
        assert a.num_confirmations == 5

    def test_tx_merge_is_confirmed_can_become_true(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = False
        b: MoneroTx = a.copy()
        b.is_confirmed = True
        a.merge(b)
        assert a.is_confirmed is True

    def test_tx_merge_is_double_spend_seen_can_become_true(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_double_spend_seen = False
        b: MoneroTx = a.copy()
        b.is_double_spend_seen = True
        a.merge(b)
        assert a.is_double_spend_seen is True

    def test_tx_merge_in_tx_pool_can_become_true(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = False
        a.in_tx_pool = False
        b: MoneroTx = a.copy()
        b.in_tx_pool = True
        a.merge(b)
        assert a.in_tx_pool is True

    def test_tx_merge_is_locked_can_become_false(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_locked = False  # self: already unlocked
        b: MoneroTx = a.copy()
        b.is_locked = True   # other: still locked
        a.merge(b)
        assert a.is_locked is False

    def test_key_image_copy(self) -> None:
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128

        copy: MoneroKeyImage = key_image.copy()
        assert copy is not key_image
        assert copy.serialize() == key_image.serialize()

    def test_key_image_merge(self) -> None:
        a: MoneroKeyImage = MoneroKeyImage()
        a.hex = "a" * 64
        b: MoneroKeyImage = a.copy()
        b.signature = "b" * 128  # a.signature is unset -> merge fills the gap
        a.merge(b)
        assert a.signature == "b" * 128

    def test_output_copy(self) -> None:
        output: MoneroOutput = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        output.key_image = key_image

        copy: MoneroOutput = output.copy()
        assert copy is not output
        assert copy.key_image is not output.key_image  # key_image is deep copied
        assert copy.serialize() == output.serialize()

    def test_output_merge(self) -> None:
        a: MoneroOutput = MoneroOutput()
        a.amount = 1000000
        a.index = 5
        b: MoneroOutput = a.copy()  # preserves the (unset) tx reference, so merge won't recurse into tx merge
        b.key_image = MoneroKeyImage()
        b.key_image.hex = "a" * 64
        a.merge(b)  # a.key_image is unset -> merge adopts b's key_image
        assert a.key_image is not None
        assert a.key_image.hex == "a" * 64

    def test_tx_merge_extra_and_output_indices(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        b: MoneroTx = a.copy()
        b.extra = [1, 2, 3, 255]
        b.output_indices = [100, 101]
        a.merge(b)  # a.extra/output_indices are unset -> merge should adopt b's
        assert a.extra == [1, 2, 3, 255]
        assert a.output_indices == [100, 101]

    def test_output_merge_ring_output_indices_and_stealth_public_key(self) -> None:
        a: MoneroOutput = MoneroOutput()
        a.amount = 1000000
        a.index = 5
        b: MoneroOutput = a.copy()  # preserves the (unset) tx reference, so merge won't recurse into tx merge
        b.ring_output_indices = [10, 20, 30]
        b.stealth_public_key = "a" * 64
        b.mask = "b" * 64
        a.merge(b)  # a's fields are unset -> merge should adopt b's
        assert a.ring_output_indices == [10, 20, 30]
        assert a.stealth_public_key == "a" * 64
        assert a.mask == "b" * 64

    def test_tx_lt_height_comparator(self) -> None:
        tx_a: MoneroTx = MoneroTx()
        tx_a.block = MoneroBlock()
        tx_a.block.height = 100

        tx_b: MoneroTx = MoneroTx()
        tx_b.block = MoneroBlock()
        tx_b.block.height = 200

        assert tx_a < tx_b
        assert not (tx_b < tx_a)
        assert TxHeightComparator.compare(tx_a, tx_b)
        assert not TxHeightComparator.compare(tx_b, tx_a)

        txs: list[MoneroTx] = [tx_b, tx_a]
        txs.sort()
        assert txs[0] is tx_a
        assert txs[1] is tx_b

        # unconfirmed (no block) transactions sort after confirmed ones
        tx_unconfirmed: MoneroTx = MoneroTx()
        assert tx_a < tx_unconfirmed
        assert not (tx_unconfirmed < tx_a)

    #endregion
