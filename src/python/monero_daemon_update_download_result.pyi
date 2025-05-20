from .monero_daemon_update_check_result import MoneroDaemonUpdateCheckResult


class MoneroDaemonUpdateDownloadResult(MoneroDaemonUpdateCheckResult):
    """
    Models the result of downloading an update.
    """
    download_path: str | None
    """Path to download the update."""
    def __init__(self) -> None:
        ...
