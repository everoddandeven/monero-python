from .monero_daemon_update_check_result import MoneroDaemonUpdateCheckResult


class MoneroDaemonUpdateDownloadResult(MoneroDaemonUpdateCheckResult):
    """Models the result of downloading a daemon update."""

    download_path: str | None
    """Path to download the update."""

    @staticmethod
    def deserialize(json: str) -> MoneroDaemonUpdateDownloadResult:
        """
        Deserialize a MoneroDaemonUpdateDownloadResult from a JSON string.

        :param str json: MoneroDaemonUpdateDownloadResult in JSON format.
        :returns MoneroDaemonUpdateDownloadResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero update download result."""
        ...
