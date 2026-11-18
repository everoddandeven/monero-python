from enum import IntEnum


class MoneroTxPriority(IntEnum):
    """Enumerates Monero transaction priorities."""
    DEFAULT = 0
    """`0` Default transaction priority."""
    UNIMPORTANT = 1
    """`1` Unimportant transaction priority."""
    NORMAL = 2
    """`2` Normal transaction priority."""
    ELEVATED = 3
    """`3` Elevated transaction priority."""
