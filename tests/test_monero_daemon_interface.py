import pytest
import logging

from typing import Optional
from monero import (
    MoneroDaemon, MoneroBan
)
from utils import TestUtils as Utils

logger: logging.Logger = logging.getLogger("TestMoneroDaemonInterface")


# Test calls to MoneroDaemon interface
class TestMoneroDaemonInterface:

    _daemon: Optional[MoneroDaemon] = None

    def _get_daemon(self) -> MoneroDaemon:
        if self._daemon is None:
            self._daemon = MoneroDaemon()

        return self._daemon

    @pytest.fixture(autouse=True)
    def before_each(self, request: pytest.FixtureRequest):
        logger.info(f"Before test {request.node.name}") # type: ignore
        yield
        logger.info(f"After test {request.node.name}") # type: ignore

    #region Tests

    # Test general node info
    def test_info(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.get_version()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.is_trusted()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_fee_estimate()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_info()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_hard_fork_info
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_alt_block_hashes()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_alt_chains()
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test node sync info
    def test_sync_info(self) -> None:
        daemon = self._get_daemon()
        
        try:
            daemon.get_height()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_last_block_header()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_sync_info()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.wait_for_next_block_header()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_key_image_spent_status("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_key_image_spent_statuses([])
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test blockchain
    def test_blocks(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.get_block_hash(1)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_template("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_header_by_hash("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_header_by_height(1)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_headers_by_range(1, 100)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_by_hash("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_blocks_by_hash([], 0, False)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_by_height(1)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_blocks_by_height([1])
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_blocks_by_range(1, 100)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_blocks_by_range_chunked(1, 100)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_block_hashes([], 0)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.submit_block("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.submit_blocks([])
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test txs
    def test_txs(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.get_tx("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_txs([])
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_tx_hex("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_tx_hexes([])
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_miner_tx_sum(0, 100)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.submit_tx_hex("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.relay_tx_by_hash("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.relay_txs_by_hash([])
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test tx pool
    def test_tx_pool(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.get_tx_pool()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_tx_pool_hashes()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_tx_pool_backlog()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_tx_pool_stats()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.flush_tx_pool()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.flush_tx_pool("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.flush_tx_pool([""])
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test outputs
    def test_outputs(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.get_outputs([])
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_output_histogram([], 0, 100, False, 1000)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_output_distribution([], False, 0, 1)
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test network and peers
    def test_network(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.get_peers()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_known_peers()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.set_outgoing_peer_limit(1000)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.set_incoming_peer_limit(10000)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_peer_bans()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.set_peer_bans([])
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.set_peer_ban(MoneroBan())
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test mining
    def test_mining(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.start_mining("", 1, False, False)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.stop_mining()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.get_mining_status()
        except Exception as e:
            Utils.assert_not_supported(e)

    # Test other utilities
    def test_utilities(self) -> None:
        daemon = self._get_daemon()

        try:
            daemon.prune_blockchain(False)
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.check_for_update()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.download_update()
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.download_update("")
        except Exception as e:
            Utils.assert_not_supported(e)

        try:
            daemon.wait_for_next_block_header()
        except Exception as e:
            Utils.assert_not_supported(e)

    #endregion
