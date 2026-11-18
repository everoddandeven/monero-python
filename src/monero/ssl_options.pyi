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

    @staticmethod
    def deserialize(json: str) -> SslOptions:
        """
        Deserialize an SslOptions from a JSON string.

        :param str json: SslOptions in JSON format.
        :returns SslOptions: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a new rpc connection ssl options."""
        ...
