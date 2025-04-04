import pytest
from monero import WalletKeys, WalletConfig, NetworkType

def test_create_wallet_random():
    config = WalletConfig()
    config.language = "English"
    config.network_type = NetworkType.TESTNET
    wallet = WalletKeys.create_wallet_random(config)

    assert wallet.get_seed() is not None
    assert isinstance(wallet.get_seed(), str)
    assert len(wallet.get_seed().split()) >= 12

def test_create_wallet_from_seed():
    config = WalletConfig()
    config.network_type = NetworkType.TESTNET
    wallet = WalletKeys.create_wallet_random(config)
    seed = wallet.get_seed()
    config.seed = seed
    config.language = "English"  

    wallet = WalletKeys.create_wallet_from_seed(config)
    assert wallet.get_seed() == seed

def test_get_keys():
    config = WalletConfig()
    config.language = "English"
    config.network_type = NetworkType.TESTNET
    wallet = WalletKeys.create_wallet_random(config)

    assert wallet.get_private_view_key() is not None
    assert wallet.get_private_spend_key() is not None
    assert isinstance(wallet.get_private_view_key(), str)
    assert isinstance(wallet.get_private_spend_key(), str)