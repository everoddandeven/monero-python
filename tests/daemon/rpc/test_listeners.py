from __future__ import annotations

import logging

import pytest
from monero import MoneroBlockHeader, MoneroDaemonListener, MoneroDaemonRpc, MoneroWalletRpc

from utils import AssertUtils, BlockchainUtils, BlockUtils, DaemonNotificationCollector, TestUtils as Utils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcListeners")


@pytest.mark.integration
class TestMoneroDaemonRpcListeners(BaseTestMoneroDaemonRpc):
    """Rpc daemon listeners integration tests."""

    # Can notify listeners when a new block is added to the chain
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE is True or Utils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_block_listener(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        try:
            # start mining if possible to help push the network along
            address: str = wallet.get_primary_address()
            try:
                daemon.start_mining(address, 1, False, True)
            except Exception as e:
                logger.warning(f"[!]: {str(e)}")

            # register a listener
            listener: MoneroDaemonListener = MoneroDaemonListener()
            daemon.add_listener(listener)

            # wait for next block notification
            header: MoneroBlockHeader = daemon.wait_for_next_block_header()
            daemon.remove_listener(listener) # unregister listener so daemon does not keep polling
            BlockUtils.test_block_header(header, True)

            # test that listener was called with equivalent header
            AssertUtils.assert_equals(header, listener.last_header)
        finally:
            # stop mining
            try :
                daemon.stop_mining()
            except Exception as e:
                logger.warning(f"[!]: {str(e)}")

    # Can remove all listeners at once
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_remove_daemon_listeners(self, daemon: MoneroDaemonRpc) -> None:
        listeners: list[DaemonNotificationCollector] = [DaemonNotificationCollector(daemon), DaemonNotificationCollector(daemon)]
        for listener in listeners:
            daemon.add_listener(listener)
        assert len(daemon.get_listeners()) == 2

        daemon.remove_listeners()
        assert len(daemon.get_listeners()) == 0

    # Can start and stop listening
    @pytest.mark.skipif(Utils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_start_stop_listening(self, daemon: MoneroDaemonRpc) -> None:
        # add listener
        listener: DaemonNotificationCollector = DaemonNotificationCollector(daemon)
        auto_remove_listener: DaemonNotificationCollector = DaemonNotificationCollector(daemon, True)
        daemon.add_listener(listener)
        daemon.add_listener(auto_remove_listener)
        assert len(daemon.get_listeners()) == 2

        # mine blocks and collect notifications
        BlockchainUtils.wait_for_blocks(10)

        # test notifications
        assert listener.num_block_hashes > 0, "Daemon listener didn't collect any block hash"
        assert listener.num_block_headers > 0, "Daemon listener didn't collect any block header"
        assert listener.num_block_headers == listener.num_block_hashes, f"Count mismatch {listener.num_block_hashes} != {listener.num_block_headers}"

        # test autoremove listener
        assert auto_remove_listener.num_block_headers == 1
        assert auto_remove_listener.num_block_hashes == 1
        assert len(daemon.get_listeners()) == 1

        # remove listener
        daemon.remove_listener(listener)
        assert len(daemon.get_listeners()) == 0
