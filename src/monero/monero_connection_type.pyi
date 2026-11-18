from enum import IntEnum


class MoneroConnectionType(IntEnum):
    """Enumerates a connection type, wich can be `IPV4`, `IPV6`, `TOR`, `I2P` or `INVALID`."""

    INVALID = 0
    """`0` Indicates that Monero connection type is invalid."""

    IPV4 = 1
    """`1` Indicates that Monero connection type is IPV4."""

    IPV6 = 2
    """`2` Indicates that Monero connection type is IPV6."""

    TOR = 3
    """`3` Indicates that Monero connection type is TOR."""

    I2P = 4
    """`4` Indicates that Monero connection type is I2P."""
