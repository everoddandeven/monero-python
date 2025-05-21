from enum import IntEnum


class MoneroAddressType(IntEnum):
    """
    Members:
    
      PRIMARY_ADDRESS
    
      INTEGRATED_ADDRESS
    
      SUBADDRESS
    """
    INTEGRATED_ADDRESS = 1
    """`1` Indicates that the Monero address format is `integrated`."""
    PRIMARY_ADDRESS = 0
    """`0` Indicates that the Monero address format is `standard`, also known as `primary`"""
    SUBADDRESS = 2
    """`2` Indicates that the Monero address format is `subaddress`."""

