import logging

from abc import ABC
from typing import Optional, Union, Any
from monero import (
    MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo,
    MoneroConnectionSpan, MoneroHardForkInfo,
    MoneroAltChain, MoneroBan, MoneroMinerTxSum,
    MoneroTxPoolStats, MoneroBlockTemplate,
    MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroNetworkType, MoneroRpcConnection
)

from .gen_utils import GenUtils
from .assert_utils import AssertUtils

logger: logging.Logger = logging.getLogger("DaemonUtils")


class DaemonUtils(ABC):

    @classmethod
    def network_type_to_str(cls, nettype: MoneroNetworkType) -> str:
        if nettype == MoneroNetworkType.MAINNET:
            return "mainnet"
        elif nettype == MoneroNetworkType.TESTNET:
            return "testnet"
        elif nettype == MoneroNetworkType.STAGENET:
            return "stagenet"

        raise TypeError(f"Invalid network type provided: {str(nettype)}")

    @classmethod
    def is_regtest(cls, network_type_str: Optional[str]) -> bool:
        if network_type_str is None:
            return False
        nettype = network_type_str.lower()
        return nettype == "regtest" or nettype == "reg"

    @classmethod
    def parse_network_type(cls, nettype: str) -> MoneroNetworkType:
        net = nettype.lower()
        if net == "mainnet" or net == "main" or cls.is_regtest(net):
            return MoneroNetworkType.MAINNET
        elif net == "testnet" or net == "test":
            return MoneroNetworkType.TESTNET
        elif net == "stagenet" or net == "stage":
            return MoneroNetworkType.STAGENET

        raise TypeError(f"Invalid network type provided: {str(nettype)}")

    @classmethod
    def test_known_peer(cls, peer: Optional[MoneroPeer], from_connection: bool):
        assert peer is not None, "Peer is null"
        assert peer.id is not None
        assert peer.host is not None
        assert peer.port is not None
        AssertUtils.assert_false(len(peer.id) == 0)
        AssertUtils.assert_false(len(peer.host) == 0)
        AssertUtils.assert_true(peer.port > 0)
        AssertUtils.assert_true(peer.rpc_port is None or peer.rpc_port >= 0)
        AssertUtils.assert_not_none(peer.is_online)
        if peer.rpc_credits_per_hash is not None:
            GenUtils.test_unsigned_big_integer(peer.rpc_credits_per_hash)
        if from_connection:
            AssertUtils.assert_is_none(peer.last_seen_timestamp)
        else:
            assert peer.last_seen_timestamp is not None

            if peer.last_seen_timestamp < 0:
                logger.warning(f"Last seen timestamp is invalid: {peer.last_seen_timestamp}")
            AssertUtils.assert_true(peer.last_seen_timestamp >= 0)

        AssertUtils.assert_true(peer.pruning_seed is None or peer.pruning_seed >= 0)

    @classmethod
    def test_peer(cls, peer: Union[Any, MoneroPeer]):
        AssertUtils.assert_true(isinstance(peer, MoneroPeer))
        cls.test_known_peer(peer, True)
        assert peer.hash is not None
        assert peer.avg_download is not None
        assert peer.avg_upload is not None
        assert peer.current_download is not None
        assert peer.current_upload is not None
        assert peer.height is not None
        assert peer.live_time is not None
        assert peer.num_receives is not None
        assert peer.receive_idle_time is not None
        assert peer.num_sends is not None
        assert peer.send_idle_time is not None
        assert peer.num_support_flags is not None

        AssertUtils.assert_false(len(peer.hash) == 0)
        AssertUtils.assert_true(peer.avg_download >= 0)
        AssertUtils.assert_true(peer.avg_upload >= 0)
        AssertUtils.assert_true(peer.current_download >= 0)
        AssertUtils.assert_true(peer.current_upload >= 0)
        AssertUtils.assert_true(peer.height >= 0)
        AssertUtils.assert_true(peer.live_time >= 0)
        AssertUtils.assert_not_none(peer.is_local_ip)
        AssertUtils.assert_not_none(peer.is_local_host)
        AssertUtils.assert_true(peer.num_receives >= 0)
        AssertUtils.assert_true(peer.receive_idle_time >= 0)
        AssertUtils.assert_true(peer.num_sends >= 0)
        AssertUtils.assert_true(peer.send_idle_time >= 0)
        AssertUtils.assert_not_none(peer.state)
        AssertUtils.assert_true(peer.num_support_flags >= 0)
        AssertUtils.assert_not_none(peer.connection_type)

    @classmethod
    def test_info(cls, info: MoneroDaemonInfo):
        assert info.num_alt_blocks is not None
        assert info.block_size_limit is not None
        assert info.block_size_median is not None
        assert info.num_offline_peers is not None
        assert info.num_online_peers is not None
        assert info.height is not None
        assert info.height_without_bootstrap is not None
        assert info.num_incoming_connections is not None
        assert info.num_outgoing_connections is not None
        assert info.num_rpc_connections is not None
        assert info.start_timestamp is not None
        assert info.adjusted_timestamp is not None
        assert info.target is not None
        assert info.target_height is not None
        assert info.num_txs is not None
        assert info.num_txs_pool is not None
        assert info.block_weight_limit is not None
        assert info.block_weight_median is not None
        assert info.database_size is not None
        AssertUtils.assert_not_none(info.version)
        AssertUtils.assert_true(info.num_alt_blocks >= 0)
        AssertUtils.assert_true(info.block_size_limit > 0)
        AssertUtils.assert_true(info.block_size_median > 0)
        AssertUtils.assert_true(info.bootstrap_daemon_address is None or not GenUtils.is_empty(info.bootstrap_daemon_address))
        GenUtils.test_unsigned_big_integer(info.cumulative_difficulty)
        GenUtils.test_unsigned_big_integer(info.free_space)
        AssertUtils.assert_true(info.num_offline_peers >= 0)
        AssertUtils.assert_true(info.num_online_peers >= 0)
        AssertUtils.assert_true(info.height >= 0)
        AssertUtils.assert_true(info.height_without_bootstrap > 0)
        AssertUtils.assert_true(info.num_incoming_connections >= 0)
        AssertUtils.assert_not_none(info.network_type)
        AssertUtils.assert_not_none(info.is_offline)
        AssertUtils.assert_true(info.num_outgoing_connections >= 0)
        AssertUtils.assert_true(info.num_rpc_connections >= 0)
        AssertUtils.assert_true(info.start_timestamp > 0)
        AssertUtils.assert_true(info.adjusted_timestamp > 0)
        AssertUtils.assert_true(info.target > 0)
        AssertUtils.assert_true(info.target_height >= 0)
        AssertUtils.assert_true(info.num_txs >= 0)
        AssertUtils.assert_true(info.num_txs_pool >= 0)
        AssertUtils.assert_not_none(info.was_bootstrap_ever_used)
        AssertUtils.assert_true(info.block_weight_limit > 0)
        AssertUtils.assert_true(info.block_weight_median > 0)
        AssertUtils.assert_true(info.database_size > 0)
        AssertUtils.assert_not_none(info.update_available)
        GenUtils.test_unsigned_big_integer(info.credits, False) # 0 credits
        AssertUtils.assert_false(GenUtils.is_empty(info.top_block_hash))
        AssertUtils.assert_not_none(info.is_busy_syncing)
        AssertUtils.assert_not_none(info.is_synchronized)

    @classmethod
    def test_sync_info(cls, sync_info: Union[Any, MoneroDaemonSyncInfo]):
        AssertUtils.assert_true(isinstance(sync_info, MoneroDaemonSyncInfo))
        assert sync_info.height is not None
        AssertUtils.assert_true(sync_info.height >= 0)

        for connection in sync_info.peers:
            cls.test_peer(connection)

        for span in sync_info.spans:
            cls.test_connection_span(span)

        assert sync_info.next_needed_pruning_seed is not None
        AssertUtils.assert_true(sync_info.next_needed_pruning_seed >= 0)
        AssertUtils.assert_is_none(sync_info.overview)
        GenUtils.test_unsigned_big_integer(sync_info.credits, False) # 0 credits
        AssertUtils.assert_is_none(sync_info.top_block_hash)

    @classmethod
    def test_connection_span(cls, span: Union[MoneroConnectionSpan, Any]) -> None:
        raise NotImplementedError()

    @classmethod
    def test_hard_fork_info(cls, hard_fork_info: MoneroHardForkInfo):
        AssertUtils.assert_not_none(hard_fork_info.earliest_height)
        AssertUtils.assert_not_none(hard_fork_info.is_enabled)
        AssertUtils.assert_not_none(hard_fork_info.state)
        AssertUtils.assert_not_none(hard_fork_info.threshold)
        AssertUtils.assert_not_none(hard_fork_info.version)
        AssertUtils.assert_not_none(hard_fork_info.num_votes)
        AssertUtils.assert_not_none(hard_fork_info.voting)
        AssertUtils.assert_not_none(hard_fork_info.window)
        GenUtils.test_unsigned_big_integer(hard_fork_info.credits, False) # 0 credits
        AssertUtils.assert_is_none(hard_fork_info.top_block_hash)

    @classmethod
    def test_alt_chain(cls, alt_chain: MoneroAltChain):
        AssertUtils.assert_not_none(alt_chain)
        AssertUtils.assert_false(len(alt_chain.block_hashes) == 0)
        GenUtils.test_unsigned_big_integer(alt_chain.difficulty, True)
        assert alt_chain.height is not None
        assert alt_chain.length is not None
        assert alt_chain.main_chain_parent_block_hash is not None
        AssertUtils.assert_true(alt_chain.height > 0)
        AssertUtils.assert_true(alt_chain.length > 0)
        AssertUtils.assert_equals(64, len(alt_chain.main_chain_parent_block_hash))

    @classmethod
    def test_ban(cls, ban: Optional[MoneroBan]) -> None:
        assert ban is not None
        assert ban.host is not None
        assert ban.ip is not None
        assert ban.seconds is not None

    @classmethod
    def test_miner_tx_sum(cls, tx_sum: Optional[MoneroMinerTxSum]) -> None:
        assert tx_sum is not None
        GenUtils.test_unsigned_big_integer(tx_sum.emission_sum, True)
        GenUtils.test_unsigned_big_integer(tx_sum.fee_sum, True)

    @classmethod
    def test_tx_pool_stats(cls, stats: MoneroTxPoolStats):
        AssertUtils.assert_not_none(stats)
        assert stats.num_txs is not None
        AssertUtils.assert_true(stats.num_txs >= 0)
        if stats.num_txs > 0:

            assert stats.bytes_max is not None
            assert stats.bytes_med is not None
            assert stats.bytes_min is not None
            assert stats.bytes_total is not None
            assert stats.oldest_timestamp is not None
            assert stats.num10m is not None
            assert stats.num_double_spends is not None
            assert stats.num_failing is not None
            assert stats.num_not_relayed is not None

            AssertUtils.assert_true(stats.bytes_max > 0)
            AssertUtils.assert_true(stats.bytes_med > 0)
            AssertUtils.assert_true(stats.bytes_min > 0)
            AssertUtils.assert_true(stats.bytes_total > 0)
            AssertUtils.assert_true(stats.histo98pc is None or stats.histo98pc > 0)
            AssertUtils.assert_true(stats.oldest_timestamp > 0)
            AssertUtils.assert_true(stats.num10m >= 0)
            AssertUtils.assert_true(stats.num_double_spends >= 0)
            AssertUtils.assert_true(stats.num_failing >= 0)
            AssertUtils.assert_true(stats.num_not_relayed >= 0)

        else:
            AssertUtils.assert_is_none(stats.bytes_max)
            AssertUtils.assert_is_none(stats.bytes_med)
            AssertUtils.assert_is_none(stats.bytes_min)
            AssertUtils.assert_equals(0, stats.bytes_total)
            AssertUtils.assert_is_none(stats.histo98pc)
            AssertUtils.assert_is_none(stats.oldest_timestamp)
            AssertUtils.assert_equals(0, stats.num10m)
            AssertUtils.assert_equals(0, stats.num_double_spends)
            AssertUtils.assert_equals(0, stats.num_failing)
            AssertUtils.assert_equals(0, stats.num_not_relayed)
            #AssertUtils.assert_is_none(stats.histo)

    @classmethod
    def test_rpc_connection(cls, connection: Optional[MoneroRpcConnection], uri: Optional[str], connected: bool = True) -> None:
        assert connection is not None
        assert uri is not None
        assert len(uri) > 0
        assert connection.uri == uri
        assert connection.check_connection() == connected
        assert connection.is_connected() == connected
        assert connection.is_online() == connected

    @classmethod
    def test_block_template(cls, template: MoneroBlockTemplate):
        AssertUtils.assert_not_none(template)
        AssertUtils.assert_not_none(template.block_template_blob)
        AssertUtils.assert_not_none(template.block_hashing_blob)
        AssertUtils.assert_not_none(template.difficulty)
        AssertUtils.assert_not_none(template.expected_reward)
        AssertUtils.assert_not_none(template.height)
        AssertUtils.assert_not_none(template.prev_hash)
        AssertUtils.assert_not_none(template.reserved_offset)
        AssertUtils.assert_not_none(template.seed_height)
        assert template.seed_height is not None
        AssertUtils.assert_true(template.seed_height >= 0)
        AssertUtils.assert_not_none(template.seed_hash)
        AssertUtils.assert_false(template.seed_hash == "")
        # next seed hash can be null or initialized TODO: test circumstances for each

    @classmethod
    def test_update_check_result(cls, result: Union[Any, MoneroDaemonUpdateCheckResult]):
        assert result is not None
        AssertUtils.assert_true(isinstance(result, MoneroDaemonUpdateCheckResult))
        AssertUtils.assert_not_none(result.is_update_available)
        if result.is_update_available:
            AssertUtils.assert_false(GenUtils.is_empty(result.auto_uri), "No auto uri is daemon online?")
            AssertUtils.assert_false(GenUtils.is_empty(result.user_uri))
            AssertUtils.assert_false(GenUtils.is_empty(result.version))
            AssertUtils.assert_false(GenUtils.is_empty(result.hash))
            assert result.hash is not None
            AssertUtils.assert_equals(64, len(result.hash))
        else:
            AssertUtils.assert_is_none(result.auto_uri)
            AssertUtils.assert_is_none(result.user_uri)
            AssertUtils.assert_is_none(result.version)
            AssertUtils.assert_is_none(result.hash)

    @classmethod
    def test_update_download_result(cls, result: MoneroDaemonUpdateDownloadResult, path: Optional[str]):
        cls.test_update_check_result(result)
        if result.is_update_available:
            if path is not None:
                AssertUtils.assert_equals(path, result.download_path)
            else:
                AssertUtils.assert_not_none(result.download_path)
        else:
            AssertUtils.assert_is_none(result.download_path)
