import logging
from typing import Optional, override

from monero import MoneroWallet

from .wallet_sync_printer import WalletSyncPrinter

logger: logging.Logger = logging.getLogger("SyncProgressTester")


class SyncProgressTester(WalletSyncPrinter):
    """Wallet sync progress tester."""

    wallet: MoneroWallet
    """Test wallet instance."""
    start_height: int
    """Blockchain start height."""
    prev_end_height: int
    """Previous blockchain end height."""
    prev_height: Optional[int]
    """Previous notified blockchain height."""
    prev_complete_height: Optional[int]
    """End height of the last completed sync session."""
    session_start: bool
    """`True` while the next notification is the first of a sync session."""
    is_done: bool
    """Indicates if wallet sync is completed."""
    on_sync_progress_after_done: Optional[bool]
    """Indicates that `on_sync_progress` has been called after `on_done`."""

    @property
    def is_notified(self) -> bool:
        """Check if listener was notified.

        :returns bool: `True` if listener got notified by sync progress.
        """
        return self.prev_height is not None

    def __init__(self, wallet: MoneroWallet, start_height: int, end_height: int) -> None:
        """Initialize a new wallet sync progress tester.

        :param MoneroWallet wallet: wallet to test.
        :param int start_height: wallet start height.
        :param int end_height: wallet end height.
        """
        super(SyncProgressTester, self).__init__()
        self.wallet = wallet
        assert start_height >= 0, f"Invalid start height provided: {start_height}"
        assert end_height >= 0, f"Invalid end height provided: {end_height}"
        self.start_height = start_height
        self.prev_end_height = end_height
        self.session_start = True
        self.is_done = False

        self.prev_height = None
        self.prev_complete_height = None
        self.on_sync_progress_after_done = None

    @override
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        """Invoked on wallet sync progress.

        :param int height: current blockchain height.
        :param int start_height: sync start height.
        :param int end_height: sync end height.
        :param float percent_done: sync percentage progress.
        :param str message: sync progress message.
        """
        super().on_sync_progress(height, start_height, end_height, percent_done, message)

        # registered wallet listeners will continue to get sync notifications after the wallet's initial sync
        if self.is_done:
            assert self in self.wallet.get_listeners(), "Listener has completed and is not registered so should not be called again"
            self.on_sync_progress_after_done = True

        # update tester's start height if new sync session
        if self.session_start and self.prev_complete_height is not None and start_height >= self.prev_complete_height:
            self.start_height = start_height

        # progress notifications are throttled, so heights may skip, and the start height may rebase
        # down to report progress while the wallet skips hashes below the sync start
        assert end_height > start_height, "end height > start height"
        assert start_height <= self.start_height, "start height only rebases down"
        self.start_height = start_height
        assert end_height >= self.prev_end_height, "chain can only grow while syncing"
        self.prev_end_height = end_height
        if self.prev_height is not None:
            assert height >= self.prev_height, "heights advance monotonically"
        self.prev_height = height

        if height < start_height:
            assert self.session_start, "hash-skip notification only at the start of a sync session"
            assert percent_done == 0.0 # initial notification while the wallet skips ahead to the sync start
        else:
            assert height < end_height
            expected_percent_done: float = (height - start_height + 1) / (end_height - start_height)
            assert expected_percent_done == percent_done
            if percent_done == 1.0:
                self.prev_complete_height = end_height # record completion height for subsequent sync sessions

        # completion starts a new session
        self.session_start = percent_done == 1.0

    def on_done(self, chain_height: int) -> None:
        """Called once on sync progress done.

        :param int chain_height: blockchain height reached.
        """
        assert self.is_done is False
        self.is_done = True
        if self.prev_height is None:
            logger.info("Wallet already synced")
            assert self.prev_complete_height is None
            assert chain_height == self.start_height, f"{chain_height} != {self.start_height}"
        else:
            # otherwise the last progress notification reports the final block
            assert chain_height - 1 == self.prev_height
            assert chain_height == self.prev_complete_height
