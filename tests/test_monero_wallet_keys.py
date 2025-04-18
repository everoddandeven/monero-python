from typing import Optional
from monero import MoneroWalletKeys, MoneroWalletConfig, MoneroNetworkType, MoneroWalletRpc, MoneroUtils, MoneroWalletFull, MoneroWallet
from utils import MoneroTestUtils as Utils

# Create wallet utility
def create_wallet(config: MoneroWalletConfig, startSyncing: bool = True):
  # assign defaults
  if (config is None):
    config = MoneroWalletConfig()

  random: bool = config.seed is None and config.primary_address is None
  if config.path is None:
    config.path = Utils.TEST_WALLETS_DIR + "/" + Utils.get_random_string()
  if config.password is None:
    config.password = Utils.WALLET_PASSWORD
  if config.network_type is None:
    config.network_type = Utils.NETWORK_TYPE
  if (config.server is None and config.get_connection_manager() is None):
    config.setServer(daemon.get_rpc_connection())
  if (config.restore_height is None and not random):
    config.restore_height = 0
  
  # create wallet
  if random:
    wallet = MoneroWalletKeys.create_wallet_random(config)
  elif config.seed is not None and config.seed != "":
    wallet = MoneroWalletKeys.create_wallet_from_seed(config)
  elif config.primary_address is not None and config.primary_address != "" and config.private_view_key is not None and config.private_view_key != "":
    wallet = MoneroWalletKeys.create_wallet_from_keys(config)
  elif config.primary_address is not None and config.primary_address != "" and config.private_spend_key is not None and config.private_spend_key != "":
    wallet = MoneroWalletKeys.create_wallet_from_keys(config)
  else:
    raise Exception("Invalid configuration")
  if not random:
    Utils.assert_equals(0 if config.restore_height is None else config.restore_height, wallet.get_restore_height())
  if (startSyncing is not False and wallet.is_connected_to_daemon()):
    wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)
  return wallet

# Close wallet utility
def close_wallet(wallet: MoneroWallet, save: bool = False):
  wallet.close(save)

# Can create a random wallet
def test_create_wallet_random():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  e1: Optional[Exception] = None  # emulating Java "finally" but compatible with other languages
  try:
    # create random wallet
    wallet: MoneroWallet = create_wallet(MoneroWalletConfig())
    path: str = wallet.get_path()
    e2: Optional[Exception] = None
    try:
      MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
      MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
      MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
      MoneroUtils.validate_mnemonic(wallet.get_seed())
      if (not isinstance(wallet, MoneroWalletRpc)): 
        Utils.assert_equals("english", wallet.get_seed_language())  # TODO monero-wallet-rpc: get seed language
    except Exception as e:
      e2 = e
    
    close_wallet(wallet)
    
    if (e2 != None):
      raise e2
    
    # attempt to create wallet at same path
    try:
      c = MoneroWalletConfig()
      c.path = path
      create_wallet(c)
      raise Exception("Should have thrown error")
    except Exception as e:
      Utils.assert_equals("Wallet already exists: " + path, str(e))
    
    # attempt to create wallet with unknown language
    try:
      c = MoneroWalletConfig()
      c.language = "english"
      create_wallet(c) # TODO: support lowercase?
      raise Exception("Should have thrown error")
    except Exception as e:
      Utils.assert_equals("Unknown language: english", str(e))
    
  except Exception as e:
    e1 = e
  
  if (e1 != None):
    raise Exception(e1)
