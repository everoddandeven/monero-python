class MoneroSslOptions:
    ssl_private_key_path: str
    """Path to private ssl key"""
    ssl_certificate_path: str
    """Path to private ssl certificate"""
    ssl_ca_file: str
    """Path to ssl CA file"""
    ssl_allowed_fingerprints: list[str]
    """Allowed ssl fingerprints"""
    ssl_allow_any_cert: bool | None
    """Allow any certificate"""
