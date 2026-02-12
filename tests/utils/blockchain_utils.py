import logging

from abc import ABC
from time import sleep
from monero import MoneroNetworkType

from .string_utils import StringUtils
from .test_utils import TestUtils as Utils
from .mining_utils import MiningUtils
from .tx_spammer import TxSpammer
from .string_utils import StringUtils


logger: logging.Logger = logging.getLogger("BlockchainUtils")


class BlockchainUtils(ABC):
    """Blockchain utilities"""

    @classmethod
    def get_height(cls) -> int:
        return MiningUtils.get_daemon().get_height()

    @classmethod
    def has_reached_height(cls, height: int) -> bool:
        """Check if blockchain has reached height"""
        return height <= cls.get_height()

    @classmethod
    def blockchain_is_ready(cls) -> bool:
        """Indicates if blockchain has reached minimum height for running tests"""
        return cls.has_reached_height(Utils.MIN_BLOCK_HEIGHT)

    @classmethod
    def wait_for_height(cls, height: int) -> int:
        """
        Wait for blockchain height.
        """
        daemon = MiningUtils.get_daemon()
        current_height = daemon.get_height()
        if height <= current_height:
            return current_height

        stop_mining: bool = False
        if not MiningUtils.is_mining():
            MiningUtils.start_mining()
            stop_mining = True

        while current_height < height:
            p = StringUtils.get_percentage(current_height, height)
            logger.info(f"[{p}] Waiting for blockchain height ({current_height}/{height})")
            block = daemon.wait_for_next_block_header()
            assert block.height is not None
            current_height = block.height
            sleep(5)

        if stop_mining:
            MiningUtils.stop_mining()
            sleep(5)
            current_height = daemon.get_height()

        logger.info(f"[100%] Reached blockchain height: {current_height}")

        return current_height

    @classmethod
    def wait_until_blockchain_ready(cls) -> int:
        """
        Wait until blockchain is ready.
        """
        height = cls.wait_for_height(Utils.MIN_BLOCK_HEIGHT)
        MiningUtils.try_stop_mining()
        return height

    @classmethod
    def wait_for_blocks(cls, num_blocks: int) -> None:
        if num_blocks <= 0:
            return
        height = cls.get_height()
        cls.wait_for_height(height + num_blocks)

    @classmethod
    def setup_blockchain(cls, network_type: MoneroNetworkType) -> None:
        """Setup blockchain for integration tests"""
        if cls.blockchain_is_ready():
            logger.debug("Already setup blockchain")
            return

        cls.wait_until_blockchain_ready()
        spammer = TxSpammer(network_type)
        spammer.spam()
        cls.wait_for_blocks(11)
