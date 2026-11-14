from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroDestination,
    MoneroSubmitTxResult,
    MoneroTx,
    MoneroTxConfig,
    MoneroWalletRpc,
)

from utils import DaemonUtils, TestContext, TestUtils as Utils, TxUtils, TxWalletUtils, WalletTxsUtils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcTxs")


@pytest.mark.integration
class TestMoneroDaemonRpcTxs(BaseTestMoneroDaemonRpc):
    """Rpc daemon txs integration tests."""

    # Can get a transaction by hash and without pruning
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_tx_by_hash(self, daemon: MoneroDaemonRpc) -> None:
        # fetch tx hashses to test
        tx_hashes: list[str] = DaemonUtils.get_confirmed_tx_hashes(daemon)

        # context for creating txs
        ctx: TestContext = TestContext()
        ctx.is_pruned = False
        ctx.is_confirmed = True
        ctx.from_get_tx_pool = False

        # fetch each tx by hash without pruning
        for tx_hash in tx_hashes:
            tx: MoneroTx | None = daemon.get_tx(tx_hash)
            TxUtils.test_tx(tx, ctx)

        # fetch each tx by hash with pruning
        for tx_hash in tx_hashes:
            tx: MoneroTx | None = daemon.get_tx(tx_hash, True)
            ctx.is_pruned = True
            TxUtils.test_tx(tx, ctx)

        # fetch invalid hash
        with pytest.raises(Exception) as exc_info:
            daemon.get_tx("invalid tx hash")
        assert str(exc_info.value) == "Invalid transaction hash"

    # Can get transactions by hashes with and without pruning
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5, only_rerun=[])
    def test_get_txs_by_hashes(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        # fetch tx hashses to test
        tx_hashes: list[str] = DaemonUtils.get_confirmed_tx_hashes(daemon)
        assert len(tx_hashes) > 0, "No tx hashes found"

        # context for creating txs
        ctx: TestContext = TestContext()
        ctx.is_pruned = False
        ctx.is_confirmed = True
        ctx.from_get_tx_pool = False

        # fetch each tx by hash without pruning
        txs: list[MoneroTx] = daemon.get_txs(tx_hashes)
        assert len(txs) == len(tx_hashes), f"Expected len(txs) == len(tx_hashes), got {len(txs)} == {len(tx_hashes)}"
        for tx in txs:
            TxUtils.test_tx(tx, ctx)

        # fetch each tx by hash with pruning
        txs = daemon.get_txs(tx_hashes, True)
        ctx.is_pruned = True
        assert len(txs) == len(tx_hashes), f"Expected len(txs) == len(tx_hashes), got {len(txs)} == {len(tx_hashes)}"
        for tx in txs:
            TxUtils.test_tx(tx, ctx)

        # fetch missing hash
        dest: MoneroDestination = MoneroDestination()
        dest.address = wallet.get_primary_address()
        dest.amount = TxWalletUtils.MAX_FEE
        config: MoneroTxConfig = MoneroTxConfig()
        config.account_index = 0
        config.destinations.append(dest)
        tx = wallet.create_tx(config)
        assert tx.hash is not None
        daemon_tx: MoneroTx | None = daemon.get_tx(tx.hash)
        assert daemon_tx is None
        tx_hashes.append(tx.hash)
        num_txs: int = len(txs)
        txs = daemon.get_txs(tx_hashes)
        assert num_txs == len(txs)

        # fetch invalid hash
        with pytest.raises(Exception) as exc_info:
            daemon.get_txs(["invalid tx hash"])
        assert str(exc_info.value) == "Invalid transaction hash"

    # Can get transactions by hashes that are in the transaction pool
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_by_hashes_in_pool(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        # wait for wallet's txs in the pool to clear to ensure reliable sync
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # submit txs to the pool but don't relay
        tx_hashes: list[str] = []
        for i in range(1, 3):
            tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, i)
            assert tx.hash is not None
            assert tx.full_hex is not None
            assert len(tx.full_hex) > 0
            result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
            DaemonUtils.test_submit_tx_result_good(result)
            assert result.is_relayed is False
            tx_hashes.append(tx.hash)

        # fetch txs by hash
        logger.debug("Fetching txs...")
        txs: list[MoneroTx] = daemon.get_txs(tx_hashes)
        num_txs: int = len(txs)
        logger.debug(f"Fetched {num_txs} tx(s)")

        # context for testing tx
        ctx: TestContext = TestContext()
        ctx.is_pruned = False
        ctx.is_confirmed = False
        ctx.from_get_tx_pool = False

        # test fetched txs
        assert len(tx_hashes) == num_txs
        for tx in txs:
            TxUtils.test_tx(tx, ctx)

        # clear txs from pool
        daemon.flush_tx_pool(tx_hashes)
        wallet.sync()

    # Can get a transaction hex by hash with and without pruning
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_tx_hex_by_hash(self, daemon: MoneroDaemonRpc) -> None:
        # fetch transaction hashes to test
        tx_hashes: list[str] = DaemonUtils.get_confirmed_tx_hashes(daemon)

        # fetch each tx hex by hash with and without pruning
        hexes: list[str | None] = []
        hexes_pruned: list[str | None] = []
        for tx_hash in tx_hashes:
            hexes.append(daemon.get_tx_hex(tx_hash))
            hexes_pruned.append(daemon.get_tx_hex(tx_hash, True))

        # test results
        assert len(hexes) == len(tx_hashes)
        assert len(hexes_pruned) == len(tx_hashes)

        for i, tx_hex in enumerate(hexes):
            pruned_tx_hex: str | None = hexes_pruned[i]
            assert tx_hex is not None
            assert pruned_tx_hex is not None
            assert len(pruned_tx_hex) > 0
            # pruned hex is shorter
            assert len(tx_hex) >= len(pruned_tx_hex)

        # fetch invalid hash
        with pytest.raises(Exception) as exc_info:
            daemon.get_tx_hex("invalid tx hash")
        assert str(exc_info.value) == "Invalid transaction hash"

    # Can get transaction hexes by hashes with and without pruning
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_tx_hexes_by_hashes(self, daemon: MoneroDaemonRpc) -> None:
        # fetch transaction hashes to test
        tx_hashes: list[str] = DaemonUtils.get_confirmed_tx_hashes(daemon)

        # fetch tx hexes by hash with and without pruning
        hexes: list[str] = daemon.get_tx_hexes(tx_hashes)
        hexes_pruned: list[str] = daemon.get_tx_hexes(tx_hashes, True)

        # test results
        assert len(hexes) == len(tx_hashes)
        assert len(hexes_pruned) == len(tx_hashes)
        for i, tx_hex in enumerate(hexes):
            pruned_tx_hex: str = hexes_pruned[i]
            assert tx_hex is not None
            assert pruned_tx_hex is not None
            assert len(pruned_tx_hex) > 0
            # pruned hex is shorter
            assert len(tx_hex) >= len(pruned_tx_hex)

        # fetch invalid hash
        tx_hashes.append("invalid tx hash")
        with pytest.raises(Exception) as exc_info:
            daemon.get_tx_hexes(tx_hashes)
        assert str(exc_info.value) == "Invalid transaction hash"
