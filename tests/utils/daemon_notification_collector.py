import logging

from typing import override

from monero import MoneroDaemonRpc, MoneroDaemonListener, MoneroBlockHeader

logger: logging.Logger = logging.getLogger("DaemonNotificationCollector")


class DaemonNotificationCollector(MoneroDaemonListener):
    """Collects block headers from daemon."""

    daemon: MoneroDaemonRpc
    """Daemon instance."""
    listening: bool
    """Indicates if listener is expected to be active."""
    block_headers: set[MoneroBlockHeader]
    """Collection of block headers seen by the daemon."""
    block_hashes: set[str]
    """Collection of block hashes seen by the daemon."""
    last_block_height: int | None
    """Last block height collected by the listener."""
    auto_remove: bool
    "Specifies if listener should self remove after block notification."
    errors: list[Exception]
    """Errors while collecting notifications."""

    @property
    def num_block_headers(self) -> int:
        return len(self.block_headers)

    @property
    def num_block_hashes(self) -> int:
        return len(self.block_hashes)

    def __init__(self, daemon: MoneroDaemonRpc, auto_remove: bool = False) -> None:
        """Initialize a new wallet notification collector."""
        super().__init__()
        self.listening = True
        self.daemon = daemon
        self.auto_remove = auto_remove
        self.block_headers = set()
        self.block_hashes = set()
        self.last_block_height = None
        self.errors = []

    @override
    def on_block_header(self, header: MoneroBlockHeader) -> None:
        try:
            logger.debug(f"Collecting block header: {header.serialize()}")
            assert header.hash is not None
            assert header.hash not in self.block_hashes, f"Duplicate block header found: {header.hash}"
            self.block_hashes.add(header.hash)
            self.block_headers.add(header)

            assert header.height is not None
            if self.last_block_height is not None and header.height != self.last_block_height + 1:
                logger.warning(f"Daemon listener missed blocks range {self.last_block_height + 1}-{header.height - 1}")

            self.last_block_height = header.height

            if self.auto_remove:
                logger.debug("Self-removing daemon listener...")
                self.daemon.remove_listener(self)
                logger.debug("Daemon listener self-removed successfully")
        except Exception as e:
            logger.error(f"{e}")
            self.errors.append(e)
