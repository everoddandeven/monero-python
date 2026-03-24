import logging

from typing import Optional
from monero import MoneroDaemonRpc
from .test_utils import TestUtils as Utils

logger: logging.Logger = logging.getLogger("MiningUtils")


class MiningUtils:
    """Mining test utilities."""

    _DAEMON: Optional[MoneroDaemonRpc] = None
    """Internal mining daemon."""

    @classmethod
    def get_daemon(cls) -> MoneroDaemonRpc:
        """
        Get internal mining daemon.

        :returns MoneroDaemonRpc: daemon rpc used for internal mining.
        """
        if cls._DAEMON is None:
            cls._DAEMON = MoneroDaemonRpc("127.0.0.1:18089", Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)

        return cls._DAEMON

    @classmethod
    def is_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Check if mining is enabled.

        :returns bool: `True` if mining is enabled, `False` otherwise.
        """
        # max tries 3
        daemon = cls.get_daemon() if d is None else d
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

        :param MoneroDaemonRpc | None d: daemon to start mining with (default internal daemon).
        """
        if cls.is_mining():
            raise Exception("Mining already started")

        daemon = cls.get_daemon() if d is None else d
        daemon.start_mining(Utils.MINING_ADDRESS, 1, False, False)

    @classmethod
    def stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> None:
        """
        Stop internal mining.

        :param MoneroDaemonRpc | None d: daemon to stop mining with (default internal daemon).
        """
        if not cls.is_mining():
            raise Exception("Mining already stopped")

        daemon = cls.get_daemon() if d is None else d
        daemon.stop_mining()

    @classmethod
    def try_stop_mining(cls, d: Optional[MoneroDaemonRpc] = None) -> bool:
        """
        Try stop internal mining.

        :param MoneroDaemonRpc | None d: daemon to stop mining with (default internal daemon).
        :returns bool: `True` if mining stopped, `False` otherwise.
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

        :param MoneroDaemonRpc | None d: daemon to start mining with (default internal daemon).
        :returns bool: `True` if mining started, `False` otherwise.
        """
        try:
            cls.start_mining(d)
            return True
        except Exception as e:
            logger.warning(f"MiningUtils.start_mining(): {e}")
            return False
