import logging

from typing import Optional
from abc import ABC
from monero import (
    MoneroBlockHeader, MoneroBlock, MoneroDaemonRpc
)

from .binary_block_context import BinaryBlockContext
from .test_context import TestContext
from .assert_utils import AssertUtils
from .tx_utils import TxUtils

logger: logging.Logger = logging.getLogger("BlockUtils")


class BlockUtils(ABC):

    @classmethod
    def test_block_header(cls, header: MoneroBlockHeader, is_full: Optional[bool]):
        AssertUtils.assert_not_none(header)
        assert header.height is not None
        AssertUtils.assert_true(header.height >= 0)
        assert header.major_version is not None
        AssertUtils.assert_true(header.major_version > 0)
        assert header.minor_version is not None
        AssertUtils.assert_true(header.minor_version >= 0)
        assert header.timestamp is not None
        if header.height == 0:
            AssertUtils.assert_true(header.timestamp == 0)
        else:
            AssertUtils.assert_true(header.timestamp > 0)
        AssertUtils.assert_not_none(header.prev_hash)
        AssertUtils.assert_not_none(header.nonce)
        if header.nonce == 0:
            # TODO (monero-project): why is header nonce 0?
            logger.warning(f"header nonce is 0 at height {header.height}")
        else:
            assert header.nonce is not None
            AssertUtils.assert_true(header.nonce > 0)
        AssertUtils.assert_is_none(header.pow_hash)  # never seen defined
        if is_full:
            assert header.size is not None
            assert header.depth is not None
            assert header.difficulty is not None
            assert header.cumulative_difficulty is not None
            assert header.hash is not None
            assert header.miner_tx_hash is not None
            assert header.num_txs is not None
            assert header.weight is not None
            AssertUtils.assert_true(header.size > 0)
            AssertUtils.assert_true(header.depth >= 0)
            AssertUtils.assert_true(header.difficulty > 0)
            AssertUtils.assert_true(header.cumulative_difficulty > 0)
            AssertUtils.assert_equals(64, len(header.hash))
            AssertUtils.assert_equals(64, len(header.miner_tx_hash))
            AssertUtils.assert_true(header.num_txs >= 0)
            AssertUtils.assert_not_none(header.orphan_status)
            AssertUtils.assert_not_none(header.reward)
            AssertUtils.assert_not_none(header.weight)
            AssertUtils.assert_true(header.weight > 0)
        else:
            AssertUtils.assert_is_none(header.size)
            AssertUtils.assert_is_none(header.depth)
            AssertUtils.assert_is_none(header.difficulty)
            AssertUtils.assert_is_none(header.cumulative_difficulty)
            AssertUtils.assert_is_none(header.hash)
            AssertUtils.assert_is_none(header.miner_tx_hash)
            AssertUtils.assert_is_none(header.num_txs)
            AssertUtils.assert_is_none(header.orphan_status)
            AssertUtils.assert_is_none(header.reward)
            AssertUtils.assert_is_none(header.weight)

    @classmethod
    def test_block(cls, block: Optional[MoneroBlock], ctx: TestContext):
        # test required fields
        assert block is not None, "Expected MoneroBlock, got None"
        assert block.miner_tx is not None, "Expected block miner tx"
        TxUtils.test_miner_tx(block.miner_tx) # TODO: miner tx doesn't have as much stuff, can't call testTx?
        cls.test_block_header(block, ctx.header_is_full)

        if ctx.has_hex:
            assert block.hex is not None
            AssertUtils.assert_true(len(block.hex) > 1)
        else:
            AssertUtils.assert_is_none(block.hex)

        if ctx.has_txs:
            AssertUtils.assert_not_none(ctx.tx_context)
            for tx in block.txs:
                AssertUtils.assert_true(block == tx.block)
                TxUtils.test_tx(tx, ctx.tx_context)

        else:
            AssertUtils.assert_is_none(ctx.tx_context)
            assert len(block.txs) == 0, "No txs expected"

    @classmethod
    def test_get_blocks_range(
        cls,
        daemon: MoneroDaemonRpc,
        start_height: Optional[int],
        end_height: Optional[int],
        chain_height: int,
        chunked: bool,
        block_ctx: BinaryBlockContext
    ) -> None:
        # fetch blocks by range
        real_start_height = 0 if start_height is None else start_height
        real_end_height = chain_height - 1 if end_height is None else end_height
        blocks = daemon.get_blocks_by_range_chunked(start_height, end_height) if chunked else daemon.get_blocks_by_range(start_height, end_height)
        AssertUtils.assert_equals(real_end_height - real_start_height + 1, len(blocks))

        # test each block
        for i, block in enumerate(blocks):
            AssertUtils.assert_equals(real_start_height + i, block.height)
            cls.test_block(block, block_ctx)
