from __future__ import annotations

import gc
import logging
import weakref

from time import monotonic, sleep
from typing import override

import pytest
from monero import MoneroBlockHeader, MoneroDaemonListener, MoneroDaemonRpc

from utils import BaseTestClass, FakeDaemonRpcServer

logger: logging.Logger = logging.getLogger("TestMoneroDaemonListenerLifetime")


class _HeaderRecorder(MoneroDaemonListener):
    """Listener that only records the heights it is notified of, in a list that the test keeps."""

    def __init__(self, heights: list[int]) -> None:
        super().__init__()
        self._heights: list[int] = heights

    @override
    def on_block_header(self, header: MoneroBlockHeader) -> None:
        assert header.height is not None
        self._heights.append(header.height)


@pytest.mark.unit
class TestMoneroDaemonListenerLifetime(BaseTestClass):
    """A listener that Python does not reference any more must stay alive while the daemon has it.

    The poller of the daemon calls its listeners from a thread of its own. When the listener was freed by Python, the poller called a
    deleted object, and the process died with a segmentation fault.
    """

    #region Tests

    # The poller notifies a listener that nothing but the daemon references
    def test_listener_is_notified_after_python_drops_it(self) -> None:
        heights: list[int] = []
        with FakeDaemonRpcServer() as server:
            daemon: MoneroDaemonRpc = MoneroDaemonRpc(server.uri)
            daemon.set_poll_period_in_ms(20)
            listener: _HeaderRecorder = _HeaderRecorder(heights)
            listener_ref: weakref.ref[_HeaderRecorder] = weakref.ref(listener)
            daemon.add_listener(listener)
            try:
                # the only reference left is the one that add_listener keeps
                del listener
                gc.collect()
                assert listener_ref() is not None, "The daemon does not keep alive its listener"

                # it is called many times, by the thread of the poller, while the objects around it are collected
                deadline: float = monotonic() + 10
                while len(heights) < 10 and monotonic() < deadline:
                    gc.collect()
                    sleep(0.02)
                assert len(heights) >= 10, f"The listener was notified {len(heights)} times"
                assert heights == sorted(heights), f"Block headers out of order: {heights}"
            finally:
                daemon.remove_listeners()

    # The listener is released with the daemon that kept it
    def test_listener_is_released_with_the_daemon(self) -> None:
        heights: list[int] = []
        with FakeDaemonRpcServer() as server:
            daemon: MoneroDaemonRpc = MoneroDaemonRpc(server.uri)
            daemon.set_poll_period_in_ms(20)
            listener: _HeaderRecorder = _HeaderRecorder(heights)
            listener_ref: weakref.ref[_HeaderRecorder] = weakref.ref(listener)
            daemon.add_listener(listener)
            del listener
            gc.collect()
            assert listener_ref() is not None

            # removed once the poller has run: removing a listener right after adding it can make the destruction of the daemon wait forever
            deadline: float = monotonic() + 10
            while len(heights) < 2 and monotonic() < deadline:
                sleep(0.02)
            assert len(heights) >= 2, f"The listener was notified {len(heights)} times"

            daemon.remove_listeners()
            del daemon
            gc.collect()
            assert listener_ref() is None, "The listener is kept alive after its daemon is gone"

    #endregion
