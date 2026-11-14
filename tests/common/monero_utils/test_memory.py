from __future__ import annotations

import gc
import logging
import subprocess
import sys

import pytest
from monero import (
    MoneroBlock,
    MoneroIncomingTransfer,
    MoneroOutputWallet,
    MoneroTx,
    MoneroTxWallet,
    MoneroUtils,
)

from utils import BaseTestClass

if sys.platform != "win32":
    import resource

logger: logging.Logger = logging.getLogger("TestMoneroUtilsMemory")


@pytest.mark.unit
class TestMoneroUtilsMemory(BaseTestClass):
    """Monero utilities memory unit tests."""

    def test_free_block_breaks_tx_backlink(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        MoneroUtils.free(block)
        assert tx.block is None

    def test_free_blocks_list(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 1
        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx1.block = block1
        block1.txs = [tx1]

        block2: MoneroBlock = MoneroBlock()
        block2.height = 2
        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        tx2.block = block2
        block2.txs = [tx2]

        MoneroUtils.free([block1, block2])
        assert tx1.block is None
        assert tx2.block is None

    def test_free_tx_without_block_does_not_crash(self) -> None:
        # free(tx) creates a throwaway placeholder block for an unconfirmed
        # tx, then immediately frees it. Net no-op on tx.block, but exercises
        # that code path safely
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        assert tx.block is None
        MoneroUtils.free(tx)
        assert tx.block is None

    def test_free_tx_with_block(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        MoneroUtils.free(tx)
        assert tx.block is None

    def test_free_txs_list_confirmed_and_unconfirmed(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        confirmed: MoneroTxWallet = MoneroTxWallet()
        confirmed.hash = "a" * 64
        confirmed.block = block
        block.txs = [confirmed]

        unconfirmed: MoneroTxWallet = MoneroTxWallet()
        unconfirmed.hash = "b" * 64

        MoneroUtils.free([confirmed, unconfirmed])
        assert confirmed.block is None
        assert unconfirmed.block is None

    def test_free_transfers_list(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.tx = tx

        MoneroUtils.free([transfer])
        assert transfer.tx.block is None

    def test_free_outputs_list(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.block = block
        block.txs = [tx]

        output: MoneroOutputWallet = MoneroOutputWallet()
        output.tx = tx

        MoneroUtils.free([output])
        assert output.tx.block is None

    @pytest.mark.skipif(sys.platform == "win32", reason="resource module (RSS measurement) is not available on Windows")
    def test_free_breaks_reference_cycle_avoids_leak(self) -> None:
        # regression guard for the leak demonstrated manually: building
        # block<->tx cycles and dropping every Python reference without
        # calling free() leaves the C++ shared_ptr cycle permanently
        # unreachable-but-alive (confirmed: 2,000,000 such tx objects grew
        # RSS by ~2.4GB with gc.collect() unable to reclaim any of it). This
        # test builds a much smaller-but-still-telling batch, always calling
        # free() before dropping references, and asserts memory stays roughly flat.
        def rss_mb() -> float:
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

        def run_batch(rounds: int) -> None:
            for _ in range(rounds):
                for _ in range(50):
                    block: MoneroBlock = MoneroBlock()
                    block.height = 100
                    txs: list[MoneroTx] = []
                    for i in range(20):
                        tx: MoneroTxWallet = MoneroTxWallet()
                        tx.hash = "a" * 63 + str(i % 10)
                        tx.block = block
                        txs.append(tx)
                    block.txs = txs
                    MoneroUtils.free(block)

        gc.disable()
        try:
            run_batch(20)  # unmeasured warmup: absorb one-time allocator growth
            baseline: float = rss_mb()
            run_batch(200)  # measured: 200 * 50 * 20 = 200,000 tx objects
            after: float = rss_mb()
        finally:
            gc.enable()

        growth_mb: float = after - baseline
        logger.debug(f"RSS growth after freeing 200,000 tx objects (post-warmup): {growth_mb:.1f} MB")
        # generous bound: a real leak of this shape grows ~1.2KB/tx (~240MB for
        # 200,000 tx); this only needs to rule out that magnitude of leak, not
        # pin down normal allocator noise
        assert growth_mb < 100, f"RSS grew {growth_mb:.1f} MB after freeing 200,000 tx objects -- possible leak"

    def test_free_none_does_not_crash(self) -> None:
        script: str = "import monero\nmonero.MoneroUtils.free(None)\n"
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"free(None) crashed the interpreter (exit code {result.returncode}) "
            "instead of raising a Python exception (or being a documented no-op)"
        )

    def test_free_transfers_missing_tx_raises(self) -> None:
        # free([transfers]) delegates to get_blocks_from_transfers(): a transfer
        # with no tx must surface a catchable exception, not segfault
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 500000
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.free([transfer])
        assert str(exc_info.value) == "Transfer has no tx"

    def test_free_outputs_missing_tx_raises(self) -> None:
        # free([outputs]) delegates to get_blocks_from_outputs(): same guarantee
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1000000
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.free([output])
        assert str(exc_info.value) == "Output has no tx"
