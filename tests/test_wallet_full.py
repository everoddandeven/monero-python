import pytest
from monero import WalletFull, WalletConfig, NetworkType
import os


def test_wallet_creation_and_sync():
    config = WalletConfig()
    config.path = "test_wallet_sync"  # will be created on disk
    config.password = "password"
    config.network_type = NetworkType.STAGENET
    config.restore_height = 0
    config.seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    wallet = WalletFull.create_wallet(config)
    assert wallet.is_view_only() is False
    
    wallet.sync()
    balance = wallet.get_balance()
    assert isinstance(balance, int)

    wallet.close(save=False)

    # Cleanup if wallet file is written
    for ext in ["", ".keys", ".address.txt"]:
        try:
            os.remove(f"test_wallet_sync{ext}")
        except FileNotFoundError:
            pass

def test_wallet_open_and_close():
    config = WalletConfig()
    config.path = "test_wallet_open"
    config.password = "testpass"
    config.network_type = NetworkType.STAGENET
    config.seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    # First create wallet
    wallet = WalletFull.create_wallet(config)
    wallet.close()

    # Then reopen
    wallet2 = WalletFull.open_wallet(config.path, config.password, config.network_type)
    assert wallet2.is_view_only() is False
    wallet2.close()

    # Cleanup
    for ext in ["", ".keys", ".address.txt"]:
        try:
            os.remove(f"test_wallet_open{ext}")
        except FileNotFoundError:
            pass
