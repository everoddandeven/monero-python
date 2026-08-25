import pytest
import logging
import subprocess
import sys

from monero import (
    MoneroVersion, MoneroRpcPaymentInfo, MoneroRpcConnection, MoneroAltChain,
    MoneroBan, MoneroPruneResult, MoneroMiningStatus, MoneroMinerTxSum,
    MoneroBlockTemplate, MoneroConnectionSpan, MoneroPeer, MoneroConnectionType,
    MoneroSubmitTxResult, MoneroOutputDistributionEntry, MoneroOutputHistogramEntry,
    MoneroTxPoolStats, MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroFeeEstimate, MoneroDaemonInfo, MoneroNetworkType, MoneroDaemonSyncInfo,
    MoneroHardForkInfo, MoneroGenerateBlocksResult, MoneroTx, MoneroKeyImage,
    MoneroOutput, MoneroBlockHeader, MoneroBlock, TxHeightComparator
)
from utils import BaseTestClass, AssertUtils

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModel")


@pytest.mark.unit
class TestMoneroDaemonModel(BaseTestClass):
    """Test monero daemon data models' deserialize() (from_property_tree) round trips."""

    #region Common / rpc models

    def test_version_deserialize(self) -> None:
        version = MoneroVersion()
        version.number = 65552
        version.is_release = True
        AssertUtils.assert_serialization_integrity(version)

    def test_rpc_payment_info_deserialize(self) -> None:
        info = MoneroRpcPaymentInfo()
        info.credits = 42
        info.top_block_hash = "a" * 64
        AssertUtils.assert_serialization_integrity(info)

    def test_rpc_connection_deserialize(self) -> None:
        connection = MoneroRpcConnection("http://127.0.0.1:18081", "user", "pass", "127.0.0.1:9050", "tcp://127.0.0.1:18083", 2, 5000)
        json_str = connection.serialize()
        logger.debug(f"Serialized rpc connection: {json_str}")
        restored = MoneroRpcConnection.deserialize(json_str)
        assert restored.uri == connection.uri
        assert restored.username == connection.username
        assert restored.password == connection.password
        assert restored.proxy_uri == connection.proxy_uri
        assert restored.zmq_uri == connection.zmq_uri

    @pytest.mark.xfail(reason="monero_rpc_connection::from_property_tree() doesn't read back priority/timeoutMs; fixed upstream in the local everoddandeven/monero-cpp checkout, pending a submodule bump", strict=True)
    def test_rpc_connection_priority_and_timeout_deserialize(self) -> None:
        # to_rapidjson_val() emits "priority" and "timeoutMs" but
        # from_property_tree() never read either back
        connection = MoneroRpcConnection("http://127.0.0.1:18081", priority=2, timeout_ms=5000)
        json_str = connection.serialize()
        logger.debug(f"Serialized rpc connection: {json_str}")
        assert '"priority"' in json_str and '"timeoutMs"' in json_str
        restored = MoneroRpcConnection.deserialize(json_str)
        logger.debug(f"Deserialized rpc connection re-serialized: {restored.serialize()}")
        assert restored.priority == connection.priority
        assert restored.timeout_ms == connection.timeout_ms

    #endregion

    #region Blockchain / mining models

    def test_alt_chain_deserialize(self) -> None:
        alt_chain = MoneroAltChain()
        alt_chain.block_hashes = ["a" * 64, "b" * 64]
        alt_chain.difficulty_low = 100
        alt_chain.difficulty_high = 0
        alt_chain.height = 12345
        alt_chain.length = 3
        alt_chain.main_chain_parent_block_hash = "c" * 64
        AssertUtils.assert_serialization_integrity(alt_chain)

    def test_ban_deserialize(self) -> None:
        ban = MoneroBan()
        ban.host = "127.0.0.1"
        ban.ip = 2130706433
        ban.is_banned = True
        ban.seconds = 3600
        AssertUtils.assert_serialization_integrity(ban)

    def test_prune_result_deserialize(self) -> None:
        result = MoneroPruneResult()
        result.pruning_seed = 387
        # is_pruned is deliberately not set here: to_rapidjson_val() serializes it
        # under "isPruned" but from_property_tree() looks for "pruned" instead, so
        # it never round trips (see test below)
        AssertUtils.assert_serialization_integrity(result)

    @pytest.mark.xfail(reason="monero_prune_result::from_property_tree() bug", strict=True)
    def test_prune_result_is_pruned_deserialize(self) -> None:
        result = MoneroPruneResult()
        result.is_pruned = True
        json_str = result.serialize()
        logger.debug(f"Serialized prune result: {json_str}")
        assert '"isPruned"' in json_str
        restored = MoneroPruneResult.deserialize(json_str)
        logger.debug(f"Deserialized prune result re-serialized: {restored.serialize()}")
        assert restored.is_pruned == result.is_pruned

    def test_mining_status_deserialize(self) -> None:
        status = MoneroMiningStatus()
        status.is_active = True
        status.is_background = False
        status.address = "9" + "a" * 94
        status.speed = 500
        status.num_threads = 4
        AssertUtils.assert_serialization_integrity(status)

    def test_miner_tx_sum_deserialize(self) -> None:
        summ = MoneroMinerTxSum()
        summ.emission_sum_low = 1000
        summ.emission_sum_high = 0
        summ.fee_sum_low = 10
        summ.fee_sum_high = 0
        AssertUtils.assert_serialization_integrity(summ)

    def test_block_template_deserialize(self) -> None:
        template = MoneroBlockTemplate()
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

    def test_connection_span_deserialize(self) -> None:
        span = MoneroConnectionSpan()
        span.connection_id = "deadbeef"
        span.remote_address = "127.0.0.1:18080"
        span.num_blocks = 10
        span.rate = 100
        span.speed = 200
        span.size = 1024
        span.start_height = 1000
        AssertUtils.assert_serialization_integrity(span)

    def test_peer_deserialize(self) -> None:
        peer = MoneroPeer()
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

    @pytest.mark.xfail(reason="monero_peer::from_property_tree() bug", strict=True)
    def test_peer_is_online_deserialize(self) -> None:
        peer = MoneroPeer()
        peer.is_online = True
        json_str = peer.serialize()
        logger.debug(f"Serialized peer: {json_str}")
        assert "isOnline" in json_str
        restored = MoneroPeer.deserialize(json_str)
        logger.debug(f"Deserialized peer re-serialized: {restored.serialize()}")
        assert restored.is_online == peer.is_online

    @pytest.mark.xfail(reason="monero_peer::to_rapidjson_val() bug/monero-cpp checkout", strict=True)
    def test_peer_connection_serialization_integrity(self) -> None:
        peer = MoneroPeer()
        peer.connection_type = MoneroConnectionType.IPV6
        json_str = peer.serialize()
        logger.debug(f"Serialized peer: {json_str}")
        assert "addressType" in json_str
        restored = MoneroPeer.deserialize(json_str)
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
            peer = MoneroPeer.deserialize(f'{{"addressType":{value}}}')
            assert peer.connection_type == expected

    def test_peer_connection_type_invalid(self) -> None:
        # TODO throws RuntimeError rather than MoneroError
        with pytest.raises(RuntimeError, match="Invalid RPC peer type"):
            MoneroPeer.deserialize('{"addressType":5}')

    def test_submit_tx_result_deserialize(self) -> None:
        result = MoneroSubmitTxResult()
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

    @pytest.mark.xfail(reason="monero_submit_tx_result::from_property_tree() bug", strict=True)
    def test_submit_tx_result_is_good_deserialize(self) -> None:
        result = MoneroSubmitTxResult()
        result.is_good = True
        json_str = result.serialize()
        logger.debug(f"Serialized submit tx result: {json_str}")
        assert "isGood" in json_str
        restored = MoneroSubmitTxResult.deserialize(json_str)
        logger.debug(f"Deserialized submit tx result re-serialized: {restored.serialize()}")
        assert restored.is_good == result.is_good

    def test_output_distribution_entry_deserialize(self) -> None:
        entry = MoneroOutputDistributionEntry()
        entry.amount = 0
        entry.base = 100
        entry.distribution = [1, 2, 3, 4]
        entry.start_height = 0
        AssertUtils.assert_serialization_integrity(entry)

    def test_output_histogram_entry_deserialize(self) -> None:
        entry = MoneroOutputHistogramEntry()
        entry.amount = 0
        entry.num_instances = 10
        entry.unlocked_instances = 8
        entry.recent_instances = 2
        AssertUtils.assert_serialization_integrity(entry)

    def test_tx_pool_stats_deserialize(self) -> None:
        stats = MoneroTxPoolStats()
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

    @pytest.mark.xfail(reason="monero_tx_pool_stats::from_property_tree() bug", strict=True)
    def test_tx_pool_stats_histo_deserialize(self) -> None:
        stats = MoneroTxPoolStats()
        stats.histo = {100: 1, 200: 2}
        json_str = stats.serialize()
        logger.debug(f"Serialized tx pool stats: {json_str}")
        assert "histo" in json_str
        restored = MoneroTxPoolStats.deserialize(json_str)
        logger.debug(f"Deserialized tx pool stats re-serialized: {restored.serialize()}")
        assert dict(restored.histo) == dict(stats.histo)

    def test_daemon_update_check_result_deserialize(self) -> None:
        result = MoneroDaemonUpdateCheckResult()
        result.is_update_available = True
        result.version = "0.18.5.1"
        result.hash = "a" * 64
        result.auto_uri = "https://example.com/auto"
        result.user_uri = "https://example.com/user"
        AssertUtils.assert_serialization_integrity(result)

    def test_daemon_update_download_result_deserialize(self) -> None:
        result = MoneroDaemonUpdateDownloadResult()
        result.is_update_available = True
        result.version = "0.18.5.1"
        result.hash = "a" * 64
        result.auto_uri = "https://example.com/auto"
        result.user_uri = "https://example.com/user"
        result.download_path = "/tmp/update.bin"
        AssertUtils.assert_serialization_integrity(result)

    def test_fee_estimate_deserialize(self) -> None:
        estimate = MoneroFeeEstimate()
        estimate.fee = 20000
        estimate.quantization_mask = 10000
        estimate.fees = [10000, 20000, 30000, 40000]
        AssertUtils.assert_serialization_integrity(estimate)

    def test_daemon_info_deserialize(self) -> None:
        info = MoneroDaemonInfo()
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
        AssertUtils.assert_serialization_integrity(info)

    def test_daemon_info_invalid_network_type(self) -> None:
        with pytest.raises(RuntimeError, match="invalid network type"):
            MoneroDaemonInfo.deserialize('{"networkType":9}')

    def test_daemon_sync_info_deserialize(self) -> None:
        info = MoneroDaemonSyncInfo()
        info.credits = 0
        info.top_block_hash = "a" * 64
        info.height = 3000000
        info.target_height = 3000010
        info.next_needed_pruning_seed = 0
        info.overview = "syncing"
        # peers/spans are serialized as sub-arrays but from_property_tree() never
        # reads them back (see test below)
        AssertUtils.assert_serialization_integrity(info)

    @pytest.mark.xfail(reason="monero_daemon_sync_info::from_property_tree() bug", strict=True)
    def test_daemon_sync_info_peers_and_spans_deserialize(self) -> None:
        info = MoneroDaemonSyncInfo()
        info.peers = [MoneroPeer()]
        info.spans = [MoneroConnectionSpan()]
        json_str = info.serialize()
        logger.debug(f"Serialized daemon sync info: {json_str}")
        assert "peers" in json_str and "spans" in json_str
        restored = MoneroDaemonSyncInfo.deserialize(json_str)
        logger.debug(f"Deserialized daemon sync info re-serialized: {restored.serialize()}")
        assert len(restored.peers) == len(info.peers)
        assert len(restored.spans) == len(info.spans)

    def test_hard_fork_info_deserialize(self) -> None:
        info = MoneroHardForkInfo()
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
        result = MoneroGenerateBlocksResult()
        result.block_hashes = ["a" * 64, "b" * 64]
        result.height = 12345
        AssertUtils.assert_serialization_integrity(result)

    #endregion

    #region Tx / output / key image

    def test_key_image_deserialize(self) -> None:
        key_image = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        AssertUtils.assert_serialization_integrity(key_image)

    def test_output_deserialize(self) -> None:
        output = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        key_image = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        output.key_image = key_image
        # ring_output_indices / stealth_public_key raise "not implemented" (see below)
        AssertUtils.assert_serialization_integrity(output)

    def test_output_ring_output_indices_not_implemented(self) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroOutput.deserialize('{"ringOutputIndices":[1,2,3]}')

    def test_output_stealth_public_key_not_implemented(self) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroOutput.deserialize('{"stealthPublicKey":"' + "a" * 64 + '"}')

    @pytest.mark.xfail(reason="monero_output::from_property_tree() bug", strict=True)
    def test_output_ring_output_indices_and_stealth_public_key_deserialize(self) -> None:
        output = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        output.ring_output_indices = [10, 20, 30]
        output.stealth_public_key = "a" * 64
        AssertUtils.assert_serialization_integrity(output)

    def test_tx_deserialize(self) -> None:
        tx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_miner_tx = False
        tx.payment_id = "b" * 16
        tx.fee = 7500000
        tx.relay = True
        tx.is_relayed = True
        tx.is_confirmed = True
        tx.in_tx_pool = False
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
        # version, inputs, outputs, outputIndices, commonTxSets, extra,
        # rctSignatures, rctSigPrunable, lastFailedHeight, maxUsedBlockHeight and
        # signatures are all left unimplemented in from_property_tree() (see below)
        AssertUtils.assert_serialization_integrity(tx)

    @pytest.mark.parametrize("json_fragment", [
        '{"version":1}',
        '{"mixin":5}',
        '{"inputs":[]}',
        '{"outputs":[]}',
        '{"outputIndices":[1]}',
        '{"commonTxSets":"x"}',
        '{"extra":[1,2,3]}',
        '{"rctSignatures":"x"}',
        '{"rctSigPrunable":"x"}',
        '{"lastFailedHeight":1}',
        '{"maxUsedBlockHeight":1}',
        '{"signatures":["x"]}',
    ])
    def test_tx_unimplemented_fields(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroTx.deserialize(json_fragment)

    @pytest.mark.xfail(reason="monero_tx::from_property_tree() bug", strict=True)
    def test_tx_version_common_tx_sets_last_failed_and_max_used_block_height_deserialize(self) -> None:
        tx = MoneroTx()
        tx.version = 2
        tx.common_tx_sets = "sets"
        tx.last_failed_height = 100
        tx.max_used_block_height = 200
        AssertUtils.assert_serialization_integrity(tx)

    @pytest.mark.xfail(reason="monero_tx::from_property_tree() bug", strict=True)
    def test_tx_ring_size_deserialize(self) -> None:
        tx = MoneroTx()
        tx.ring_size = 16
        AssertUtils.assert_serialization_integrity(tx)

    @pytest.mark.xfail(reason="monero_tx::from_property_tree() bug", strict=True)
    def test_tx_extra_deserialize(self) -> None:
        tx = MoneroTx()
        tx.extra = [1, 2, 3, 255]
        AssertUtils.assert_serialization_integrity(tx)

    @pytest.mark.xfail(reason="monero_tx::from_property_tree() bug", strict=True)
    def test_tx_inputs_outputs_and_output_indices_deserialize(self) -> None:
        tx = MoneroTx()
        tx.output_indices = [100, 101]
        vin = MoneroOutput()
        vin.amount = 1
        vin.key_image = MoneroKeyImage()
        vin.key_image.hex = "a" * 64
        tx.inputs = [vin]
        vout = MoneroOutput()
        vout.amount = 2
        vout.index = 0
        tx.outputs = [vout]
        AssertUtils.assert_serialization_integrity(tx)

    #endregion

    #region Copy / merge / comparators

    def test_block_header_copy(self) -> None:
        header = MoneroBlockHeader()
        header.hash = "a" * 64
        header.height = 100
        header.timestamp = 1700000000
        header.size = 1000
        header.weight = 1000
        header.major_version = 16
        header.minor_version = 16
        header.nonce = 12345
        header.reward = 600000000000

        copy = header.copy()
        assert copy is not header
        assert copy.serialize() == header.serialize()

        # copy is independent of the original
        copy.height = 999
        assert header.height == 100

    def test_block_header_merge(self) -> None:
        a = MoneroBlockHeader()
        a.hash = "a" * 64
        a.height = 100
        a.timestamp = 1700000000

        b = a.copy()
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
        a = MoneroBlockHeader()
        a.hash = "a" * 64
        b = MoneroBlockHeader()
        b.hash = "b" * 64
        with pytest.raises(Exception, match="[Cc]annot reconcile"):
            a.merge(b)

    def test_block_copy(self) -> None:
        block = MoneroBlock()
        block.hash = "a" * 64
        block.height = 100
        block.hex = "deadbeef"
        block.tx_hashes = ["b" * 64, "c" * 64]

        copy = block.copy()
        assert copy is not block
        assert copy.serialize() == block.serialize()

    def test_block_merge(self) -> None:
        a = MoneroBlock()
        a.hash = "a" * 64
        a.height = 100
        b = a.copy()
        b.hex = "deadbeef"  # a.hex is unset -> merge fills the gap
        a.merge(b)
        assert a.hex == "deadbeef"

    @pytest.mark.xfail(reason="merge_tx() dereferences m_hash unconditionally (boost::optional UB when unset); locally this just dedups wrongly, but the same NDEBUG/ODR-ambiguity root cause aborts the process in CI", strict=True)
    def test_block_merge_txs_with_unset_hash_are_kept_distinct(self) -> None:
        script = (
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
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"Block.merge() did not keep unset-hash txs distinct (exit code {result.returncode}): "
            f"{result.stderr.strip()[-300:]}"
        )

    def test_tx_copy(self) -> None:
        tx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_confirmed = True
        tx.fee = 7500000

        copy = tx.copy()
        assert copy is not tx
        assert copy.serialize() == tx.serialize()

    def test_tx_merge(self) -> None:
        a = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        a.fee = 7500000

        b = a.copy()
        b.num_confirmations = 5  # a.num_confirmations is unset -> merge fills the gap
        a.merge(b)
        assert a.num_confirmations == 5

    @pytest.mark.xfail(reason="gen_utils::reconcile() bug", strict=True)
    def test_tx_merge_is_confirmed_can_become_true(self) -> None:
        a = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = False
        b = a.copy()
        b.is_confirmed = True
        a.merge(b)
        assert a.is_confirmed is True

    @pytest.mark.xfail(reason="same gen_utils::reconcile() bug", strict=True)
    def test_tx_merge_is_double_spend_seen_can_become_true(self) -> None:
        a = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_double_spend_seen = False
        b = a.copy()
        b.is_double_spend_seen = True
        a.merge(b)
        assert a.is_double_spend_seen is True

    @pytest.mark.xfail(reason="same gen_utils::reconcile() bug", strict=True)
    def test_tx_merge_in_tx_pool_can_become_true(self) -> None:
        a = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = False
        a.in_tx_pool = False
        b = a.copy()
        b.in_tx_pool = True
        a.merge(b)
        assert a.in_tx_pool is True

    def test_key_image_copy(self) -> None:
        key_image = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128

        copy = key_image.copy()
        assert copy is not key_image
        assert copy.serialize() == key_image.serialize()

    def test_key_image_merge(self) -> None:
        a = MoneroKeyImage()
        a.hex = "a" * 64
        b = a.copy()
        b.signature = "b" * 128  # a.signature is unset -> merge fills the gap
        a.merge(b)
        assert a.signature == "b" * 128

    def test_output_copy(self) -> None:
        output = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        key_image = MoneroKeyImage()
        key_image.hex = "a" * 64
        output.key_image = key_image

        copy = output.copy()
        assert copy is not output
        assert copy.key_image is not output.key_image  # key_image is deep copied
        assert copy.serialize() == output.serialize()

    def test_output_merge(self) -> None:
        a = MoneroOutput()
        a.amount = 1000000
        a.index = 5
        b = a.copy()  # preserves the (unset) tx reference, so merge won't recurse into tx merge
        b.key_image = MoneroKeyImage()
        b.key_image.hex = "a" * 64
        a.merge(b)  # a.key_image is unset -> merge adopts b's key_image
        assert a.key_image is not None
        assert a.key_image.hex == "a" * 64

    @pytest.mark.xfail(reason="monero_tx::merge() bug", strict=True)
    def test_tx_merge_extra_and_output_indices(self) -> None:
        a = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        b = a.copy()
        b.extra = [1, 2, 3, 255]
        b.output_indices = [100, 101]
        a.merge(b)  # a.extra/output_indices are unset -> merge should adopt b's
        assert a.extra == [1, 2, 3, 255]
        assert a.output_indices == [100, 101]

    @pytest.mark.xfail(reason="monero_output::merge() bug", strict=True)
    def test_output_merge_ring_output_indices_and_stealth_public_key(self) -> None:
        a = MoneroOutput()
        a.amount = 1000000
        a.index = 5
        b = a.copy()  # preserves the (unset) tx reference, so merge won't recurse into tx merge
        b.ring_output_indices = [10, 20, 30]
        b.stealth_public_key = "a" * 64
        a.merge(b)  # a.ring_output_indices/stealth_public_key are unset -> merge should adopt b's
        assert a.ring_output_indices == [10, 20, 30]
        assert a.stealth_public_key == "a" * 64

    def test_tx_lt_height_comparator(self) -> None:
        tx_a = MoneroTx()
        tx_a.block = MoneroBlock()
        tx_a.block.height = 100

        tx_b = MoneroTx()
        tx_b.block = MoneroBlock()
        tx_b.block.height = 200

        assert tx_a < tx_b
        assert not (tx_b < tx_a)
        assert TxHeightComparator.compare(tx_a, tx_b)
        assert not TxHeightComparator.compare(tx_b, tx_a)

        txs = [tx_b, tx_a]
        txs.sort()
        assert txs[0] is tx_a
        assert txs[1] is tx_b

        # unconfirmed (no block) transactions sort after confirmed ones
        tx_unconfirmed = MoneroTx()
        assert tx_a < tx_unconfirmed
        assert not (tx_unconfirmed < tx_a)

    #endregion
