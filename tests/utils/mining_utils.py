import logging

from typing import Optional
from time import sleep
from monero import MoneroDaemonRpc
from .const import MINING_ADDRESS

logger: logging.Logger = logging.getLogger(__name__)


class MiningUtils:
    """
    Mining utilities.
    """
    _DAEMON: Optional[MoneroDaemonRpc] = None
    """Internal mining daemon."""

    @classmethod
    def _get_daemon(cls) -> MoneroDaemonRpc:
        """
        Get internal mining daemon.
        """
        if cls._DAEMON is None:
            cls._DAEMON = MoneroDaemonRpc("127.0.0.1:18089")

        return cls._DAEMON

    @classmethod
    def is_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Check if mining is enabled.
        """
        # max tries 3
        daemon = cls._get_daemon() if d is None else d
        for i in range(3):
            try:
                status = daemon.get_mining_status()
                return status.is_active is True

            except Exception as e:
                if i == 2:
                    raise e

        return False

    @classmethod
    def start_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> None:
        """
        Start internal mining.
        """
        if cls.is_mining():
            raise Exception("Mining already started")

        daemon = cls._get_daemon() if d is None else d
        daemon.start_mining(MINING_ADDRESS, 1, False, False)

    @classmethod
    def stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> None:
        """
        Stop internal mining.
        """
        if not cls.is_mining():
            raise Exception("Mining already stopped")

        daemon = cls._get_daemon() if d is None else d
        daemon.stop_mining()

    @classmethod
    def try_stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Try stop internal mining.
        """
        try:
            cls.stop_mining(d)
            return True
        except Exception as e:
            logger.warning(f"MiningUtils.stop_mining(): {e}")
            return False

    @classmethod
    def try_start_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Try start internal mining.
        """
        try:
            cls.start_mining(d)
            return True
        except Exception as e:
            logger.warning(f"MiningUtils.start_mining(): {e}")
            return False

    @classmethod
    def wait_for_height(cls, height: int) -> int:
        """
        Wait for blockchain height.
        """
        daemon = cls._get_daemon()
        current_height = daemon.get_height()
        if height <= current_height:
            return current_height

        stop_mining: bool = False
        if not cls.is_mining():
            cls.start_mining()
            stop_mining = True

        while current_height < height:
            logger.info(f"Waiting for blockchain height ({current_height}/{height})")
            block = daemon.wait_for_next_block_header()
            assert block.height is not None
            current_height = block.height
            sleep(3)

        if stop_mining:
            cls.stop_mining()
            sleep(3)
            current_height = daemon.get_height()

        logger.info(f"Blockchain height: {current_height}")

        return current_height
