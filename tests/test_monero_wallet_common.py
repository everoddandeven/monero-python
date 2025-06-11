import pytest

from abc import ABC, abstractmethod
from typing import Optional

from monero import (
  MoneroWallet, MoneroWalletRpc, MoneroDaemonRpc, MoneroWalletConfig, MoneroUtils,
  MoneroTxConfig, MoneroDestination, MoneroRpcConnection
)
from utils import MoneroTestUtils as TestUtils


class BaseTestMoneroWallet(ABC):

  _wallet: MoneroWallet
  _daemon: MoneroDaemonRpc

  # region Private Methods

  def _get_test_daemon(self) -> MoneroDaemonRpc:
    return TestUtils.get_daemon_rpc()

  @abstractmethod
  def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
    ...

  @abstractmethod
  def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWallet:
    ...

  @abstractmethod
  def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
    ...

  @abstractmethod
  def _get_seed_languages(self) -> list[str]:
    ...

  def _open_wallet_from_path(self, path: str, password: str | None) -> MoneroWallet:
    config = MoneroWalletConfig()
    config.path = path
    config.password = password

    return self._open_wallet(config)

  @abstractmethod
  def get_test_wallet(self) -> MoneroWallet:
    ...

  # endregion

  # region Tests

  def test_create_wallet_random(self) -> None:
    """
    Can create a random wallet.
    """
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    e1: Exception | None = None
    wallet: MoneroWallet | None = None
    try:
      config = MoneroWalletConfig()
      wallet = self._create_wallet(config)
      path = wallet.get_path()
      e2: Exception | None = None

      try:
        MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
        MoneroUtils.validate_private_view_key(wallet.get_private_view_key())
        MoneroUtils.validate_private_spend_key(wallet.get_private_spend_key())
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        if not isinstance(wallet, MoneroWalletRpc): 
          TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())  # TODO monero-wallet-rpc: get seed language
      except Exception as e:
        e2 = e
    
      self._close_wallet(wallet)
      if e2 is not None:
        raise e2
      
      # attempt to create wallet at same path
      try:
        config = MoneroWalletConfig()
        config.path = path
        wallet = self._create_wallet(config)
      except Exception as e:
        TestUtils.assert_equals("Wallet already exists: " + path, str(e))

      # attempt to create wallet with unknown language
      try:
        config = MoneroWalletConfig()
        config.language = "english"
        raise Exception("Should have thrown error")
      except Exception as e:
        TestUtils.assert_equals("Unknown language: english", str(e))

    except Exception as e:
      e1 = e

    if e1 is not None:
      raise e1
  
  def test_create_wallet_from_seed(self) -> None:
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    e1: Exception | None = None  # emulating Python "finally" but compatible with other languages
    try:
      
      # save for comparison
      primaryAddress = self._wallet.get_primary_address()
      privateViewKey = self._wallet.get_private_view_key()
      privateSpendKey = self._wallet.get_private_spend_key()
      
      # recreate test wallet from seed
      config = MoneroWalletConfig()
      config.seed = TestUtils.SEED
      config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT

      wallet: MoneroWallet = self._create_wallet(config)
      path = wallet.get_path()
      e2: Exception | None = None
      try:
        TestUtils.assert_equals(primaryAddress, wallet.get_primary_address())
        TestUtils.assert_equals(privateViewKey, wallet.get_private_view_key())
        TestUtils.assert_equals(privateSpendKey, wallet.get_private_spend_key())
        TestUtils.assert_equals(TestUtils.SEED, wallet.get_seed())
        if not isinstance(wallet, MoneroWalletRpc):
          TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
      except Exception as e:
        e2 = e
      
      self._close_wallet(wallet)
      if e2 is not None:
        raise e2
      
      # attempt to create wallet with two missing words
      try:
        config = MoneroWalletConfig()
        config.seed = "memoir desk algebra inbound innocent unplugs fully okay five inflamed giant factual ritual toyed topic snake unhappy guarded tweezers haunted inundate giant"
        config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
        wallet = self._create_wallet(config)
      except Exception as e:
        TestUtils.assert_equals("Invalid mnemonic", str(e))
      
      # attempt to create wallet at same path
      try:
        config = MoneroWalletConfig()
        config.path = path
        self._create_wallet(config)
        raise Exception("Should have thrown error")
      except Exception as e:
        TestUtils.assert_equals("Wallet already exists: " + path, str(e))
  
    except Exception as e:
      e1 = e

    if e1 is not None:
      raise e1

  def test_create_wallet_from_seed_with_offset(self) -> None:
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    e1: Exception | None = None  # emulating Python "finally" but compatible with other languages
    try:

      # create test wallet with offset
      config = MoneroWalletConfig()
      config.seed = TestUtils.SEED
      config.restore_height = TestUtils.FIRST_RECEIVE_HEIGHT
      config.seed_offset = "my secret offset!"
      wallet: MoneroWallet = self._create_wallet(config)
      e2: Exception | None = None
      try:
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        TestUtils.assert_not_equals(TestUtils.SEED, wallet.get_seed())
        MoneroUtils.validate_address(wallet.get_primary_address(), TestUtils.NETWORK_TYPE)
        TestUtils.assert_not_equals(TestUtils.ADDRESS, wallet.get_primary_address())
        if not isinstance(wallet, MoneroWalletRpc):
          TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language()) # TODO monero-wallet-rpc: support
      except Exception as e:
        e2 = e
      
      self._close_wallet(wallet)
      if e2 is not None:
        raise e2
    except Exception as e:
      e1 = e
    
    if e1 is not None:
      raise e1

  def test_create_wallet_from_keys(self) -> None:
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    e1: Exception | None = None # emulating Java "finally" but compatible with other languages
    try:
      # save for comparison
      primaryAddress = self._wallet.get_primary_address()
      privateViewKey = self._wallet.get_private_view_key()
      privateSpendKey = self._wallet.get_private_spend_key()
      
      # recreate test wallet from keys
      config = MoneroWalletConfig()
      config.primary_address = primaryAddress
      config.private_view_key = privateViewKey
      config.private_spend_key = privateSpendKey
      config.restore_height = self._daemon.get_height()
      wallet: MoneroWallet = self._create_wallet(config)
      path = wallet.get_path()
      e2: Exception | None = None
      try:
        TestUtils.assert_equals(primaryAddress, wallet.get_primary_address())
        TestUtils.assert_equals(privateViewKey, wallet.get_private_view_key())
        TestUtils.assert_equals(privateSpendKey, wallet.get_private_spend_key())
        if not wallet.is_connected_to_daemon():
          print("WARNING: wallet created from keys is not connected to authenticated daemon") # TODO monero-project: keys wallets not connected
        TestUtils.assert_true(wallet.is_connected_to_daemon(), "Wallet created from keys is not connected to authenticated daemon")
        if not isinstance(wallet, MoneroWalletRpc):
          MoneroUtils.validate_mnemonic(wallet.get_seed()) # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
          TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())
        
      except Exception as e:
        e2 = e
      
      self._close_wallet(wallet)
      if e2 is not None:
        raise e2
      
      # recreate test wallet from spend key
      if not isinstance(wallet, MoneroWalletRpc): # TODO monero-wallet-rpc: cannot create wallet from spend key?
        config = MoneroWalletConfig()
        config.private_spend_key = privateSpendKey
        config.restore_height = self._daemon.get_height()
        wallet = self._create_wallet(config)
        e2 = None
        try:
          TestUtils.assert_equals(primaryAddress, wallet.get_primary_address())
          TestUtils.assert_equals(privateViewKey, wallet.get_private_view_key())
          TestUtils.assert_equals(privateSpendKey, wallet.get_private_spend_key())
          if not wallet.is_connected_to_daemon():
            print("WARNING: wallet created from keys is not connected to authenticated daemon") # TODO monero-project: keys wallets not connected
          TestUtils.assert_true(wallet.is_connected_to_daemon(), "Wallet created from keys is not connected to authenticated daemon")
          if not isinstance(wallet, MoneroWalletRpc):
            MoneroUtils.validate_mnemonic(wallet.get_seed()) # TODO monero-wallet-rpc: cannot get seed from wallet created from keys?
            TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, wallet.get_seed_language())

        except Exception as e:
          e2 = e
        
        self._close_wallet(wallet)
        if e2 is not None:
          raise e2
      
      # attempt to create wallet at same path
      try:
        config = MoneroWalletConfig()
        config.path = path
        self._create_wallet(config)
        raise Exception("Should have thrown error")
      except Exception as e:
        TestUtils.assert_equals("Wallet already exists: " + path, str(e))
      
    except Exception as e:
      e1 = e
    
    
    if e1 is not None:
      raise e1

  def test_subaddress_lookahead(self) -> None:
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    e1: Exception | None = None  # emulating Java "finally" but compatible with other languages
    receiver: MoneroWallet | None = None
    try:
      # create wallet with high subaddress lookahead
      config = MoneroWalletConfig()
      config.account_lookahead = 1
      config.subaddress_lookahead = 100000
      receiver = self._create_wallet(config)
     
      # transfer funds to subaddress with high index
      tx_config = MoneroTxConfig()
      tx_config.account_index = 0
      dest = MoneroDestination()
      dest.address = receiver.get_subaddress(0, 85000).address
      dest.amount = TestUtils.MAX_FEE
      tx_config.destinations.append(dest)
      tx_config.relay = True

      self._wallet.create_tx(tx_config)
     
      # observe unconfirmed funds
      
      TestUtils.wait_for(1000)
      receiver.sync()
      assert receiver.get_balance() > 0
    except Exception as e:
      e1 = e
   
    if receiver is not None:
      self._close_wallet(receiver)
    if e1 is not None:
      raise e1

  def test_get_version(self) -> None:
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    version = self._wallet.get_version()
    assert version.number is not None
    assert version.number > 0
    assert version.is_release is not None

  def test_get_path(self) -> None:
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    
    # create random wallet
    config = MoneroWalletConfig()
    wallet = self._create_wallet(config)
    
    # set a random attribute
    #String uuid = UUID.randomUUID().toString()
    uuid = TestUtils.get_random_string()
    wallet.set_attribute("uuid", uuid)
    
    # record the wallet's path then save and close
    path = wallet.get_path()
    self._close_wallet(wallet, True)
    
    # re-open the wallet using its path
    wallet = self._open_wallet_from_path(path, None)
    
    # test the attribute
    TestUtils.assert_equals(uuid, wallet.get_attribute("uuid"))
    self._close_wallet(wallet)

  def test_set_daemon_connection(self):
    
    # create random wallet with default daemon connection
    config = MoneroWalletConfig()
    wallet = self._create_wallet(config)
    connection = MoneroRpcConnection(TestUtils.DAEMON_RPC_URI, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD)
    TestUtils.assert_equals(connection, wallet.get_daemon_connection())
    TestUtils.assert_true(wallet.is_connected_to_daemon()) # uses default localhost connection
    
    # set empty server uri
    wallet.set_daemon_connection("")
    TestUtils.assert_equals(None, wallet.get_daemon_connection())
    TestUtils.assert_false(wallet.is_connected_to_daemon())
    
    # set offline server uri
    wallet.set_daemon_connection(TestUtils.OFFLINE_SERVER_URI)
    connection = MoneroRpcConnection(TestUtils.OFFLINE_SERVER_URI, "", "")
    TestUtils.assert_equals(connection, wallet.get_daemon_connection())
    TestUtils.assert_false(wallet.is_connected_to_daemon())
    
    # set daemon with wrong credentials
    wallet.set_daemon_connection(TestUtils.DAEMON_RPC_URI, "wronguser", "wrongpass")
    connection = MoneroRpcConnection(TestUtils.DAEMON_RPC_URI, "wronguser", "wrongpass")
    TestUtils.assert_equals(connection, wallet.get_daemon_connection())
    if "" == TestUtils.DAEMON_RPC_USERNAME or TestUtils.DAEMON_RPC_USERNAME is None:
      TestUtils.assert_true(wallet.is_connected_to_daemon()) # TODO: monerod without authentication works with bad credentials?
    else:
      TestUtils.assert_false(wallet.is_connected_to_daemon())
    
    # set daemon with authentication
    wallet.set_daemon_connection(TestUtils.DAEMON_RPC_URI, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD)
    connection = MoneroRpcConnection(TestUtils.DAEMON_RPC_URI, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD)
    TestUtils.assert_equals(connection, wallet.get_daemon_connection())
    TestUtils.assert_true(wallet.is_connected_to_daemon())
    
    # nullify daemon connection
    wallet.set_daemon_connection(None)
    TestUtils.assert_equals(None, wallet.get_daemon_connection())
    wallet.set_daemon_connection(TestUtils.DAEMON_RPC_URI)
    connection = MoneroRpcConnection(TestUtils.DAEMON_RPC_URI)
    TestUtils.assert_equals(connection, wallet.get_daemon_connection())
    wallet.set_daemon_connection(None)
    TestUtils.assert_equals(None, wallet.get_daemon_connection())
    
    # set daemon uri to non-daemon
    wallet.set_daemon_connection("www.getmonero.org")
    connection = MoneroRpcConnection("www.getmonero.org")
    TestUtils.assert_equals(connection, wallet.get_daemon_connection())
    TestUtils.assert_false(wallet.is_connected_to_daemon())
    
    # set daemon to invalid uri
    wallet.set_daemon_connection("abc123")
    TestUtils.assert_false(wallet.is_connected_to_daemon())
    
    # attempt to sync
    try:
      wallet.sync()
      raise Exception("Exception expected")
    except Exception as e:
      TestUtils.assert_equals("Wallet is not connected to daemon", str(e))
    finally:
      self._close_wallet(wallet)

  def test_get_seed(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    seed = self._wallet.get_seed()
    MoneroUtils.validate_mnemonic(seed)
    TestUtils.assert_equals(TestUtils.SEED, seed)

  def test_get_seed_language(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    language = self._wallet.get_seed_language()
    TestUtils.assert_equals(MoneroWallet.DEFAULT_LANGUAGE, language)

  def test_get_seed_languages(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    languages = self._get_seed_languages()
    assert len(languages) > 0
    for language in languages:
      assert len(language) > 0

  def test_get_private_view_key(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    privateViewKey = self._wallet.get_private_view_key()
    MoneroUtils.validate_private_view_key(privateViewKey)

  def test_get_private_spend_key(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    privateSpendKey = self._wallet.get_private_spend_key()
    MoneroUtils.validate_private_spend_key(privateSpendKey)

  def test_get_public_view_key(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    publicViewKey = self._wallet.get_public_view_key()
    MoneroUtils.validate_private_spend_key(publicViewKey)

  def test_get_public_spend_key(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    publicSpendKey = self._wallet.get_public_spend_key()
    MoneroUtils.validate_private_spend_key(publicSpendKey)

  def test_get_primary_address(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    primaryAddress = self._wallet.get_primary_address()
    MoneroUtils.validate_address(primaryAddress, TestUtils.NETWORK_TYPE)
    TestUtils.assert_equals(self._wallet.get_address(0, 0), primaryAddress)
  
  def test_get_subaddress_address(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    TestUtils.assert_equals(self._wallet.get_primary_address(), (self._wallet.get_address(0, 0)))
    for account in self._wallet.get_accounts(True):
      for subaddress in account.subaddresses:
        assert account.index is not None
        assert subaddress.index is not None
        TestUtils.assert_equals(subaddress.address, self._wallet.get_address(account.index, subaddress.index))

  def test_get_subaddress_address_out_of_range(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    accounts = self._wallet.get_accounts(True)
    accountIdx = len(accounts) - 1
    subaddressIdx = len(accounts[accountIdx].subaddresses)
    address = self._wallet.get_address(accountIdx, subaddressIdx)
    TestUtils.assert_not_none(address)
    TestUtils.assert_true(len(address) > 0)

  def test_get_address_indices(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    wallet = self._wallet
    # get last subaddress to test
    accounts = wallet.get_accounts(True)
    accountIdx = len(accounts) - 1
    subaddressIdx = len(accounts[accountIdx].subaddresses) - 1
    address = wallet.get_address(accountIdx, subaddressIdx)
    TestUtils.assert_not_none(address)
    
    # get address index
    subaddress = wallet.get_address_index(address)
    TestUtils.assert_equals(accountIdx, subaddress.account_index)
    TestUtils.assert_equals(subaddressIdx, subaddress.index)

    # test valid but unfound address
    nonWalletAddress = TestUtils.get_external_wallet_address()
    try:
      subaddress = wallet.get_address_index(nonWalletAddress)
      raise Exception("Should have thrown exception")
    except Exception as e:
      TestUtils.assert_equals("Address doesn't belong to the wallet", str(e))
    
    # test invalid address
    try:
      subaddress = wallet.get_address_index("this is definitely not an address")
      raise Exception("Should have thrown exception")
    except Exception as e:
      TestUtils.assert_equals("Invalid address", str(e))

  def test_decode_integrated_address(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    wallet = self._wallet
    integratedAddress = wallet.get_integrated_address('', "03284e41c342f036")
    decodedAddress = wallet.decode_integrated_address(integratedAddress.integrated_address)
    TestUtils.assert_equals(integratedAddress, decodedAddress)
    
    # decode invalid address
    try:
      wallet.decode_integrated_address("bad address")
      raise Exception("Should have failed decoding bad address")
    except Exception as e:
      TestUtils.assert_equals("Invalid address", str(e))

  def test_sync_without_progress(self):
    TestUtils.assert_true(TestUtils.TEST_NON_RELAYS)
    wallet = self._wallet
    daemon = self._daemon
    numBlocks = 100
    chainHeight = daemon.get_height()
    TestUtils.assert_true(chainHeight >= numBlocks)
    result = wallet.sync(chainHeight - numBlocks)  # sync end of chain
    TestUtils.assert_true(result.num_blocks_fetched >= 0)
    TestUtils.assert_not_none(result.received_money)

  # endregion