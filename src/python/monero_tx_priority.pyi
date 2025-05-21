from enum import IntEnum


class MoneroTxPriority(IntEnum):
    """
    Members:
    
      DEFAULT
    
      UNIMPORTANT
    
      NORMAL
    
      ELEVATED
    """
    DEFAULT = 0
    """`0` Default transaction priority."""
    ELEVATED = 3
    """`3` Elevated transaction priority."""
    NORMAL = 2
    """`2` Normal transaction priority."""
    UNIMPORTANT = 1
    """`1` Unimportant transaction priority."""
