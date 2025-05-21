from enum import IntEnum


class MoneroNetworkType(IntEnum):
    """
    Members:
    
      MAINNET
    
      TESTNET
    
      STAGENET
    """
    MAINNET = 0
    """`0` Mainnet."""
    STAGENET = 2
    """`2` Stagenet."""
    TESTNET = 1
    """`1` Testnet."""
