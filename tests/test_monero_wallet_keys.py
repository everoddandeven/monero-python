from monero import MoneroWalletKeys, MoneroWalletConfig, MoneroNetworkType

def test_create_wallet_random():
  config = MoneroWalletConfig()
  config.language = "English"
  config.network_type = MoneroNetworkType.TESTNET
  wallet = MoneroWalletKeys.create_wallet_random(config)

  assert wallet.get_seed() is not None
  assert isinstance(wallet.get_seed(), str)
  assert len(wallet.get_seed().split()) >= 12

def test_create_wallet_from_seed():
  config = MoneroWalletConfig()
  config.network_type = MoneroNetworkType.TESTNET
  wallet = MoneroWalletKeys.create_wallet_random(config)
  seed = wallet.get_seed()
  config.seed = seed
  config.language = "English"  

  wallet = MoneroWalletKeys.create_wallet_from_seed(config)
  assert wallet.get_seed() == seed

def test_get_keys():
  config = MoneroWalletConfig()
  config.language = "English"
  config.network_type = MoneroNetworkType.TESTNET
  wallet = MoneroWalletKeys.create_wallet_random(config)

  assert wallet.get_private_view_key() is not None
  assert wallet.get_private_spend_key() is not None
  assert isinstance(wallet.get_private_view_key(), str)
  assert isinstance(wallet.get_private_spend_key(), str)