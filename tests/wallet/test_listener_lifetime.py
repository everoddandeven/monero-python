from __future__ import annotations

import gc
import weakref

from time import monotonic, sleep

import pytest
from monero import MoneroWalletFull, MoneroWalletListener, MoneroWalletRpc

from utils import BaseTestClass, FakeWalletRpcServer, TestUtils as Utils


@pytest.mark.unit
class TestMoneroWalletListenerLifetime(BaseTestClass):
    """A listener that Python does not reference any more must stay alive while the wallet has it, as the threads of the wallet call it."""

    #region Tests

    # The wallet keeps its listener alive
    def test_wallet_keeps_its_listener_alive(self) -> None:
        wallet: MoneroWalletFull = Utils.get_wallet_full_offline()
        listener: MoneroWalletListener = MoneroWalletListener()
        listener_ref: weakref.ref[MoneroWalletListener] = weakref.ref(listener)
        wallet.add_listener(listener)
        try:
            del listener
            gc.collect()
            assert listener_ref() is not None, "The wallet does not keep alive its listener"
            assert len(wallet.get_listeners()) == 1
        finally:
            listener_back: MoneroWalletListener | None = listener_ref()
            if listener_back is not None:
                wallet.remove_listener(listener_back)
        assert len(wallet.get_listeners()) == 0

    # The wallet rpc is destroyed while its poller waits for the server
    def test_rpc_wallet_is_destroyed_with_a_request_in_flight(self) -> None:
        # The server of this process answers from a thread of python, which needs the GIL. The destruction of the wallet waits for the
        # request of the poller, and it used to do it with the GIL held: both waited for the other one until the request timed out.
        with FakeWalletRpcServer(response_delay=0.5) as server:
            wallet: MoneroWalletRpc = MoneroWalletRpc(server.uri, timeout_ms=20000)
            wallet.set_poll_period_in_ms(20)
            wallet.add_listener(MoneroWalletListener())
            requests: int = server.num_requests
            deadline: float = monotonic() + 10
            while server.num_requests == requests and monotonic() < deadline:
                sleep(0.005)
            assert server.num_requests > requests, "The poller did not ask the server"

            start: float = monotonic()
            del wallet
            gc.collect()
            elapsed: float = monotonic() - start
            assert elapsed < 10, f"The destruction of the wallet took {elapsed:.1f} s"

    #endregion
