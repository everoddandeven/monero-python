import logging

from typing_extensions import override
from monero import MoneroWalletListener

logger: logging.Logger = logging.getLogger("WalletSyncPrinter")


class WalletSyncPrinter(MoneroWalletListener):
    """Print listener for wallet sync progress"""

    next_increment: float
    """Next expected sync progress increment"""
    sync_resolution: float
    """Sync progress resolution"""

    def __init__(self, sync_resolution: float = 0.05) -> None:
        """
        Initialize a new wallet sync printer

        :param float sync_resolution: Sync progress resolution
        """
        super().__init__()
        self.next_increment = 0
        self.sync_resolution = sync_resolution

    @override
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        """
        Invoked on wallet sync progress

        :param int height: current blockchain height
        :param int start_height: sync start height
        :param int end_height: sync end height
        :param float percent_done: sync percentage progress
        :param str message: sync progress message
        """
        if percent_done == 1.0 or percent_done >= self.next_increment:
            msg = f"on_sync_progress({height}, {start_height}, {end_height}, {percent_done}, {message})"
            logger.info(msg)
            self.next_increment += self.sync_resolution
