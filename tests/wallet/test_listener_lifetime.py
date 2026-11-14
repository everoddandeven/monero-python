from __future__ import annotations

import gc
import weakref

import pytest
from monero import MoneroWalletFull, MoneroWalletListener

from utils import BaseTestClass, TestUtils as Utils


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

    #endregion
