from __future__ import annotations

import logging
import time

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroDaemonUpdateCheckResult,
    MoneroDaemonUpdateDownloadResult,
    MoneroPruneResult,
    MoneroRpcError,
)

from utils import DaemonUtils, TestUtils as Utils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcAdmin")


@pytest.mark.integration
class TestMoneroDaemonRpcAdmin(BaseTestMoneroDaemonRpc):
    """Rpc daemon admin integration tests."""

    # Can prune the blockchain
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_prune_blockchain(self, daemon: MoneroDaemonRpc) -> None:
        result: MoneroPruneResult = daemon.prune_blockchain(True)
        logger.debug(f"Testing prune result: {result.serialize()}")

        if result.is_pruned:
            assert result.pruning_seed is not None
            assert result.pruning_seed > 0
        else:
            assert 0 == result.pruning_seed

    # Can check for an update
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.xfail(reason="the update check needs DNSSEC validated TXT records, which the daemon in docker does not get", raises=MoneroRpcError, strict=False)
    def test_check_for_update(self, daemon: MoneroDaemonRpc) -> None:
        result: MoneroDaemonUpdateCheckResult = daemon.check_for_update()
        DaemonUtils.test_update_check_result(result)

    # Can download an update
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.xfail(reason="the update check needs DNSSEC validated TXT records, which the daemon in docker does not get", raises=MoneroRpcError, strict=False)
    def test_download_update(self, daemon: MoneroDaemonRpc) -> None:
        # download to default path
        result: MoneroDaemonUpdateDownloadResult = daemon.download_update()
        DaemonUtils.test_update_download_result(result, None)

        # download to defined path
        path: str = "test_download_" + str(time.time()) + ".tar.bz2"
        result = daemon.download_update(path)
        DaemonUtils.test_update_download_result(result, path)

        # test invalid path
        # TODO monerod: an invalid path causes a 500 in daemon rpc rather than a clean error
        if result.is_update_available:
            try:
                daemon.download_update("./ohhai/there")
            except Exception as e:
                logger.warning(str(e))

    # Can be stopped
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="test is disabled to not interfere with other tests")
    def test_stop(self, daemon: MoneroDaemonRpc) -> None:
        # stop the daemon
        daemon.stop()

        # give the daemon time to shut down
        time.sleep(Utils.SYNC_PERIOD_IN_MS / 1000)

        # try to interact with the stopped daemon
        with pytest.raises(Exception):
            daemon.get_height()

    # Can flush the blockchain to disk
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_save_blockchain(self, daemon: MoneroDaemonRpc) -> None:
        daemon.save_blockchain()

    # Can flush the daemon's invalid block and tx caches
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_flush_cache(self, daemon: MoneroDaemonRpc) -> None:
        daemon.flush_cache()
        daemon.flush_cache(True)

    # Can disable the bootstrap daemon
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_remove_bootstrap_daemon(self, daemon: MoneroDaemonRpc) -> None:
        daemon.remove_bootstrap_daemon()

    # Can set the poll period for block notifications
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_poll_period_in_ms(self, daemon: MoneroDaemonRpc) -> None:
        try:
            daemon.set_poll_period_in_ms(1000)
        finally:
            # restore the configured period so later tests poll at the expected rate
            daemon.set_poll_period_in_ms(Utils.DAEMON_POLL_PERIOD_IN_MS)

    # Can set the daemon's log level
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_log_level(self, daemon: MoneroDaemonRpc) -> None:
        try:
            for i in range(0, 5):
                daemon.set_log_level(i)

            for level in (-1, 5):
                with pytest.raises(Exception) as exc_info:
                    daemon.set_log_level(level)
                assert str(exc_info.value) == "Log level must be an integer between 0 and 4"
        finally:
            # restore the level from docker-compose so later tests keep full logs
            daemon.set_log_level(Utils.DAEMON_LOG_LEVEL)

    # Can set the daemon's log categories
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_log_categories(self, daemon: MoneroDaemonRpc) -> None:
        try:
            categories: str = daemon.set_log_categories("*:WARNING")
            assert isinstance(categories, str)
        finally:
            # re-applying the configured level also resets categories to its mapping
            daemon.set_log_level(Utils.DAEMON_LOG_LEVEL)

    # Can toggle the mining hash rate in the daemon log
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_log_hash_rate(self, daemon: MoneroDaemonRpc) -> None:
        try:
            daemon.set_log_hash_rate(True)
            daemon.set_log_hash_rate(False)
        except Exception as e:
            # daemon rejects the call while not mining
            logger.warning(f"set_log_hash_rate: {e}")
