import pytest
import logging

from monero import MoneroDaemon, MoneroBan

logger: logging.Logger = logging.getLogger("TestMoneroDaemonInterface")


# Test calls to MoneroDaemon interface
@pytest.mark.unit
class TestMoneroDaemonInterface:
    """Daemon interface bindings unit tests"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    @pytest.fixture(scope="class")
    def daemon(self) -> MoneroDaemon:
        """Test rpc daemon instance"""
        return MoneroDaemon()

    #region Tests

    # Test interface calls

    @pytest.mark.not_supported
    def test_get_version(self, daemon: MoneroDaemon) -> None:
        daemon.get_version()

    @pytest.mark.not_supported
    def test_is_trusted(self, daemon: MoneroDaemon) -> None:
        daemon.is_trusted()

    @pytest.mark.not_supported
    def test_get_fee_estimate(self, daemon: MoneroDaemon) -> None:
        daemon.get_fee_estimate()

    @pytest.mark.not_supported
    def test_get_info(self, daemon: MoneroDaemon) -> None:
        daemon.get_info()

    @pytest.mark.not_supported
    def test_get_hard_fork_info(self, daemon: MoneroDaemon) -> None:
        daemon.get_hard_fork_info()

    @pytest.mark.not_supported
    def test_get_alt_block_hashes(self, daemon: MoneroDaemon) -> None:
        daemon.get_alt_block_hashes()

    @pytest.mark.not_supported
    def test_get_alt_chains(self, daemon: MoneroDaemon) -> None:
        daemon.get_alt_chains()

    @pytest.mark.not_supported
    def test_get_sync_info(self, daemon: MoneroDaemon) -> None:
        daemon.get_sync_info()

    @pytest.mark.not_supported
    def test_get_height(self, daemon: MoneroDaemon) -> None:
        daemon.get_height()

    @pytest.mark.not_supported
    def test_get_last_block_header(self, daemon: MoneroDaemon) -> None:
        daemon.get_last_block_header()

    @pytest.mark.not_supported
    def test_wait_for_next_block_header(self, daemon: MoneroDaemon) -> None:
        daemon.wait_for_next_block_header()

    @pytest.mark.not_supported
    def test_get_key_image_spent_status(self, daemon: MoneroDaemon) -> None:
        daemon.get_key_image_spent_status("")

    @pytest.mark.not_supported
    def test_get_key_image_spent_statuses(self, daemon: MoneroDaemon) -> None:
        daemon.get_key_image_spent_statuses([])

    @pytest.mark.not_supported
    def test_get_block_hash(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_hash(1)

    @pytest.mark.not_supported
    def test_get_block_template(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_template("")

    @pytest.mark.not_supported
    def test_get_block_header_by_hash(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_header_by_hash("")

    @pytest.mark.not_supported
    def test_get_block_header_by_height(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_header_by_height(1)

    @pytest.mark.not_supported
    def test_block_headers_by_range(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_headers_by_range(1, 100)

    @pytest.mark.not_supported
    def test_get_block_by_hash(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_by_hash("")

    @pytest.mark.not_supported
    def test_blocks_by_hash(self, daemon: MoneroDaemon) -> None:
        daemon.get_blocks_by_hash([], 0, False)

    @pytest.mark.not_supported
    def test_get_block_by_height(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_by_height(1)

    @pytest.mark.not_supported
    def test_get_blocks_by_height(self, daemon: MoneroDaemon) -> None:
        daemon.get_blocks_by_height([1])

    @pytest.mark.not_supported
    def test_get_blocks_by_range(self, daemon: MoneroDaemon) -> None:
        daemon.get_blocks_by_range(1, 100)

    @pytest.mark.not_supported
    def test_get_blocks_by_range_chunked(self, daemon: MoneroDaemon) -> None:
        daemon.get_blocks_by_range_chunked(1, 100)

    @pytest.mark.not_supported
    def test_get_block_hashes(self, daemon: MoneroDaemon) -> None:
        daemon.get_block_hashes([], 0)

    @pytest.mark.not_supported
    def test_submit_block(self, daemon: MoneroDaemon) -> None:
        daemon.submit_block("")

    @pytest.mark.not_supported
    def test_submit_blocks(self, daemon: MoneroDaemon) -> None:
        daemon.submit_blocks([])

    @pytest.mark.not_supported
    def test_get_tx(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx("")

    @pytest.mark.not_supported
    def test_get_txs(self, daemon: MoneroDaemon) -> None:
        daemon.get_txs([])

    @pytest.mark.not_supported
    def test_get_tx_hex(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx_hex("")

    @pytest.mark.not_supported
    def test_get_tx_hexes(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx_hexes([])

    @pytest.mark.not_supported
    def test_get_miner_tx_sum(self, daemon: MoneroDaemon) -> None:
        daemon.get_miner_tx_sum(0, 100)

    @pytest.mark.not_supported
    def test_submit_tx_hex(self, daemon: MoneroDaemon) -> None:
        daemon.submit_tx_hex("")

    @pytest.mark.not_supported
    def test_relay_tx_by_hash(self, daemon: MoneroDaemon) -> None:
        daemon.relay_tx_by_hash("")

    @pytest.mark.not_supported
    def test_relay_txs_by_hash(self, daemon: MoneroDaemon) -> None:
        daemon.relay_txs_by_hash([])

    @pytest.mark.not_supported
    def test_get_tx_pool(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx_pool()

    @pytest.mark.not_supported
    def test_get_tx_pool_hashes(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx_pool_hashes()

    @pytest.mark.not_supported
    def test_get_tx_pool_backlog(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx_pool_backlog()

    @pytest.mark.not_supported
    def test_get_tx_pool_stats(self, daemon: MoneroDaemon) -> None:
        daemon.get_tx_pool_stats()

    @pytest.mark.not_supported
    def test_flush_tx_pool_1(self, daemon: MoneroDaemon) -> None:
        daemon.flush_tx_pool()

    @pytest.mark.not_supported
    def test_flush_tx_pool_2(self, daemon: MoneroDaemon) -> None:
        daemon.flush_tx_pool("")

    @pytest.mark.not_supported
    def test_flush_tx_pool_3(self, daemon: MoneroDaemon) -> None:
        daemon.flush_tx_pool([""])

    @pytest.mark.not_supported
    def test_get_outputs(self, daemon: MoneroDaemon) -> None:
        daemon.get_outputs([])

    @pytest.mark.not_supported
    def test_get_output_histogram(self, daemon: MoneroDaemon) -> None:
        daemon.get_output_histogram([], 0, 100, False, 1000)

    @pytest.mark.not_supported
    def test_output_distribution(self, daemon: MoneroDaemon) -> None:
        daemon.get_output_distribution([], False, 0, 1)

    @pytest.mark.not_supported
    def test_get_peers(self, daemon: MoneroDaemon) -> None:
        daemon.get_peers()

    @pytest.mark.not_supported
    def test_get_known_peers(self, daemon: MoneroDaemon) -> None:
        daemon.get_known_peers()

    @pytest.mark.not_supported
    def test_set_outgoing_peer_limit(self, daemon: MoneroDaemon) -> None:
        daemon.set_outgoing_peer_limit(1000)

    @pytest.mark.not_supported
    def test_set_incoming_peer_limit(self, daemon: MoneroDaemon) -> None:
        daemon.set_incoming_peer_limit(10000)

    @pytest.mark.not_supported
    def test_get_peer_bans(self, daemon: MoneroDaemon) -> None:
        daemon.get_peer_bans()

    @pytest.mark.not_supported
    def test_set_peer_bans(self, daemon: MoneroDaemon) -> None:
        daemon.set_peer_bans([])

    @pytest.mark.not_supported
    def test_set_peer_ban(self, daemon: MoneroDaemon) -> None:
        daemon.set_peer_ban(MoneroBan())

    @pytest.mark.not_supported
    def test_start_mining(self, daemon: MoneroDaemon) -> None:
        daemon.start_mining("", 1, False, False)

    @pytest.mark.not_supported
    def test_stop_mining(self, daemon: MoneroDaemon) -> None:
        daemon.stop_mining()

    @pytest.mark.not_supported
    def test_get_mining_status(self, daemon: MoneroDaemon) -> None:
        daemon.get_mining_status()

    @pytest.mark.not_supported
    def test_prune_blockchain(self, daemon: MoneroDaemon) -> None:
        daemon.prune_blockchain(False)

    @pytest.mark.not_supported
    def test_check_for_update(self, daemon: MoneroDaemon) -> None:
        daemon.check_for_update()

    @pytest.mark.not_supported
    def test_download_update_1(self, daemon: MoneroDaemon) -> None:
        daemon.download_update()

    @pytest.mark.not_supported
    def test_download_update_2(self, daemon: MoneroDaemon) -> None:
        daemon.download_update("")

    #endregion
