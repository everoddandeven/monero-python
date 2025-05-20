class MoneroDaemonUpdateCheckResult:
    """
    Models the result of checking for a daemon update.
    """
    auto_uri: str | None
    hash: str | None
    is_update_available: bool | None
    """Indicates if an update is available to download."""
    user_uri: str | None
    version: str | None
    """Version available for download."""
    def __init__(self) -> None:
        ...
