from __future__ import annotations

from typing import Any

import pytest
from monero import MoneroSyncResult, MoneroTx, MoneroTxQuery, MoneroTxWallet, MoneroWalletRpc

from utils import BaseTestClass, FakeWalletRpcServer, WalletTxTracker


class _Daemon:
    """The part of a daemon that the tracker uses when there is nothing to wait for."""

    def get_height(self) -> int:
        return 0

    def get_tx_pool(self) -> list[MoneroTx]:
        return []

    def stop_mining(self) -> None:
        pass


class _Wallet:
    """A wallet that is not a wallet rpc and has no pending txs, that counts the times that it was asked which outputs are spent."""

    def __init__(self) -> None:
        self.num_rescans: int = 0

    def sync(self) -> MoneroSyncResult:
        result: MoneroSyncResult = MoneroSyncResult()
        result.num_blocks_fetched = 0
        return result

    def get_txs(self, query: MoneroTxQuery) -> list[MoneroTxWallet]:
        return []

    def get_height(self) -> int:
        return 0

    def rescan_spent(self) -> None:
        self.num_rescans += 1


@pytest.mark.unit
class TestWalletTxTracker(BaseTestClass):
    """The tracker waits for the txs of a wallet to leave the pool, and then the wallet is fit for the next tx."""

    #region Tests

    # A wallet rpc is asked which of its outputs are spent, when its txs left the pool
    def test_rpc_wallet_rescans_spent_outputs_after_the_pool_is_clear(self) -> None:
        # the server of a wallet rpc sets back as unspent the inputs of a tx that it saw in the pool and that left it, 500 s after, and
        # the next tx used them: the daemon rejected it as a double spend (test_subtract_fee_from, in CI)
        tracker: WalletTxTracker = WalletTxTracker(_Daemon(), 10, "")  # type: ignore[arg-type]
        with FakeWalletRpcServer() as server:
            wallet: MoneroWalletRpc = MoneroWalletRpc(server.uri)
            tracker.wait_for_txs_to_clear_pool([wallet])
            methods: list[str] = server.methods
        assert "refresh" in methods, f"The wallet was not synced: {methods}"
        assert "rescan_spent" in methods, f"The wallet was not asked which outputs are spent: {methods}"
        assert methods.index("rescan_spent") > methods.index("refresh"), f"It was asked before it synced: {methods}"

    # Every wallet rpc of a list is asked, not only the first one
    def test_each_rpc_wallet_rescans_spent_outputs(self) -> None:
        tracker: WalletTxTracker = WalletTxTracker(_Daemon(), 10, "")  # type: ignore[arg-type]
        with FakeWalletRpcServer() as server1, FakeWalletRpcServer() as server2:
            wallets: list[Any] = [MoneroWalletRpc(server1.uri), MoneroWalletRpc(server2.uri)]
            tracker.wait_for_txs_to_clear_pool(wallets)
            assert "rescan_spent" in server1.methods
            assert "rescan_spent" in server2.methods

    # The other wallets are not asked: the full wallet follows its own outputs, and a wallet that is not a wallet rpc may not have it
    def test_other_wallets_do_not_rescan_spent_outputs(self) -> None:
        tracker: WalletTxTracker = WalletTxTracker(_Daemon(), 10, "")  # type: ignore[arg-type]
        wallet: _Wallet = _Wallet()
        tracker.wait_for_txs_to_clear_pool([wallet])  # type: ignore[list-item]
        assert wallet.num_rescans == 0

    #endregion
