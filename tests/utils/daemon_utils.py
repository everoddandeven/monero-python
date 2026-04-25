import logging

from abc import ABC
from monero import (
    MoneroDaemon, MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo,
    MoneroConnectionSpan, MoneroHardForkInfo, MoneroBlock,
    MoneroBan, MoneroMinerTxSum, MoneroTx, MoneroTxPoolStats,
    MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroNetworkType, MoneroSubmitTxResult,
    MoneroKeyImageSpentStatus, MoneroDaemonRpc,
)

from .gen_utils import GenUtils

logger: logging.Logger = logging.getLogger("DaemonUtils")


class DaemonUtils(ABC):
    """Daemon test utilities."""

    @classmethod
    def is_regtest(cls, network_type_str: str | None) -> bool:
        """Check if network type string indicates `regtest` network.

        :param str | None network_type_str: network type in string format.
        :returns bool: `True` if network type string indicates `regtest` network, `False` otherwise.
        """
        if network_type_str is None:
            return False
        nettype = network_type_str.lower()
        return nettype == "regtest" or nettype == "reg"

    @classmethod
    def parse_network_type(cls, nettype: str) -> MoneroNetworkType:
        """Parse network type string into enum.

        :param str nettype: network type in string format.
        :returns MoneroNetworkType: parsed network type.
        """
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
    def test_known_peer(cls, peer: MoneroPeer, from_connection: bool, debug: bool = True) -> None:
        """Test known daemon peer.

        :param MoneroPeer peer: daemon peer to test.
        :param bool from_connection: indicates if `peer` is obtained from daemon connections.
        """
        if debug:
            logger.debug(f"Testing known peer: {peer.serialize()}")
        # common peer validation
        assert peer.id is not None
        assert peer.host is not None
        assert peer.port is not None
        assert len(peer.id) > 0
        assert len(peer.host) > 0
        assert peer.port > 0
        assert peer.rpc_port is None or peer.rpc_port >= 0
        assert peer.is_online is not None
        assert peer.pruning_seed is None or peer.pruning_seed >= 0
        if peer.rpc_credits_per_hash is not None:
            GenUtils.test_unsigned_big_integer(peer.rpc_credits_per_hash)

        if from_connection:
            # validate peer connection
            assert peer.last_seen_timestamp is None
        else:
            # validate known peer
            assert peer.last_seen_timestamp is not None
            assert peer.last_seen_timestamp >= 0, f"Last seen timestamp is invalid: {peer.last_seen_timestamp}"

    @classmethod
    def test_peer(cls, peer: MoneroPeer) -> None:
        """Test daemon connection peer.

        :param MoneroPeer peer: peer connection to test.
        """
        logger.debug(f"Testing peer: {peer.serialize()}")
        cls.test_known_peer(peer, True, False)
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
        """Test daemon information.

        :param MoneroDaemonInfo info: daemon info to test.
        """
        logger.debug(f"Testing daemon info: {info.serialize()}")
        assert info.version is not None
        assert info.num_alt_blocks is not None and info.num_alt_blocks >= 0
        assert info.block_size_limit is not None and info.block_size_limit > 0
        assert info.block_size_median is not None and info.block_size_median > 0
        assert info.bootstrap_daemon_address is None or len(info.bootstrap_daemon_address) > 0
        GenUtils.test_unsigned_big_integer(info.cumulative_difficulty)
        GenUtils.test_unsigned_big_integer(info.free_space)
        assert info.num_offline_peers is not None and info.num_offline_peers >= 0
        assert info.num_online_peers is not None and info.num_online_peers >= 0
        assert info.height is not None and info.height >= 0
        assert info.height_without_bootstrap is not None and info.height_without_bootstrap > 0
        assert info.num_incoming_connections is not None and info.num_incoming_connections >= 0
        assert info.num_outgoing_connections is not None and info.num_outgoing_connections >= 0
        assert info.network_type is not None
        assert info.is_offline is not None
        assert info.num_rpc_connections is not None and info.num_rpc_connections >= 0
        assert info.start_timestamp is not None and info.start_timestamp > 0
        assert info.adjusted_timestamp is not None and info.adjusted_timestamp > 0
        assert info.target is not None and info.target > 0
        assert info.target_height is not None and info.target_height >= 0
        assert info.num_txs is not None and info.num_txs >= 0
        assert info.num_txs_pool is not None and info.num_txs_pool >= 0
        assert info.was_bootstrap_ever_used is not None
        assert info.block_weight_limit is not None and info.block_weight_limit > 0
        assert info.block_weight_median is not None and info.block_weight_median > 0
        assert info.database_size is not None and info.database_size > 0
        assert info.update_available is not None
        # 0 credits
        GenUtils.test_unsigned_big_integer(info.credits, False)
        assert info.top_block_hash is not None
        assert len(info.top_block_hash) > 0
        assert info.is_busy_syncing is not None
        assert info.is_synchronized is not None

    @classmethod
    def test_connection_span(cls, span: MoneroConnectionSpan) -> None:
        """Test daemon connection span.

        :param MoneroConnectionSpan span: daemon connection span to test.
        """
        logger.debug(f"Testing connection span: {span.serialize()}")
        raise NotImplementedError("DaemonUtils.test_connection_span(): not implemented")

    @classmethod
    def test_sync_info(cls, sync_info: MoneroDaemonSyncInfo) -> None:
        """Test daemon synchronization info.

        :param MoneroDaemonSyncInfo sync_info: daemon sync info to test.
        """
        logger.debug(f"Testing daemon sync info: {sync_info.serialize()}")
        assert sync_info.height is not None and sync_info.height >= 0

        # test peers
        for connection in sync_info.peers:
            cls.test_peer(connection)

        # test connection spans
        for span in sync_info.spans:
            cls.test_connection_span(span)

        assert sync_info.next_needed_pruning_seed is not None
        assert sync_info.next_needed_pruning_seed >= 0
        assert sync_info.overview is None
        # 0 credits
        GenUtils.test_unsigned_big_integer(sync_info.credits, False)
        assert sync_info.top_block_hash is None

    @classmethod
    def test_hard_fork_info(cls, hard_fork_info: MoneroHardForkInfo) -> None:
        """Test daemon hard fork information.

        :param MoneroHardForkInfo hard_fork_info: daemon hard fork information to test.
        """
        logger.debug(f"Testing hard fork info: {hard_fork_info.serialize()}")
        assert hard_fork_info.earliest_height is not None
        assert hard_fork_info.is_enabled is not None
        assert hard_fork_info.state is not None
        assert hard_fork_info.threshold is not None
        assert hard_fork_info.version is not None
        assert hard_fork_info.num_votes is not None
        assert hard_fork_info.voting is not None
        assert hard_fork_info.window is not None
        # 0 credits
        GenUtils.test_unsigned_big_integer(hard_fork_info.credits, False)
        assert hard_fork_info.top_block_hash is None

    @classmethod
    def test_ban(cls, ban: MoneroBan) -> None:
        """Test daemon ban.

        :param MoneroBan ban: daemon ban to test.
        """
        logger.debug(f"Testing ban: {ban.serialize()}")
        assert ban.host is not None
        assert ban.ip is not None
        assert ban.seconds is not None

    @classmethod
    def test_miner_tx_sum(cls, tx_sum: MoneroMinerTxSum) -> None:
        """Test miner tx sum result.

        :param MoneroMinerTxSum tx_sum: miner tx sum to test.
        """
        logger.debug(f"Testing tx sum: {tx_sum.serialize()}")
        GenUtils.test_unsigned_big_integer(tx_sum.emission_sum)
        GenUtils.test_unsigned_big_integer(tx_sum.fee_sum)

    @classmethod
    def test_tx_pool_stats(cls, stats: MoneroTxPoolStats) -> None:
        """Test daemon tx pool statistics.

        :param MoneroTxPoolStats stats: daemon tx pool statistics to test.
        """
        logger.debug(f"Testing tx pool stats: {stats.serialize()}")
        assert stats is not None
        assert stats.num_txs is not None
        assert stats.num_txs >= 0
        if stats.num_txs > 0:
            # TODO test stats.histo

            assert stats.bytes_max is not None and stats.bytes_max > 0
            assert stats.bytes_med is not None and stats.bytes_med > 0
            assert stats.bytes_min is not None and stats.bytes_min > 0
            assert stats.bytes_total is not None and stats.bytes_total > 0
            assert stats.oldest_timestamp is not None and stats.oldest_timestamp > 0
            assert stats.histo98pc is None or stats.histo98pc > 0
            assert stats.num10m is not None and stats.num10m >= 0
            assert stats.num_double_spends is not None and stats.num_double_spends >= 0
            assert stats.num_failing is not None and stats.num_failing >= 0
            assert stats.num_not_relayed is not None and stats.num_not_relayed >= 0

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
            assert len(stats.histo.values()) == 0

    @classmethod
    def test_update_check_result(cls, result: MoneroDaemonUpdateCheckResult, debug: bool = True) -> None:
        """Test daemon update check result.

        :param MoneroDaemonUpdateCheckResult result: daemon update check result to test.
        """
        if debug:
            logger.debug(f"Testing update check result: {result.serialize()}")
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
    def test_update_download_result(cls, result: MoneroDaemonUpdateDownloadResult, path: str | None) -> None:
        """Test daemon update download result.

        :param MoneroDaemonUpdateDownloadResult result: daemon update download result to test.
        :param str | None path: expected download path in result.
        """
        logger.debug(f"Testing update download result: {result.serialize()}")
        cls.test_update_check_result(result, False)
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
        """Test common daemon submit tx result.

        :param MoneroSubmitTxResult result: daemon submit tx result to test common structure.
        """
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
    def test_submit_tx_result_good(cls, result: MoneroSubmitTxResult) -> None:
        """Test succesfull daemon submit tx result.

        :param MoneroSubmitTxResult result: daemon submit tx result to test.
        """
        logger.debug(f"Testing valid submit tx result: {result.serialize()}")
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
    def test_submit_tx_result_double_spend(cls, result: MoneroSubmitTxResult) -> None:
        """Test double spend daemon submit tx result.

        :param MoneroSubmitTxResult result: daemon submit tx result to test.
        """
        logger.debug(f"Testing double spend submit tx result: {result.serialize()}")
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
        """Test key images spent statuses.

        :param MoneroDaemonRpc daemon: daemon to get key image spent statuses from.
        :param list[str] key_images: list of key image hex to get spent status from daemon.
        :param MoneroKeyImageSpentStatus expected_status: expected key images spent status.
        """
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

        raise Exception(f"Could not get {num_txs} confirmed txs (found: {len(txs)})")

    @classmethod
    def get_confirmed_tx_hashes(cls, daemon: MoneroDaemon) -> list[str]:
        """Get confirmed tx hashes from daemon from last 5 blocks.

        :param MoneroDaemon daemon: daemon instance to get confirmed txs from.
        :returns list[str]: confirmed txs hashes.
        """
        hashes: list[str] = []
        height: int = daemon.get_height()
        while len(hashes) < 5 and height > 0:
            height -= 1
            block = daemon.get_block_by_height(height)
            for tx_hash in block.tx_hashes:
                hashes.append(tx_hash)
        return hashes

    #endregion
