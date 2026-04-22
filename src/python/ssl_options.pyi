from .serializable_struct import SerializableStruct


class SslOptions(SerializableStruct):
    """Models SSL options for a Monero rpc connection."""

    ssl_private_key_path: str | None
    """Path to private ssl key."""
    ssl_certificate_path: str | None
    """Path to private ssl certificate."""
    ssl_ca_file: str | None
    """Path to ssl CA file."""
    ssl_allowed_fingerprints: list[str]
    """Allowed ssl fingerprints."""
    ssl_allow_any_cert: bool | None
    """Allow any certificate."""

    def __init__(self) -> None:
        """Initialize a new rpc connection ssl options."""
        ...
