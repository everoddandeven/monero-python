import logging

from abc import ABC
from typing import Optional, Union, Any
from monero import (
    MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo,
    MoneroConnectionSpan, MoneroHardForkInfo,
    MoneroAltChain, MoneroBan, MoneroMinerTxSum,
    MoneroTxPoolStats, MoneroBlockTemplate,
    MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroNetworkType, MoneroRpcConnection, MoneroSubmitTxResult,
    MoneroKeyImageSpentStatus, MoneroDaemonRpc, MoneroTx,
    MoneroBlock, MoneroOutputHistogramEntry, MoneroOutputDistributionEntry,
    MoneroConnectionType, SerializableStruct
)

from .gen_utils import GenUtils

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

    # region Test Utils

    @classmethod
    def test_known_peer(cls, peer: Optional[MoneroPeer], from_connection: bool) -> None:
        assert peer is not None, "Peer is null"
        assert peer.id is not None
        assert peer.host is not None
        assert peer.port is not None
        assert len(peer.id) > 0
        assert len(peer.host) > 0
        assert peer.port > 0
        assert peer.rpc_port is None or peer.rpc_port >= 0
        assert peer.is_online is not None
        if peer.rpc_credits_per_hash is not None:
            GenUtils.test_unsigned_big_integer(peer.rpc_credits_per_hash)
        if from_connection:
            assert peer.last_seen_timestamp is None
        else:
            assert peer.last_seen_timestamp is not None

            if peer.last_seen_timestamp < 0:
                logger.warning(f"Last seen timestamp is invalid: {peer.last_seen_timestamp}")
            assert peer.last_seen_timestamp >= 0

        assert peer.pruning_seed is None or peer.pruning_seed >= 0

    @classmethod
    def test_peer(cls, peer: Union[Any, MoneroPeer]) -> None:
        assert isinstance(peer, MoneroPeer)
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

        assert len(peer.hash) > 0
        assert peer.avg_download >= 0
        assert peer.avg_upload >= 0
        assert peer.current_download >= 0
        assert peer.current_upload >= 0
        assert peer.height >= 0
        assert peer.live_time >= 0
        assert peer.is_local_ip is not None
        assert peer.is_local_host is not None
        assert peer.num_receives >= 0
        assert peer.receive_idle_time >= 0
        assert peer.num_sends >= 0
        assert peer.send_idle_time >= 0
        assert peer.state is not None
        assert peer.num_support_flags >= 0
        assert peer.connection_type is not None

    @classmethod
    def test_info(cls, info: MoneroDaemonInfo) -> None:
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
        assert info.version is not None
        assert info.num_alt_blocks >= 0
        assert info.block_size_limit > 0
        assert info.block_size_median > 0
        assert info.bootstrap_daemon_address is None or len(info.bootstrap_daemon_address) > 0
        GenUtils.test_unsigned_big_integer(info.cumulative_difficulty)
        GenUtils.test_unsigned_big_integer(info.free_space)
        assert info.num_offline_peers >= 0
        assert info.num_online_peers >= 0
        assert info.height >= 0
        assert info.height_without_bootstrap > 0
        assert info.num_incoming_connections >= 0
        assert info.network_type is not None
        assert info.is_offline is not None
        assert info.num_outgoing_connections >= 0
        assert info.num_rpc_connections >= 0
        assert info.start_timestamp > 0
        assert info.adjusted_timestamp > 0
        assert info.target > 0
        assert info.target_height >= 0
        assert info.num_txs >= 0
        assert info.num_txs_pool >= 0
        assert info.was_bootstrap_ever_used is not None
        assert info.block_weight_limit > 0
        assert info.block_weight_median > 0
        assert info.database_size > 0
        assert info.update_available is not None
        GenUtils.test_unsigned_big_integer(info.credits, False) # 0 credits
        assert info.top_block_hash is not None
        assert len(info.top_block_hash) > 0
        assert info.is_busy_syncing is not None
        assert info.is_synchronized is not None

    @classmethod
    def test_sync_info(cls, sync_info: Union[Any, MoneroDaemonSyncInfo]) -> None:
        assert isinstance(sync_info, MoneroDaemonSyncInfo)
        assert sync_info.height is not None
        assert sync_info.height >= 0

        for connection in sync_info.peers:
            cls.test_peer(connection)

        for span in sync_info.spans:
            cls.test_connection_span(span)

        assert sync_info.next_needed_pruning_seed is not None
        assert sync_info.next_needed_pruning_seed >= 0
        assert sync_info.overview is None
        GenUtils.test_unsigned_big_integer(sync_info.credits, False) # 0 credits
        assert sync_info.top_block_hash is None

    @classmethod
    def test_connection_span(cls, span: Union[MoneroConnectionSpan, Any]) -> None:
        raise NotImplementedError()

    @classmethod
    def test_hard_fork_info(cls, hard_fork_info: MoneroHardForkInfo) -> None:
        assert hard_fork_info.earliest_height is not None
        assert hard_fork_info.is_enabled is not None
        assert hard_fork_info.state is not None
        assert hard_fork_info.threshold is not None
        assert hard_fork_info.version is not None
        assert hard_fork_info.num_votes is not None
        assert hard_fork_info.voting is not None
        assert hard_fork_info.window is not None
        GenUtils.test_unsigned_big_integer(hard_fork_info.credits, False) # 0 credits
        assert hard_fork_info.top_block_hash is None

    @classmethod
    def test_alt_chain(cls, alt_chain: Optional[MoneroAltChain]) -> None:
        assert alt_chain is not None
        assert len(alt_chain.block_hashes) > 0
        GenUtils.test_unsigned_big_integer(alt_chain.difficulty, True)
        assert alt_chain.height is not None
        assert alt_chain.length is not None
        assert alt_chain.main_chain_parent_block_hash is not None
        assert alt_chain.height > 0
        assert alt_chain.length > 0
        assert 64 == len(alt_chain.main_chain_parent_block_hash)

    @classmethod
    def test_ban(cls, ban: Optional[MoneroBan]) -> None:
        assert ban is not None
        assert ban.host is not None
        assert ban.ip is not None
        assert ban.seconds is not None

    @classmethod
    def test_miner_tx_sum(cls, tx_sum: Optional[MoneroMinerTxSum]) -> None:
        assert tx_sum is not None
        GenUtils.test_unsigned_big_integer(tx_sum.emission_sum)
        GenUtils.test_unsigned_big_integer(tx_sum.fee_sum)

    @classmethod
    def test_tx_pool_stats(cls, stats: Optional[MoneroTxPoolStats]) -> None:
        assert stats is not None
        assert stats.num_txs is not None
        assert stats.num_txs >= 0
        if stats.num_txs > 0:
            # TODO test stats.histo

            assert stats.bytes_max is not None
            assert stats.bytes_med is not None
            assert stats.bytes_min is not None
            assert stats.bytes_total is not None
            assert stats.oldest_timestamp is not None
            assert stats.num10m is not None
            assert stats.num_double_spends is not None
            assert stats.num_failing is not None
            assert stats.num_not_relayed is not None

            assert stats.bytes_max > 0
            assert stats.bytes_med > 0
            assert stats.bytes_min > 0
            assert stats.bytes_total > 0
            # TODO getting 0 from regtest daemon
            #assert stats.histo98pc is None or stats.histo98pc > 0, f"stats.histo98pc: {stats.histo98pc}")
            assert stats.oldest_timestamp > 0
            assert stats.num10m >= 0
            assert stats.num_double_spends >= 0
            assert stats.num_failing >= 0
            assert stats.num_not_relayed >= 0

        else:
            assert stats.bytes_max is None
            assert stats.bytes_med is None
            assert stats.bytes_min is None
            assert stats.bytes_total == 0
            assert stats.histo98pc is None
            assert stats.oldest_timestamp is None
            assert stats.num10m == 0
            assert stats.num_double_spends == 0
            assert stats.num_failing == 0
            assert stats.num_not_relayed == 0
            # TODO test histo
            #assert stats.histo is None

    @classmethod
    def test_rpc_connection(cls,
                            connection: Optional[MoneroRpcConnection],
                            uri: Optional[str],
                            connected: bool,
                            connection_type: Optional[MoneroConnectionType]
                            ) -> None:
        """
        Test a monero rpc connection.

        :param MoneroRpcConnection | None connection: rpc connection to test.
        :param str | None uri: rpc uri of the connection to test.
        :param bool connected: checks if rpc is connected or not.
        :param MoneroConnectionType | None connection_type: type of rpc connection to test.
        :raises AssertionError: raises an error if rpc connection is not as expected.
        """
        # check expected values from rpc connection
        assert connection is not None
        assert isinstance(connection, SerializableStruct)
        assert isinstance(connection, MoneroRpcConnection)
        assert uri is not None
        assert len(uri) > 0
        assert connection.uri == uri
        # check connection
        assert connection.check_connection()
        assert not connection.check_connection()
        assert connection.is_connected() == connected
        assert connection.is_online() == connected

        if connected:
            assert connection.response_time is not None
            assert connection.response_time > 0
            logger.debug(f"Rpc connection response time: {connection.response_time} ms")
        else:
            assert connection.response_time is None

        # test setting to readonly property
        try:
            connection.response_time = 0 # type: ignore
            raise Exception("Should have failed")
        except Exception as e:
            e_msg: str = str(e)
            assert e_msg != "Should have failed", e_msg

        # test connection type
        if connection_type == MoneroConnectionType.I2P:
            assert connection.is_i2p()
        elif connection_type == MoneroConnectionType.TOR:
            assert connection.is_onion()
        elif connection_type is not None:
            assert not connection.is_i2p()
            assert not connection.is_onion()

    @classmethod
    def test_block_template(cls, template: Optional[MoneroBlockTemplate]) -> None:
        assert template is not None
        assert template.block_template_blob is not None
        assert template.block_hashing_blob is not None
        assert template.difficulty is not None
        assert template.expected_reward is not None
        assert template.height is not None
        assert template.prev_hash is not None
        assert template.reserved_offset is not None
        assert template.seed_height is not None
        assert template.seed_height is not None
        assert template.seed_height >= 0
        assert template.seed_hash is not None
        assert len(template.seed_hash) > 0
        # next seed hash can be null or initialized TODO: test circumstances for each

    @classmethod
    def test_update_check_result(cls, result: Union[Any, MoneroDaemonUpdateCheckResult]) -> None:
        assert result is not None
        assert isinstance(result, MoneroDaemonUpdateCheckResult)
        assert result.is_update_available is not None
        if result.is_update_available:
            err_msg: str = "No auto uri is daemon online?"
            assert result.auto_uri is not None, err_msg
            assert len(result.auto_uri) > 0, err_msg

            assert result.user_uri is not None
            assert len(result.user_uri) > 0

            assert result.version is not None
            assert len(result.version) > 0

            assert result.hash is not None
            assert len(result.hash) == 64

        else:
            assert result.auto_uri is None
            assert result.user_uri is None
            assert result.version is None
            assert result.hash is None

    @classmethod
    def test_update_download_result(cls, result: MoneroDaemonUpdateDownloadResult, path: Optional[str]) -> None:
        cls.test_update_check_result(result)
        if result.is_update_available:
            if result.download_path is None:
                # TODO monero-project daemon returning empty status string on download update error
                logger.warning("TODO Result path is None")
                return
            #if path is not None:
            #    assert path == result.download_path
            #else:
            #    assert result.download_path is not None
        else:
            assert result.download_path is None

    @classmethod
    def test_submit_tx_result_common(cls, result: MoneroSubmitTxResult) -> None:
        assert result.is_good is not None
        assert result.is_relayed is not None
        assert result.is_double_spend is not None
        assert result.is_fee_too_low is not None
        assert result.is_mixin_too_low is not None
        assert result.has_invalid_input is not None
        assert result.has_invalid_output is not None
        assert result.is_overspend is not None
        assert result.is_too_big is not None
        assert result.sanity_check_failed is not None
        assert result.reason is None or len(result.reason) > 0

    @classmethod
    def test_submit_tx_result_good(cls, result: Optional[MoneroSubmitTxResult]) -> None:
        assert result is not None
        cls.test_submit_tx_result_common(result)
        # test good tx submission
        assert result.is_double_spend is False, "tx submission is double spend."
        assert result.is_fee_too_low is False, "fee is too low."
        assert result.is_mixin_too_low is False, "mixin is too low."
        assert result.has_invalid_input is False, "tx has invalid input."
        assert result.has_invalid_output is False, "tx has invalid output."
        assert result.has_too_few_outputs is False, "tx has too few outputs."
        assert result.is_overspend is False, "tx is overspend."
        assert result.is_too_big is False, "tx is too big."
        assert result.sanity_check_failed is False, "tx sanity check failed."
        # 0 credits
        GenUtils.test_unsigned_big_integer(result.credits, False)
        assert result.top_block_hash is None
        assert result.is_tx_extra_too_big is False, "tx extra is too big."
        assert result.is_good is True
        assert result.is_nonzero_unlock_time is False, "tx has non-zero unlock time."

    @classmethod
    def test_submit_tx_result_double_spend(cls, result: Optional[MoneroSubmitTxResult]) -> None:
        assert result is not None
        cls.test_submit_tx_result_common(result)
        assert result.is_good is False
        assert result.is_double_spend is True
        assert result.is_fee_too_low is False
        assert result.is_mixin_too_low is False
        assert result.has_invalid_input is False
        assert result.has_invalid_output is False
        assert result.is_overspend is False
        assert result.is_too_big is False

    @classmethod
    def test_spent_statuses(cls, daemon: MoneroDaemonRpc, key_images: list[str], expected_status: MoneroKeyImageSpentStatus) -> None:
        # test image
        for key_image in key_images:
            assert daemon.get_key_image_spent_status(key_image) == expected_status

        # test array of images
        statuses: list[MoneroKeyImageSpentStatus] = []
        if len(key_images) > 0:
            statuses = daemon.get_key_image_spent_statuses(key_images)

        assert len(key_images) == len(statuses)
        for status in statuses:
            assert status == expected_status

    @classmethod
    def test_output_distribution_entry(cls, entry: Optional[MoneroOutputDistributionEntry]) -> None:
        assert entry is not None
        GenUtils.test_unsigned_big_integer(entry.amount)
        assert entry.base is not None
        assert entry.base >= 0
        assert len(entry.distribution) > 0
        assert entry.start_height is not None
        assert entry.start_height >= 0

    @classmethod
    def test_output_histogram_entry(cls, entry: Optional[MoneroOutputHistogramEntry]) -> None:
        assert entry is not None
        GenUtils.test_unsigned_big_integer(entry.amount)
        assert entry.num_instances is not None
        assert entry.num_instances >= 0
        assert entry.unlocked_instances is not None
        assert entry.unlocked_instances >= 0
        assert entry.recent_instances is not None
        assert entry.recent_instances >= 0

    @classmethod
    def get_confirmed_txs(cls, daemon: MoneroDaemonRpc, num_txs: int) -> list[MoneroTx]:
        """
        Get confirmed txs on blockchain.

        :param MoneroDaemonRpc daemon: daemon to use to query blockchain.
        :param int num_txs: number of confirmed transactions to get from blockchain.
        :returns list[MoneroTx]: list of transactions confirmed on blockchain.
        """
        txs: list[MoneroTx] = []
        num_blocks_per_req: int = 50
        start_idx: int = daemon.get_height() - num_blocks_per_req - 1

        while start_idx >= 0:
            blocks: list[MoneroBlock] = daemon.get_blocks_by_range(start_idx, start_idx + num_blocks_per_req)
            for block in blocks:
                for tx in block.txs:
                    txs.append(tx)
                    if len(txs) == num_txs:
                        return txs

            start_idx -= num_blocks_per_req

        raise Exception(f"Could not get {num_txs} confirmed txs")

    #endregion
