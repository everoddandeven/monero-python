from enum import IntEnum


class MoneroMessageSignatureType(IntEnum):
    """
    Members:
    
      SIGN_WITH_SPEND_KEY
    
      SIGN_WITH_VIEW_KEY
    """
    SIGN_WITH_SPEND_KEY = 0
    """`0` Indicates that the message verification was signed with the wallet `spend key`"""
    SIGN_WITH_VIEW_KEY = 1
    """`1` Indicates that the message verification was signed with the wallet `view key`"""
