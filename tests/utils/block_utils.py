import logging

from typing import Optional
from abc import ABC
from monero import (
    MoneroAltChain,
    MoneroBlockHeader, MoneroBlock,
    MoneroBlockTemplate, MoneroDaemonRpc
)

from .gen_utils import GenUtils
from .context import TestContext, BinaryBlockContext
from .tx_utils import TxUtils

logger: logging.Logger = logging.getLogger("BlockUtils")


class BlockUtils(ABC):
    """Block test utilities."""

    @classmethod
    def test_block_header(cls, header: MoneroBlockHeader, is_full: Optional[bool], debug: bool = True) -> None:
        """Test a block header.

        :param MoneroBlockHeader header: header to test.
        :param bool | None is_full: check full header.
        """
        if debug:
            logger.debug(f"Testing block header: {header.serialize()}")
        # test base fields
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
        # test full header details
        cls.test_full_header(header, is_full)

    @classmethod
    def test_full_header(cls, header: MoneroBlockHeader, is_full: Optional[bool]) -> None:
        """Test full header details.

        :param MoneroBlockHeader header: header to test full details.
        :param bool | None is_full: indicates if `header`'s full details should be defined.
        """
        logger.debug(f"Testing full header: {header.serialize()}")

        # num_txs always defined
        assert header.num_txs is not None
        assert header.num_txs >= 0

        if is_full:
            # check full block
            assert header.size is not None
            assert header.depth is not None
            assert header.difficulty_low is not None
            assert header.difficulty_high is not None
            assert header.cumulative_difficulty_low is not None
            assert header.cumulative_difficulty_high is not None
            assert header.hash is not None
            assert header.miner_tx_hash is not None
            assert header.weight is not None
            assert header.size > 0
            assert header.depth >= 0
            assert header.difficulty_low > 0
            assert header.difficulty_high >= 0
            assert header.cumulative_difficulty_low > 0
            assert header.cumulative_difficulty_high >= 0
            assert 64 == len(header.hash)
            assert 64 == len(header.miner_tx_hash)
            assert header.orphan_status is not None
            assert header.reward is not None
            assert header.weight is not None
            assert header.weight > 0
        else:
            assert header.size is None
            assert header.depth is None
            assert header.difficulty_low is None
            assert header.difficulty_high is None
            assert header.cumulative_difficulty_low is None
            assert header.cumulative_difficulty_high is None
            assert header.hash is None
            assert header.miner_tx_hash is None
            assert header.orphan_status is None
            assert header.reward is None
            assert header.weight is None

    @classmethod
    def test_block(cls, block: MoneroBlock, ctx: TestContext) -> None:
        """Test a block

        :param MoneroBlock | None block: block to test.
        :param TestContext ctx: test context.
        """
        logger.debug(f"Testing block: {block.serialize()}")

        # test required fields
        assert block.miner_tx is not None, "Expected block miner tx"
        # TODO: miner tx doesn't have as much stuff, can't call TxUtils.test_tx?
        TxUtils.test_miner_tx(block.miner_tx)
        cls.test_block_header(block, ctx.header_is_full, False)

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

            # test duplicates
            num_block_txs: int = len(block.txs)
            num_tx_hashes: int = len(block.tx_hashes)

            if block.num_txs is not None:
                assert block.num_txs == num_block_txs, f"Expected {block.num_txs}, got {num_block_txs}"
                assert block.num_txs == num_tx_hashes, f"Expected {block.num_txs}, got {num_tx_hashes}"
                assert num_tx_hashes == len(set(block.tx_hashes)), "Duplicate tx hashes found in block"
            else:
                assert num_block_txs == 0
                assert num_tx_hashes == 0

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
        """Test get blocks by range.

        :param MoneroDaemonRpc daemon: daemon to test.
        :param int | None start_height: range start height.
        :param int | None end_height: range end height.
        :param int chain_height: blockchain height.
        :param bool chunked: get blocks range chunked.
        :param BinaryBlockContext: binary block test context.
        """
        # fetch blocks by range
        real_start_height: int = 0 if start_height is None else start_height
        real_end_height: int = chain_height - 1 if end_height is None else end_height
        blocks: list[MoneroBlock]

        if chunked:
            blocks = daemon.get_blocks_by_range_chunked(start_height, end_height)
        else:
            blocks = daemon.get_blocks_by_range(start_height, end_height)

        num_blocks: int = len(blocks)
        expected_num_blocks: int = real_end_height - real_start_height + 1
        assert expected_num_blocks == num_blocks, f"Expected {expected_num_blocks} block(s), got {num_blocks}"

        # test each block
        for i, block in enumerate(blocks):
            assert real_start_height + i == block.height
            cls.test_block(block, block_ctx)

    @classmethod
    def is_tx_in_block(cls, tx_hash: str | None, block: MoneroBlock) -> bool:
        """Check if transaction is included in block.

        :param str | None tx_hash: tx's hash to check if included in block.
        :param MoneroBlock block: block to check if `tx` is included in.
        """
        # validate tx hash
        assert tx_hash is not None
        assert len(tx_hash) > 0

        # search tx hash in block txs
        for block_tx in block.txs:
            if block_tx.hash == tx_hash:
                return True

        return False

    @classmethod
    def test_block_template(cls, template: MoneroBlockTemplate) -> None:
        """Test a mining block template.

        :param MoneroBlockTemplate template: mining block template to test.
        """
        logger.debug(f"Testing block template: {template.serialize()}")
        assert template.block_template_blob is not None
        assert template.block_hashing_blob is not None
        assert template.difficulty_low is not None
        assert template.difficulty_high is not None
        assert template.expected_reward is not None
        assert template.height is not None
        assert template.prev_hash is not None
        assert template.reserved_offset is not None
        assert template.seed_height is not None
        assert template.seed_height is not None
        assert template.seed_height >= 0
        assert template.seed_hash is not None
        assert len(template.seed_hash) > 0
        # next seed hash can be null or initialized TODO: test circumstances for each

    @classmethod
    def test_alt_chain(cls, alt_chain: MoneroAltChain) -> None:
        """Test daemon alternative chain info.

        :param MoneroAltChain alt_chain: alternative chain info to test.
        """
        logger.debug(f"Testing alternative chain: {alt_chain.serialize()}")
        assert len(alt_chain.block_hashes) > 0
        GenUtils.test_unsigned_big_integer(alt_chain.difficulty_low, True)
        GenUtils.test_unsigned_big_integer(alt_chain.difficulty_high)
        assert alt_chain.height is not None
        assert alt_chain.length is not None
        assert alt_chain.main_chain_parent_block_hash is not None
        assert alt_chain.height > 0
        assert alt_chain.length > 0
        assert 64 == len(alt_chain.main_chain_parent_block_hash)
