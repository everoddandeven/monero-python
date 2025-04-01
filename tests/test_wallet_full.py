import pytest
from monero import WalletFull, WalletKeys, WalletConfig, NetworkType
import os

def test_wallet_creation_and_close():

    config_keys = WalletConfig()
    config_keys.language = "English"
    config_keys.network_type = NetworkType.TESTNET
    keys_wallet = WalletKeys.create_wallet_random(config_keys)
    seed = keys_wallet.get_seed()

    config = WalletConfig()
    config.path = "test_wallet_sync"
    config.password = "password"
    config.network_type = NetworkType.TESTNET
    config.restore_height = 0
    config.seed = seed
    config.language = "English"

    wallet = WalletFull.create_wallet(config)
    assert wallet.is_view_only() is False
    wallet.close(save=False)

    for ext in ["", ".keys", ".address.txt"]:
        try:
            os.remove(f"test_wallet_sync{ext}")
        except FileNotFoundError:
            pass
