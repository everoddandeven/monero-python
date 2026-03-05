from enum import IntEnum


class WalletType(IntEnum):
    """Monero wallet type enum"""
    KEYS = 0
    """Keys only wallet"""
    RPC = 1
    """RPC wallet"""
    FULL = 2
    """Full local wallet"""
    UNDEFINED = 255
    """Invalid wallet type"""
