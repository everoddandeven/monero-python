import logging

from abc import ABC
from time import sleep
from monero import MoneroNetworkType, MoneroGenerateBlocksResult

from .string_utils import StringUtils
from .test_utils import TestUtils as Utils
from .mining_utils import MiningUtils
from .tx_spammer import TxSpammer

logger: logging.Logger = logging.getLogger("BlockchainUtils")


# Blockchain utilities to be used in integration tests
class BlockchainUtils(ABC):
    """Blockchain utilities."""

    CHECK_BLOCK_TIMEOUT_SECONDS: int = 5
    """Timeout in seconds to check blockchain mining progress."""

    @classmethod
    def get_height(cls) -> int:
        """Get current blockchain height.

        :returns int: current blockchain height.
        """
        return MiningUtils.get_daemon().get_height()

    @classmethod
    def has_reached_height(cls, height: int) -> bool:
        """Check if blockchain has reached height.

        :param int height: blockchain height to check.
        :returns bool: `True` if blockchain has reached `height`.
        """
        return height <= cls.get_height()

    @classmethod
    def blockchain_is_ready(cls) -> bool:
        """Indicates if blockchain has reached minimum height for running tests.

        :returns bool: `True` if blockchain is ready, `False` otherwise.
        """
        # check if blockchain has reached minimum block height
        return cls.has_reached_height(Utils.MIN_BLOCK_HEIGHT)

    @classmethod
    def wait_for_height(cls, height: int) -> int:
        """Wait for blockchain height.

        :param int height: height to wait for.
        :returns int: blockchain height.
        """
        daemon = MiningUtils.get_daemon()
        current_height: int = daemon.get_height()
        # check if already reached height
        if height <= current_height:
            # return last height
            return current_height

        # start mining if not active
        stop_mining: bool = False
        if not MiningUtils.is_mining():
            MiningUtils.start_mining()
            stop_mining = True

        # wait until blockchain reaches desired height
        while current_height < height:
            p = StringUtils.get_percentage(current_height, height)
            logger.info(f"[{p}] Waiting for blockchain height ({current_height}/{height})")
            block = daemon.wait_for_next_block_header()
            assert block.height is not None
            current_height = block.height
            sleep(cls.CHECK_BLOCK_TIMEOUT_SECONDS)

        # stop mining, if started
        if stop_mining:
            MiningUtils.stop_mining()
            sleep(cls.CHECK_BLOCK_TIMEOUT_SECONDS)
            current_height = daemon.get_height()

        logger.info(f"[100%] Reached blockchain height: {current_height}")

        return current_height

    @classmethod
    def wait_until_blockchain_ready(cls) -> int:
        """Wait until blockchain is ready.

        :returns int: blockchain height.
        """
        # wait for minimun blockchain height
        height: int = cls.wait_for_height(Utils.MIN_BLOCK_HEIGHT)
        # stop mining
        MiningUtils.try_stop_mining()
        return height

    @classmethod
    def wait_for_blocks(cls, num_blocks: int) -> int:
        """Start mining and wait for blocks.

        :param int num_blocks: number of blocks to wait.
        :returns int: blockchain height.
        """
        # validate parameters
        assert num_blocks >= 0, f"Invalid number of blocks to wait for: {num_blocks}"
        height: int = cls.get_height()
        # wait for block height
        return cls.wait_for_height(height + num_blocks)

    @classmethod
    def setup_blockchain(cls, network_type: MoneroNetworkType) -> None:
        """Setup blockchain for integration tests.

        :param MoneroNetworkType network_type: blockchain network type to setup.
        """
        # check if blockchain is already setup
        if cls.blockchain_is_ready():
            logger.debug("Already setup blockchain")
            return

        # wait until blockchain reaches desired height
        cls.wait_until_blockchain_ready()
        # spam some transactions on blockchain
        spammer: TxSpammer = TxSpammer(network_type)
        spammer.spam()
        # wait for spammed txs to confirm
        cls.wait_for_blocks(11)

        # create an alternative chain on regtest
        if Utils.REGTEST:
            cls.reorg_blockchain()

    @classmethod
    def reorg_blockchain(cls, num_blocks: int = 3) -> int:
        """Force a blockchain reorganization and ensure it completes successfully (regtest only).

        Forks the chain at the current tip: first mines a short chain on top of it, then mines
        a longer alternate chain from the same fork point. Since the alternate chain has more
        cumulative work, the daemon must reorg onto it, replacing the blocks of the original
        chain.

        :param int num_blocks: number of blocks to mine on the original chain before forking
            (the alternate chain mines one more block than this to guarantee it wins the reorg).
        :returns int: blockchain height after the reorg.
        """
        assert num_blocks >= 1, f"Invalid number of blocks to reorg: {num_blocks}"

        daemon = MiningUtils.get_daemon()

        # mining must be stopped so it doesn't race with the forced reorg
        stop_mining: bool = MiningUtils.try_stop_mining()

        try:
            # mark the fork point: the last common block between both chains
            fork_header = daemon.get_last_block_header()
            assert fork_header.hash is not None and fork_header.height is not None
            fork_hash: str = fork_header.hash
            fork_height: int = fork_header.height

            # mine the original, shorter chain on top of the fork point
            original: MoneroGenerateBlocksResult = daemon.generate_blocks(Utils.MINING_ADDRESS, num_blocks, fork_hash)
            assert original.height == fork_height + num_blocks, \
                f"Failed to build original chain: expected height {fork_height + num_blocks}, got {original.height}"
            original_hash: str = daemon.get_block_hash(fork_height + 1)
            logger.debug(f"Built original chain of {num_blocks} block(s) on top of height {fork_height}")

            # mine a longer alternate chain from the same fork point to force a reorg
            alt_num_blocks: int = num_blocks + 1
            alt: MoneroGenerateBlocksResult = daemon.generate_blocks(Utils.MINING_ADDRESS, alt_num_blocks, fork_hash)
            assert alt.height == fork_height + alt_num_blocks, \
                f"Failed to build alternate chain: expected height {fork_height + alt_num_blocks}, got {alt.height}"
            logger.debug(f"Built alternate chain of {alt_num_blocks} block(s) on top of height {fork_height}")
        finally:
            # restart mining, if it was active before
            if stop_mining:
                MiningUtils.try_start_mining()

        # ensure the reorg was accepted: the active chain must now follow the heavier alternate fork
        active_hash: str = daemon.get_block_hash(fork_height + 1)
        assert active_hash != original_hash, \
            "Reorg failed: block after the fork point was not replaced by the alternate chain"
        assert active_hash in alt.block_hashes, \
            "Reorg failed: active chain block is not part of the generated alternate chain"

        original_header = daemon.get_block_header_by_hash(original_hash)
        assert original_header.orphan_status is True, \
            "Reorg failed: original chain block was not marked as orphaned"

        reorg_height: int = daemon.get_height()
        logger.debug(f"Blockchain reorg succeeded: active chain now at height {reorg_height}")

        return reorg_height
