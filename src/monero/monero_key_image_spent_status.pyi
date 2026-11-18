from enum import IntEnum


class MoneroKeyImageSpentStatus(IntEnum):
    """Enumerates the spent status of a key image."""

    NOT_SPENT = 0
    """`0` Indicates that the key image is not spent."""

    CONFIRMED = 1
    """`1` Indicates that the key image is spent."""

    TX_POOL = 2
    """`2` Indicates that the key image is in transaction pool."""
