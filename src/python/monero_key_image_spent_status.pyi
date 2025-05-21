from enum import IntEnum


class MoneroKeyImageSpentStatus(IntEnum):
    """
    Members:
    
      NOT_SPENT
    
      CONFIRMED
    
      TX_POOL
    """
    CONFIRMED = 1
    """`1`Indicates that the key image is spent."""
    NOT_SPENT = 0
    """`0`Indicates that the key image is not spent."""
    TX_POOL = 2
    """`2`Indicates that the key image is in transaction pool."""
