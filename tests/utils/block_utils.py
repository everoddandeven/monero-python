import logging

from typing import Optional
from abc import ABC
from monero import (
    MoneroBlockHeader, MoneroBlock, MoneroDaemonRpc
)

from .binary_block_context import BinaryBlockContext
from .test_context import TestContext
from .tx_utils import TxUtils

logger: logging.Logger = logging.getLogger("BlockUtils")


class BlockUtils(ABC):
    """Block utilities"""

    @classmethod
    def test_block_header(cls, header: Optional[MoneroBlockHeader], is_full: Optional[bool]):
        """
        Test a block header

        :param MoneroBlockHeader header: header to test
        :param bool | None is_full: check full header
        """
        # test base fields
        assert header is not None
        assert header.height is not None
        assert header.height >= 0
        assert header.major_version is not None
        assert header.major_version > 0
        assert header.minor_version is not None
        assert header.minor_version >= 0
        assert header.timestamp is not None
        if header.height == 0:
            assert header.timestamp == 0
        else:
            assert header.timestamp > 0
        assert header.prev_hash is not None
        assert header.nonce is not None
        if header.nonce == 0:
            # TODO (monero-project): why is header nonce 0?
            logger.warning(f"header nonce is 0 at height {header.height}")
        else:
            assert header.nonce > 0
        # never seen defined
        assert header.pow_hash is None
        if is_full:
            # check full block
            assert header.size is not None
            assert header.depth is not None
            assert header.difficulty is not None
            assert header.cumulative_difficulty is not None
            assert header.hash is not None
            assert header.miner_tx_hash is not None
            assert header.num_txs is not None
            assert header.weight is not None
            assert header.size > 0
            assert header.depth >= 0
            assert header.difficulty > 0
            assert header.cumulative_difficulty > 0
            assert 64 == len(header.hash)
            assert 64 == len(header.miner_tx_hash)
            assert header.num_txs >= 0
            assert header.orphan_status is not None
            assert header.reward is not None
            assert header.weight is not None
            assert header.weight > 0
        else:
            assert header.size is None
            assert header.depth is None
            assert header.difficulty is None
            assert header.cumulative_difficulty is None
            assert header.hash is None
            assert header.miner_tx_hash is None
            assert header.num_txs is None
            assert header.orphan_status is None
            assert header.reward is None
            assert header.weight is None

    @classmethod
    def test_block(cls, block: Optional[MoneroBlock], ctx: TestContext) -> None:
        """
        Test a block

        :param MoneroBlock | None block: block to test
        :param TestContext ctx: test context
        """
        # test required fields
        assert block is not None, "Expected MoneroBlock, got None"
        assert block.miner_tx is not None, "Expected block miner tx"
        # TODO: miner tx doesn't have as much stuff, can't call TxUtils.test_tx?
        TxUtils.test_miner_tx(block.miner_tx)
        cls.test_block_header(block, ctx.header_is_full)

        if ctx.has_hex:
            assert block.hex is not None
            assert len(block.hex) > 1
        else:
            assert block.hex is None

        if ctx.has_txs:
            assert ctx.tx_context is not None
            for tx in block.txs:
                assert block == tx.block
                TxUtils.test_tx(tx, ctx.tx_context)

        else:
            assert ctx.tx_context is None
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
        """
        Test get blocks by range

        :param MoneroDaemonRpc daemon: daemon to test
        :param int | None start_height: range start height
        :param int | none end_height: range end height
        :param int chain_height: blockchain height
        :param bool chunked: get blocks range chunked
        :param BinaryBlockContext: binary block test context
        """
        # fetch blocks by range
        real_start_height = 0 if start_height is None else start_height
        real_end_height = chain_height - 1 if end_height is None else end_height
        blocks = daemon.get_blocks_by_range_chunked(start_height, end_height) if chunked else daemon.get_blocks_by_range(start_height, end_height)
        assert real_end_height - real_start_height + 1 == len(blocks)

        # test each block
        for i, block in enumerate(blocks):
            assert real_start_height + i == block.height
            cls.test_block(block, block_ctx)
