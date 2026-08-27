import logging

from monero import MoneroDaemonRpc, MoneroGenerateBlocksResult, MoneroMiningStatus

from .test_utils import TestUtils as Utils

logger: logging.Logger = logging.getLogger("MiningUtils")


class MiningUtils:
    """Mining test utilities."""

    _DAEMON: MoneroDaemonRpc | None = None
    """Internal mining daemon."""

    @classmethod
    def get_daemon(cls) -> MoneroDaemonRpc:
        """Get internal mining daemon.

        :returns MoneroDaemonRpc: daemon rpc used for internal mining.
        """
        return Utils.get_mining_daemon()

    @classmethod
    def generate_blocks(cls, address: str, num_blocks: int, d: MoneroDaemonRpc | None = None) -> MoneroGenerateBlocksResult:
        """Generate blocks to a wallet address (regtest only).

        :param str address: is the address of the wallet to receive miner transactions if block is successfully mined.
        :param int num_blocks: is the number of blocks to generate.
        :param MoneroDaemonRpc | None d: daemon to generate blocks with (default internal daemon).
        :returns MoneroGenerateBlocksResult: the result of generating blocks; height is the height of the last block generated.
        """
        assert Utils.REGTEST, "Generating blocks is supported only on regtest."
        daemon: MoneroDaemonRpc = cls.get_daemon() if d is None else d
        return daemon.generate_blocks(address, num_blocks)

    @classmethod
    def is_mining(cls, d: MoneroDaemonRpc | None = None) -> bool:
        """Check if mining is enabled.

        :param MoneroDaemonRpc | None d: rpc daemon to check (default internal daemon).
        :returns bool: `True` if mining is enabled, `False` otherwise.
        """
        # max tries 3
        daemon: MoneroDaemonRpc = cls.get_daemon() if d is None else d
        for i in range(3):
            try:
                status: MoneroMiningStatus = daemon.get_mining_status()
                return status.is_active is True

            except Exception:
                if i == 2:
                    raise

        return False

    @classmethod
    def start_mining(cls, d: MoneroDaemonRpc | None = None) -> None:
        """Start mining.

        :param MoneroDaemonRpc | None d: daemon to start mining with (default internal daemon).
        """
        if cls.is_mining():
            raise Exception("Mining already started")

        daemon: MoneroDaemonRpc = cls.get_daemon() if d is None else d
        daemon.start_mining(Utils.MINING_ADDRESS, 1, False, False)

    @classmethod
    def stop_mining(cls, d: MoneroDaemonRpc | None = None) -> None:
        """
        Stop mining.

        :param MoneroDaemonRpc | None d: daemon to stop mining with (default internal daemon).
        """
        if not cls.is_mining():
            raise Exception("Mining already stopped")

        daemon: MoneroDaemonRpc = cls.get_daemon() if d is None else d
        daemon.stop_mining()

    @classmethod
    def try_stop_mining(cls, d: MoneroDaemonRpc | None = None) -> bool:
        """
        Try stop mining.

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
    def try_start_mining(cls, d: MoneroDaemonRpc | None = None) -> bool:
        """
        Try start mining.

        :param MoneroDaemonRpc | None d: daemon to start mining with (default internal daemon).
        :returns bool: `True` if mining started, `False` otherwise.
        """
        try:
            cls.start_mining(d)
            return True
        except Exception as e:
            logger.warning(f"MiningUtils.start_mining(): {e}")
            return False
