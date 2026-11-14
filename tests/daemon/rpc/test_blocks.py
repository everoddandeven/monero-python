from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAltChain,
    MoneroBlock,
    MoneroBlockHeader,
    MoneroBlockTemplate,
    MoneroDaemonRpc,
    MoneroGetBlockHashesResult,
    MoneroGetBlocksByHashResult,
    MoneroMinerTxSum,
)

from utils import AssertUtils, BlockUtils, DaemonUtils, MiningUtils, TestContext, TestUtils as Utils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcBlocks")


@pytest.mark.integration
class TestMoneroDaemonRpcBlocks(BaseTestMoneroDaemonRpc):
    """Rpc daemon blocks integration tests."""

    # Can get the blockchain height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height(self, daemon: MoneroDaemonRpc) -> None:
        height: int = daemon.get_height()
        logger.debug(f"Daemon height: {height}")
        assert height > 0, "Height must be greater than 0"

    # Can get a block hash by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_id_by_height(self, daemon: MoneroDaemonRpc) -> None:
        last_header: MoneroBlockHeader = daemon.get_last_block_header()
        logger.debug(f"Last block header height: {last_header.height}")
        assert last_header.height is not None
        hash_str: str = daemon.get_block_hash(last_header.height)
        logger.debug(f"Got block hash: {hash_str}")
        assert hash_str is not None
        assert 64 == len(hash_str), f"Invalid block hash '{hash_str}'"

    # Can get a block template
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_template(self, daemon: MoneroDaemonRpc) -> None:
        template: MoneroBlockTemplate = daemon.get_block_template(Utils.ADDRESS, 2)
        BlockUtils.test_block_template(template)

    # Can get the last block's header
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_last_block_header(self, daemon: MoneroDaemonRpc) -> None:
        last_header: MoneroBlockHeader = daemon.get_last_block_header()
        BlockUtils.test_block_header(last_header, True)

    # Can get a block header by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_header_by_hash(self, daemon: MoneroDaemonRpc) -> None:
        # retrieve last block by hash
        last_header: MoneroBlockHeader = daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = daemon.get_block_hash(last_header.height)
        header: MoneroBlockHeader = daemon.get_block_header_by_hash(hash_str)
        BlockUtils.test_block_header(header, True)
        AssertUtils.assert_equals(last_header, header)

        # retrieve by hash of previous to last block
        hash_str = daemon.get_block_hash(last_header.height - 1)
        header = daemon.get_block_header_by_hash(hash_str)
        BlockUtils.test_block_header(header, True)
        assert last_header.height - 1 == header.height

    # Can get a block header by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_header_by_height(self, daemon: MoneroDaemonRpc) -> None:
        # retrieve by height of last block
        last_header: MoneroBlockHeader = daemon.get_last_block_header()
        assert last_header.height is not None
        header: MoneroBlockHeader = daemon.get_block_header_by_height(last_header.height)
        BlockUtils.test_block_header(header, True)
        AssertUtils.assert_equals(last_header, header)

        # retrieve by height of previous to last block
        header = daemon.get_block_header_by_height(last_header.height - 1)
        BlockUtils.test_block_header(header, True)
        assert last_header.height - 1 == header.height

    # Can get block headers by range
    # TODO: test start with no end, vice versa, inclusivity
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_headers_by_range(self, daemon: MoneroDaemonRpc) -> None:
        # determine start and end height based on number of blocks and how many blocks ago
        num_blocks: int = 100
        num_blocks_ago: int = 100
        current_height: int = daemon.get_height()
        start_height: int = current_height - num_blocks_ago
        end_height: int = current_height - (num_blocks_ago - num_blocks) - 1

        # fetch headers
        headers: list[MoneroBlockHeader] = daemon.get_block_headers_by_range(start_height, end_height)

        # test headers
        assert num_blocks == len(headers)

        for i in range(num_blocks):
            header: MoneroBlockHeader = headers[i]
            assert start_height + i == header.height
            BlockUtils.test_block_header(header, True)

    # Can get a block by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_by_hash(self, daemon: MoneroDaemonRpc) -> None:
        # test config
        ctx: TestContext = TestContext()
        ctx.has_hex = True
        ctx.has_txs = False
        ctx.header_is_full = True

        # retrieve by hash of last block
        last_header: MoneroBlockHeader = daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = daemon.get_block_hash(last_header.height)
        block: MoneroBlock = daemon.get_block_by_hash(hash_str)
        assert block.height is not None
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(daemon.get_block_by_height(block.height), block)
        assert len(block.txs) == 0, f"No block tx expected, found: {len(block.txs)}"

        # retrieve by hash of previous to last block
        hash_str = daemon.get_block_hash(last_header.height - 1)
        block = daemon.get_block_by_hash(hash_str)
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(daemon.get_block_by_height(last_header.height - 1), block)
        assert len(block.txs) == 0, f"No block tx expected, found: {len(block.txs)}"

    # Can get blocks by hash which includes transactions (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_hash_binary(self, daemon: MoneroDaemonRpc) -> None:
        chain_height: int = daemon.get_height()
        genesis_hash: str = daemon.get_block_hash(0)

        # a non-zero start height resumes from there and ignores the hash list
        resume_height: int = chain_height - 5
        result: MoneroGetBlocksByHashResult = daemon.get_blocks_by_hash([genesis_hash], resume_height, False, 0)
        assert result.current_height is not None and result.current_height >= chain_height
        assert len(result.blocks) > 0
        for i, block in enumerate(result.blocks):
            assert block.height == resume_height + i
            BlockUtils.test_block(block, self.BINARY_BLOCK_CTX)

        # a genesis-terminated history resumes from height 0, capped by max_block_count
        result = daemon.get_blocks_by_hash([genesis_hash], 0, False, 10)
        assert 0 < len(result.blocks) <= 10
        assert result.blocks[0].height == 0

        # noop when the first hash is already the tip
        tip: MoneroBlockHeader = daemon.get_last_block_header()
        assert tip.hash is not None
        result = daemon.get_blocks_by_hash([tip.hash, genesis_hash], 0, False, 0)
        assert len(result.blocks) == 0

    # Can get a block by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_by_height(self, daemon: MoneroDaemonRpc) -> None:
        # config for testing blocks
        ctx: TestContext = TestContext()
        ctx.has_hex = True
        ctx.header_is_full = True
        ctx.has_txs = False

        # retrieve by height of last block
        last_header: MoneroBlockHeader = daemon.get_last_block_header()
        assert last_header.height is not None
        block: MoneroBlock = daemon.get_block_by_height(last_header.height)
        assert block.height is not None
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(daemon.get_block_by_height(block.height), block)

        # retrieve by height of previous to last block
        block = daemon.get_block_by_height(last_header.height - 1)
        BlockUtils.test_block(block, ctx)
        assert last_header.height - 1 == block.height

    # Can get blocks by height which includes transactions (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_height_binary(self, daemon: MoneroDaemonRpc) -> None:
        # set number of blocks to test
        num_blocks: int = 100

        # select random heights # TODO: this is horribly inefficient way of computing last 100 blocks if not shuffling
        current_height: int = daemon.get_height()
        all_heights: list[int] = list(range(current_height - 1))
        start_height: int = len(all_heights) - num_blocks
        heights: list[int] = list(range(start_height, len(all_heights)))

        # fetch blocks
        blocks: list[MoneroBlock] = daemon.get_blocks_by_height(heights)

        # test blocks
        tx_found: bool = False
        assert num_blocks == len(blocks)

        for i, height in enumerate(heights):
            block: MoneroBlock = blocks[i]
            if len(block.txs) > 0:
                tx_found = True

            BlockUtils.test_block(block, self.BINARY_BLOCK_CTX)
            assert block.height == height

        assert tx_found, "No transactions found to test"

    # Can get blocks by range in a single request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_range(self, daemon: MoneroDaemonRpc) -> None:
        # get height range
        num_blocks: int = 100
        num_blocks_ago: int = 102
        assert num_blocks > 0
        assert num_blocks_ago >= num_blocks
        height: int = daemon.get_height()
        assert height - num_blocks_ago + num_blocks - 1 < height
        start_height: int = height - num_blocks_ago
        end_height: int = height - num_blocks_ago + num_blocks - 1

        # test known start and end heights
        BlockUtils.test_get_blocks_range(daemon, start_height, end_height, height, False, self.BINARY_BLOCK_CTX)

        # test unspecified start
        BlockUtils.test_get_blocks_range(daemon, None, num_blocks - 1, height, False, self.BINARY_BLOCK_CTX)

        # test unspecified end
        BlockUtils.test_get_blocks_range(daemon, height - num_blocks - 1, None, height, False, self.BINARY_BLOCK_CTX)

    # Test invalid blocks range
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_range_invalid(self, daemon: MoneroDaemonRpc) -> None:
        height: int = daemon.get_height()
        blocks: list[MoneroBlock] = daemon.get_blocks_by_range_chunked(height, height - 10)
        num_blocks: int = len(blocks)
        assert num_blocks == 0, f"Expected empty blocks for invalid range request, got {num_blocks}"

    # Can get blocks by range using chunked requests
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_range_chunked(self, daemon: MoneroDaemonRpc) -> None:
        # get long height range
        num_blocks: int = min(daemon.get_height() - 2, 1440) # test up to ~2 days of blocks
        assert num_blocks > 0
        height: int = daemon.get_height()
        assert height - num_blocks - 1 < height
        start_height: int = height - num_blocks
        end_height: int = height - 1

        # test known start and end heights
        BlockUtils.test_get_blocks_range(daemon, start_height, end_height, height, True, self.BINARY_BLOCK_CTX)

        # test unspecified start
        BlockUtils.test_get_blocks_range(daemon, None, num_blocks - 1, height, True, self.BINARY_BLOCK_CTX)

        # test unspecified end
        BlockUtils.test_get_blocks_range(daemon, end_height - num_blocks - 1, None, height, True, self.BINARY_BLOCK_CTX)

    # Can get genesis block by range using chunked requests
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_genesis_block_by_range_chunked(self, daemon: MoneroDaemonRpc) -> None:
        # get current chain height
        chain_height: int = daemon.get_height()

        # test genesis
        BlockUtils.test_get_blocks_range(daemon, 0, 0, chain_height, True, self.BINARY_BLOCK_CTX)

    # Can get block hashes (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_hashes_binary(self, daemon: MoneroDaemonRpc) -> None:
        chain_height: int = daemon.get_height()
        genesis_hash: str = daemon.get_block_hash(0)

        # a genesis-terminated history returns the whole chain from height 0
        result: MoneroGetBlockHashesResult = daemon.get_block_hashes([genesis_hash])
        assert result.start_height == 0
        assert result.current_height is not None and result.current_height >= chain_height
        assert len(result.hashes) > 0
        assert result.hashes[0] == genesis_hash
        for hash_str in result.hashes:
            assert len(hash_str) == 64

        # only the tip comes back when it is already the first hash
        tip: MoneroBlockHeader = daemon.get_last_block_header()
        assert tip.hash is not None
        result = daemon.get_block_hashes([tip.hash, genesis_hash])
        assert result.hashes == [tip.hash]

    # Can get the miner tx sum
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_miner_tx_sum(self, daemon: MoneroDaemonRpc) -> None:
        tx_sum: MoneroMinerTxSum = daemon.get_miner_tx_sum(0, min(5000, daemon.get_height()))
        DaemonUtils.test_miner_tx_sum(tx_sum)

    # Can get alternative chains
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_alternative_chains(self, daemon: MoneroDaemonRpc) -> None:
        alt_chains: list[MoneroAltChain] = daemon.get_alt_chains()
        if len(alt_chains) == 0:
            logger.warning("No alternative chain found!")

        for alt_chain in alt_chains:
            BlockUtils.test_alt_chain(alt_chain)

    # Can get alternative block hashes
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_alternative_block_ids(self, daemon: MoneroDaemonRpc) -> None:
        alt_block_ids: list[str] = daemon.get_alt_block_hashes()
        if len(alt_block_ids) == 0:
            logger.warning("No alternative block ids found!")

        for alt_block_id in alt_block_ids:
            logger.debug(f"Testing alternarive block id: {alt_block_id}")
            assert alt_block_id is not None
            # TODO: common validation
            assert 64, len(alt_block_id)

    # Can pop blocks from the top of the chain
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(Utils.REGTEST is False, reason="REGTEST disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5, only_rerun=[])
    def test_pop_blocks(self, daemon: MoneroDaemonRpc) -> None:
        # stop mining so it doesn't race the pop, then restore the shared chain afterwards
        MiningUtils.try_stop_mining(daemon)
        height: int = daemon.get_height()

        assert daemon.pop_blocks(1) == height - 1
        MiningUtils.generate_blocks(Utils.MINING_ADDRESS, 1, daemon)
        assert daemon.get_height() == height

        with pytest.raises(Exception) as exc_info:
            daemon.pop_blocks(0)
        assert str(exc_info.value) == "Must provide a number of blocks to pop greater than 0"
