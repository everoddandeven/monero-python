from enum import IntEnum


class MoneroConnectionPollType(IntEnum):
    """
    Members:
    
      PRIORITIZED
    
      CURRENT
    
      ALL
    
      UNDEFINED
    """
    ALL = 2
    """`2` Poll all connections."""
    CURRENT = 1
    """`1` Poll only current connection."""
    PRIORITIZED = 0
    """`0` Poll only prioritized connections."""
    UNDEFINED = 3
    """`3` Invalid poll type."""

