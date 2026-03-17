
from typing import Optional, override

from monero import MoneroWalletFull

from .wallet_sync_printer import WalletSyncPrinter


class SyncProgressTester(WalletSyncPrinter):
    """Wallet sync progress tester."""

    wallet: MoneroWalletFull
    """Test wallet instance."""
    prev_height: Optional[int]
    """Previous blockchain height."""
    start_height: int
    """Blockchain start height."""
    prev_end_height: int
    """Previous blockchain end height."""
    prev_complete_height: Optional[int]
    """Previous blockchain completed height."""
    is_done: bool
    """Indicates if wallet sync is completed."""
    on_sync_progress_after_done: Optional[bool]
    """Indicates that `on_sync_progress` has been called after `on_done`."""

    @property
    def is_notified(self) -> bool:
        """
        Check if listener was notified.

        :returns bool: `True` if listener got notified by sync progress.
        """
        return self.prev_height is not None

    def __init__(self, wallet: MoneroWalletFull, start_height: int, end_height: int) -> None:
        """
        Initialize a new wallet sync progress tester.

        :param MoneroWalletFull wallet: wallet to test.
        :param int start_height: wallet start height.
        :param int end_height: wallet end height.
        """
        super(SyncProgressTester, self).__init__()
        self.wallet = wallet
        assert start_height >= 0, f"Invalid start height provided: {start_height}"
        assert end_height >= 0, f"Invalid end height provided: {end_height}"
        self.start_height = start_height
        self.prev_end_height = end_height
        self.is_done = False

        self.prev_height = None
        self.prev_complete_height = None
        self.on_sync_progress_after_done = None

    @override
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        super().on_sync_progress(height, start_height, end_height, percent_done, message)

        # registered wallet listeners will continue to get sync notifications after the wallet's initial sync
        if self.is_done:
            assert self in self.wallet.get_listeners(), "Listener has completed and is not registered so should not be called again"
            self.on_sync_progress_after_done = True

        # update tester's start height if new sync session
        if self.prev_complete_height is not None and start_height == self.prev_complete_height:
            self.start_height = start_height

        # if sync is complete, record completion height for subsequent start heights
        if int(percent_done) == 1:
            self.prev_complete_height = end_height
        elif self.prev_complete_height is not None:
            # otherwise start height is equal to previous completion height
            assert self.prev_complete_height == start_height

        assert end_height > start_height, "end height > start height"
        assert self.start_height == start_height
        assert end_height >= start_height
        assert height < end_height

        expected_percent_done: float = (height - start_height + 1) / (end_height - start_height)
        assert expected_percent_done == percent_done
        if self.prev_height is None:
            assert start_height == height
        else:
            assert height == self.prev_height + 1

        self.prev_height = height

    def on_done(self, chain_height: int) -> None:
        """
        Called once on sync progress done.

        :param int chain_height: blockchain height reached.
        """
        assert self.is_done is False
        self.is_done = True
        if self.prev_height is None:
            assert self.prev_complete_height is None
            assert chain_height == self.start_height
        else:
            # otherwise last height is chain height - 1
            assert chain_height - 1 == self.prev_height
            assert chain_height == self.prev_complete_height

