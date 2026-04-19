import logging

from abc import ABC
from time import sleep
from monero import MoneroNetworkType

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
