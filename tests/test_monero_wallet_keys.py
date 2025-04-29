import pytest
from typing import Optional
from monero import (
  MoneroWalletKeys, MoneroWalletConfig, MoneroUtils, MoneroWallet, MoneroVersion, MoneroAccount,
  MoneroSubaddress
)
from utils import MoneroTestUtils as Utils

_wallet: MoneroWalletKeys = Utils.get_wallet_keys()

# Create wallet utility
def create_wallet(config: MoneroWalletConfig):
  print(f"create_wallet()")
  # assign defaults
  if (config is None):
    config = MoneroWalletConfig()
    print(f"create_wallet(): created config")

  random: bool = config.seed is None and config.primary_address is None and config.private_spend_key is None
  print(f"create_wallet(): random = {random}")
  if config.path is None:
    config.path = Utils.TEST_WALLETS_DIR + "/" + Utils.get_random_string()
  if config.password is None:
    config.password = Utils.WALLET_PASSWORD
  if config.network_type is None:
    config.network_type = Utils.NETWORK_TYPE
  if (config.restore_height is None and not random):
    config.restore_height = 0
  
  # create wallet
  if random:
    wallet = MoneroWalletKeys.create_wallet_random(config)
  elif config.seed is not None and config.seed != "":
    wallet = MoneroWalletKeys.create_wallet_from_seed(config)
  elif config.primary_address is not None and config.private_view_key is not None:
    wallet = MoneroWalletKeys.create_wallet_from_keys(config)
  elif config.primary_address is not None and config.private_spend_key is not None:
    wallet = MoneroWalletKeys.create_wallet_from_keys(config)
  else:
    raise Exception("Invalid configuration")
  
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
    print("test_create_wallet_random(): creating keys wallet...")
    wallet: MoneroWallet = create_wallet(MoneroWalletConfig())
    print("keys wallet created: " + wallet.get_seed())
    e2: Optional[Exception] = None
    try:
      MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
      MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
      MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
      MoneroUtils.validate_mnemonic(wallet.get_seed())
      Utils.assert_equals("English", wallet.get_seed_language())
    except Exception as e:
      e2 = e
    
    close_wallet(wallet)
    
    if (e2 != None):
      raise e2

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

# Can create wallet from seed
def test_create_wallet_from_seed():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  e1: Optional[Exception] = None  # emulating Java "finally" but compatible with other languages
  try:
    # save for comparison
    primaryAddress: str = _wallet.get_primary_address()
    privateViewKey: str = _wallet.get_private_view_key()
    privateSpendKey: str = _wallet.get_private_spend_key()
    
    # recreate test wallet from seed
    config = MoneroWalletConfig()
    config.seed = Utils.SEED

    wallet: MoneroWallet = create_wallet(config)

    e2: Optional[Exception] = None
    try:
      Utils.assert_equals(primaryAddress, wallet.get_primary_address())
      Utils.assert_equals(privateViewKey, wallet.get_private_view_key())
      Utils.assert_equals(privateSpendKey, wallet.get_private_spend_key())
      Utils.assert_equals(Utils.SEED, wallet.get_seed())
      #if (!(wallet instanceof MoneroWalletRpc)) Utils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.getSeedLanguage())
    except Exception as e:
      e2 = e
    
    close_wallet(wallet)
    if e2 is not None: 
      raise e2
    
    # attempt to create wallet with two missing words
    try:
      invalidMnemonic: str = "memoir desk algebra inbound innocent unplugs fully okay five inflamed giant factual ritual toyed topic snake unhappy guarded tweezers haunted inundate giant"
      config = MoneroWalletConfig()
      config.seed = invalidMnemonic

      wallet = create_wallet(config)
    except Exception as e:
      Utils.assert_equals("Invalid mnemonic", str(e))
    
  except Exception as e:
    e1 = e
  
  if e1 is not None:
    raise Exception(e1)

# Can create wallet from keys
def test_create_wallet_from_keys():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  e1: Optional[Exception] = None # emulating Java "finally" but compatible with other languages
  try:
    # save for comparison
    primaryAddress: str = _wallet.get_primary_address()
    privateViewKey: str = _wallet.get_private_view_key()
    privateSpendKey: str = _wallet.get_private_spend_key()
    
    # recreate test wallet from keys
    config = MoneroWalletConfig()
    config.primary_address = primaryAddress
    config.private_view_key = privateViewKey
    config.private_spend_key = privateSpendKey
    wallet: MoneroWallet = create_wallet(config)
    e2: Optional[Exception] = None
    try:
      Utils.assert_equals(primaryAddress, wallet.get_primary_address())
      Utils.assert_equals(privateViewKey, wallet.get_private_view_key())
      Utils.assert_equals(privateSpendKey, wallet.get_private_spend_key())
      MoneroUtils.validate_mnemonic(wallet.get_seed()) # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
      Utils.assert_equals("English", wallet.get_seed_language())
    except Exception as e:
      e2 = e
    
    close_wallet(wallet)
    if e2 is not None: 
      raise e2
    
    # recreate test wallet from spend key
    test_config = MoneroWalletConfig()
    test_config.primary_address = primaryAddress
    test_config.private_spend_key = privateSpendKey
    wallet = create_wallet(test_config)
    e2 = None
    try:
      Utils.assert_equals(primaryAddress, wallet.get_primary_address())
      Utils.assert_equals(privateViewKey, wallet.get_private_view_key())
      Utils.assert_equals(privateSpendKey, wallet.get_private_spend_key())
      MoneroUtils.validate_mnemonic(wallet.get_seed()) # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
      Utils.assert_equals("English", wallet.get_seed_language())
    except Exception as e:
      e2 = e
    
    close_wallet(wallet)
    if e2 is not None: 
      raise e2
    
  except Exception as e:
    e1 = e
  
  if e1 is not None: 
    raise Exception(e1)

# Can get the wallet's version
def test_get_version():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  version: MoneroVersion = _wallet.get_version()
  assert version.number is not None
  Utils.assert_true(version.number > 0)
  Utils.assert_not_none(version.is_release)

# Can get seed language
def test_get_seed_language():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  language = _wallet.get_seed_language()
  assert MoneroUtils.is_valid_language(language), f"Invalid seed language: {language}"

# Can get seed languanges
def test_get_seed_languages():
  languages: list[str] = MoneroWalletKeys.get_seed_languages()

  for language in languages:
    assert MoneroUtils.is_valid_language(language), f"Invalid seed language: {language}"

# Can get private view key
def test_get_private_view_key():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  private_view_key = _wallet.get_private_view_key()
  MoneroUtils.validate_private_view_key(private_view_key)

# Can get private spend key
def test_get_private_spend_key():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  private_spend_key = _wallet.get_private_spend_key()
  MoneroUtils.validate_private_spend_key(private_spend_key)

# Can get primary address
def test_get_primary_address():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  primary_address = _wallet.get_primary_address()
  network_type = _wallet.get_network_type()
  MoneroUtils.validate_address(primary_address, network_type)

