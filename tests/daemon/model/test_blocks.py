from __future__ import annotations

import logging
import subprocess
import sys
from typing import LiteralString

import pytest
from monero import (
    MoneroBlock,
    MoneroBlockHeader,
    MoneroBlockTemplate,
    MoneroGetBlockHashesResult,
    MoneroGetBlocksByHashResult,
    MoneroTx,
)

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelBlocks")


@pytest.mark.unit
class TestMoneroDaemonModelBlocks(BaseTestClass):
    """Daemon blocks model unit tests."""

    def test_block_template_deserialize(self) -> None:
        template: MoneroBlockTemplate = MoneroBlockTemplate()
        template.block_template_blob = "abcd"
        template.block_hashing_blob = "ef01"
        template.prev_hash = "a" * 64
        template.seed_hash = "b" * 64
        template.next_seed_hash = "c" * 64
        template.difficulty_low = 5000
        template.difficulty_high = 0
        template.expected_reward = 600000000000
        template.height = 12345
        template.reserved_offset = 130
        template.seed_height = 0
        AssertUtils.assert_serialization_integrity(template)

    def test_block_header_deserialize(self) -> None:
        header: MoneroBlockHeader = MoneroBlockHeader()
        header.hash = "a" * 64
        header.height = 12345
        header.timestamp = 1600000000
        header.size = 2048
        header.weight = 2048
        header.long_term_weight = 2048
        header.depth = 10
        header.difficulty_low = 5000
        header.difficulty_high = 0
        header.cumulative_difficulty_low = 900000
        header.cumulative_difficulty_high = 0
        header.major_version = 16
        header.minor_version = 16
        header.nonce = 42
        header.miner_tx_hash = "b" * 64
        header.num_txs = 3
        header.orphan_status = False
        header.prev_hash = "c" * 64
        header.reward = 600000000000
        header.pow_hash = "d" * 64
        AssertUtils.assert_serialization_integrity(header)

    def test_block_deserialize(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.hash = "a" * 64
        block.height = 12345
        block.hex = "deadbeef"
        block.tx_hashes = ["b" * 64, "c" * 64]

        miner_tx: MoneroTx = MoneroTx()
        miner_tx.hash = "d" * 64
        miner_tx.is_miner_tx = True
        block.miner_tx = miner_tx

        tx: MoneroTx = MoneroTx()
        tx.hash = "e" * 64
        block.txs = [tx]

        restored: MoneroBlock = AssertUtils.assert_serialization_integrity(block)

        # nested txs are parsed and back-linked to the block
        assert restored.miner_tx is not None
        assert restored.miner_tx.hash == "d" * 64
        assert restored.miner_tx.is_miner_tx is True
        assert restored.miner_tx.block is not None and restored.miner_tx.block.height == 12345
        assert len(restored.txs) == 1
        assert restored.txs[0].hash == "e" * 64
        assert restored.txs[0].block is not None and restored.txs[0].block.height == 12345

    def test_get_block_hashes_result_deserialize(self) -> None:
        result: MoneroGetBlockHashesResult = MoneroGetBlockHashesResult()
        result.hashes = ["a" * 64, "b" * 64]
        result.start_height = 100
        result.current_height = 3000000
        AssertUtils.assert_serialization_integrity(result)

    def test_get_blocks_by_hash_result_deserialize(self) -> None:
        result: MoneroGetBlocksByHashResult = MoneroGetBlocksByHashResult()
        result.current_height = 3000000
        # blocks are serialized but from_property_tree() never reads them back
        # (monero_block has no from_property_tree of its own); see test below
        AssertUtils.assert_serialization_integrity(result)

    def test_get_blocks_by_hash_result_blocks_deserialize(self) -> None:
        result: MoneroGetBlocksByHashResult = MoneroGetBlocksByHashResult()
        block: MoneroBlock = MoneroBlock()
        block.hash = "a" * 64
        block.height = 100
        result.blocks = [block]
        json_str: str = result.serialize()
        logger.debug(f"Serialized get blocks by hash result: {json_str}")
        assert '"blocks"' in json_str
        restored: MoneroGetBlocksByHashResult = MoneroGetBlocksByHashResult.deserialize(json_str)
        assert len(restored.blocks) == 0

    def test_block_header_copy(self) -> None:
        header: MoneroBlockHeader = MoneroBlockHeader()
        header.hash = "a" * 64
        header.height = 100
        header.timestamp = 1700000000
        header.size = 1000
        header.weight = 1000
        header.major_version = 16
        header.minor_version = 16
        header.nonce = 12345
        header.reward = 600000000000

        copy: MoneroBlockHeader = header.copy()
        assert copy is not header
        assert copy.serialize() == header.serialize()

        # copy is independent of the original
        copy.height = 999
        assert header.height == 100

    def test_block_header_merge(self) -> None:
        a: MoneroBlockHeader = MoneroBlockHeader()
        a.hash = "a" * 64
        a.height = 100
        a.timestamp = 1700000000

        b: MoneroBlockHeader = a.copy()
        b.height = 200             # height can increase -> resolves to the higher value
        b.timestamp = 1800000000   # timestamp can increase -> resolves to the higher value
        b.size = 2000              # a.size is unset -> merge fills the gap

        a.merge(b)
        assert a.height == 200
        assert a.timestamp == 1800000000
        assert a.size == 2000
        assert a.hash == "a" * 64

    def test_block_header_merge_conflict_raises(self) -> None:
        # fields without special reconciliation (e.g. hash) must match on both
        # sides, or merge() raises rather than silently picking one
        a: MoneroBlockHeader = MoneroBlockHeader()
        a.hash = "a" * 64
        b: MoneroBlockHeader = MoneroBlockHeader()
        b.hash = "b" * 64
        with pytest.raises(Exception, match="[Cc]annot reconcile"):
            a.merge(b)

    def test_block_copy(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.hash = "a" * 64
        block.height = 100
        block.hex = "deadbeef"
        block.tx_hashes = ["b" * 64, "c" * 64]

        miner_tx: MoneroTx = MoneroTx()
        miner_tx.hash = "d" * 64
        miner_tx.is_miner_tx = True
        block.miner_tx = miner_tx

        tx: MoneroTx = MoneroTx()
        tx.hash = "e" * 64
        block.txs = [tx]

        copy: MoneroBlock = block.copy()
        assert copy is not block
        assert copy.serialize() == block.serialize()

        # miner tx and non-wallet txs are deep copied and back-linked to the copy
        assert copy.miner_tx is not None and copy.miner_tx is not block.miner_tx
        assert copy.miner_tx.hash == "d" * 64
        assert copy.miner_tx.block is copy
        assert len(copy.txs) == 1
        assert copy.txs[0] is not block.txs[0]
        assert copy.txs[0].hash == "e" * 64
        assert copy.txs[0].block is copy

    def test_block_merge(self) -> None:
        a: MoneroBlock = MoneroBlock()
        a.hash = "a" * 64
        a.height = 100
        b: MoneroBlock = a.copy()
        b.hex = "deadbeef"  # a.hex is unset -> merge fills the gap
        a.merge(b)
        assert a.hex == "deadbeef"

    def test_block_header_merge_dispatches_to_block_merge(self) -> None:
        a: MoneroBlock = MoneroBlock()
        a.height = 100
        b: MoneroBlock = MoneroBlock()
        b.height = 100
        b.hex = "deadbeef"  # a.hex is unset -> merge fills the gap

        MoneroBlockHeader.merge(a, b)
        assert a.hex == "deadbeef"

    def test_block_merge_adopts_other_miner_tx(self) -> None:
        a: MoneroBlock = MoneroBlock()
        a.height = 100
        # a.miner_tx is unset -> merge adopts other's miner tx and repoints its block at a

        b: MoneroBlock = MoneroBlock()
        b.height = 100
        miner_tx: MoneroTx = MoneroTx()
        miner_tx.hash = "a" * 64
        miner_tx.is_miner_tx = True
        b.miner_tx = miner_tx

        a.merge(b)
        assert a.miner_tx is not None
        assert a.miner_tx is b.miner_tx
        assert a.miner_tx.hash == "a" * 64
        assert a.miner_tx.block is a

    def test_block_merge_merges_distinct_miner_txs(self) -> None:
        a: MoneroBlock = MoneroBlock()
        a.height = 100
        miner_a: MoneroTx = MoneroTx()
        miner_a.hash = "a" * 64
        miner_a.is_confirmed = True  # required: tx merge() dereferences is_confirmed directly
        a.miner_tx = miner_a

        b: MoneroBlock = MoneroBlock()
        b.height = 100
        miner_b: MoneroTx = MoneroTx()
        miner_b.hash = "a" * 64
        miner_b.is_confirmed = True
        miner_b.num_confirmations = 5  # miner_a's num_confirmations is unset -> merge fills the gap
        b.miner_tx = miner_b

        a.merge(b)
        assert a.miner_tx is miner_a  # kept in place, fields merged into it
        assert a.miner_tx.num_confirmations == 5
        assert a.miner_tx.block is a

    def test_block_merge_txs_with_unset_hash_are_kept_distinct(self) -> None:
        script: LiteralString = (
            "import monero, sys\n"
            "a = monero.MoneroBlock()\n"
            "a.height = 100\n"
            "tx_a = monero.MoneroTx()\n"  # hash intentionally left unset
            "a.txs = [tx_a]\n"
            "b = monero.MoneroBlock()\n"
            "b.height = 100\n"
            "tx_b = monero.MoneroTx()\n"  # hash intentionally left unset
            "b.txs = [tx_b]\n"
            "a.merge(b)\n"
            "n = len(a.txs) if a.txs else 0\n"
            "sys.exit(0 if n == 2 else f'txs not kept distinct: len={n}')\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"Block.merge() did not keep unset-hash txs distinct (exit code {result.returncode}): "
            f"{result.stderr.strip()[-300:]}"
        )
