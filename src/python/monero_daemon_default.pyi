from .monero_daemon import MoneroDaemon


class MoneroDaemonDefault(MoneroDaemon):
    """
    Base Monero daemon with default implementations.
    """
    def __init__(self) -> None:
        """Initialize a Monero daemon with default implementations."""
        ...
