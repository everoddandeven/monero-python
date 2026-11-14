from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDaemonInfo,
    MoneroDaemonNetworkStats,
    MoneroDaemonRpc,
    MoneroDaemonSyncInfo,
    MoneroHardForkInfo,
    MoneroRpcConnection,
    MoneroVersion,
)

from utils import DaemonUtils, RpcConnectionUtils, TestUtils as Utils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcInfo")


@pytest.mark.integration
class TestMoneroDaemonRpcInfo(BaseTestMoneroDaemonRpc):
    """Rpc daemon info integration tests."""

    # Test offline daemon connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_offline_daemon(self) -> None:
        # create connection to offline uri
        offline_connection: MoneroRpcConnection = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)

        assert offline_connection.check_connection()
        assert not offline_connection.is_connected()
        assert not offline_connection.is_online()

        # create daemon
        daemon: MoneroDaemonRpc = MoneroDaemonRpc(offline_connection)

        # test daemon connection
        assert daemon.get_rpc_connection() == offline_connection
        assert not daemon.is_connected()

        # call to any daemon method should throw network error
        with pytest.raises(Exception) as exc_info:
            daemon.get_height()
        assert str(exc_info.value) == RpcConnectionUtils.NETWORK_ERROR_MSG

    # Can get the daemon's version
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_version(self, daemon: MoneroDaemonRpc) -> None:
        version: MoneroVersion = daemon.get_version()
        logger.debug(f"Testing monero version: {version.serialize()}")
        assert version.number is not None
        assert version.number > 0
        assert version.is_release is not None

    # Can indicate if it's trusted
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_is_trusted(self, daemon: MoneroDaemonRpc) -> None:
        is_trusted: bool = daemon.is_trusted()
        logger.debug(f"Trusted daemon: {is_trusted}")

    # Can get general information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_general_information(self, daemon: MoneroDaemonRpc) -> None:
        info: MoneroDaemonInfo = daemon.get_info()
        DaemonUtils.test_info(info)
        assert info.is_regtest == Utils.REGTEST

    # Can get sync information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_sync_information(self, daemon: MoneroDaemonRpc) -> None:
        sync_info: MoneroDaemonSyncInfo = daemon.get_sync_info()
        DaemonUtils.test_sync_info(sync_info)

    # Can get hard fork information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_hard_fork_information(self, daemon: MoneroDaemonRpc) -> None:
        hard_fork_info: MoneroHardForkInfo = daemon.get_hard_fork_info()
        DaemonUtils.test_hard_fork_info(hard_fork_info)

    # Can get network (bandwidth) statistics
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_network_stats(self, daemon: MoneroDaemonRpc) -> None:
        stats: MoneroDaemonNetworkStats = daemon.get_network_stats()
        DaemonUtils.test_network_stats(stats)
