from typing import Any, Optional
from monero import MoneroNetworkType, MoneroUtils, MoneroWalletFull, MoneroRpcConnection, MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc

from wallet_sync_printer import WalletSyncPrinter

class MoneroTestUtils:
  _WALLET_FULL: MoneroWalletFull
  # monero daemon rpc endpoint configuration (change per your configuration)
  DAEMON_RPC_URI: str = "localhost:28081"
  DAEMON_RPC_USERNAME: str = ""
  DAEMON_RPC_PASSWORD: str = ""

  # monero wallet rpc configuration (change per your configuration)
  WALLET_RPC_PORT_START: int = 28084 # test wallet executables will bind to consecutive ports after these
  WALLET_RPC_ZMQ_ENABLED: bool = False
  WALLET_RPC_ZMQ_PORT_START: int = 58083
  WALLET_RPC_ZMQ_BIND_PORT_START: int = 48083  # TODO: zmq bind port necessary?
  WALLET_RPC_USERNAME: str = "rpc_user"
  WALLET_RPC_PASSWORD: str = "abc123"
  WALLET_RPC_ZMQ_DOMAIN: str = "127.0.0.1"
  WALLET_RPC_DOMAIN: str = "localhost"
  WALLET_RPC_URI = WALLET_RPC_DOMAIN + ":" + str(WALLET_RPC_PORT_START)
  WALLET_RPC_ZMQ_URI = "tcp:#" + WALLET_RPC_ZMQ_DOMAIN + ":" + str(WALLET_RPC_ZMQ_PORT_START)
  WALLET_RPC_ACCESS_CONTROL_ORIGINS = "http:#localhost:8080" # cors access from web browser

  # test wallet config
  WALLET_NAME = "test_wallet_1"
  WALLET_PASSWORD = "supersecretpassword123"
  TEST_WALLETS_DIR = "./test_wallets"
  WALLET_FULL_PATH = TEST_WALLETS_DIR + "/" + WALLET_NAME

  # test wallet constants
  MAX_FEE = 7500000*10000
  NETWORK_TYPE: MoneroNetworkType = MoneroNetworkType.TESTNET
  LANGUAGE: str = "English"
  SEED: str = "silk mocked cucumber lettuce hope adrenalin aching lush roles fuel revamp baptism wrist long tender teardrop midst pastry pigment equip frying inbound pinched ravine frying"
  ADDRESS: str = "A1y9sbVt8nqhZAVm3me1U18rUVXcjeNKuBd1oE2cTs8biA9cozPMeyYLhe77nPv12JA3ejJN3qprmREriit2fi6tJDi99RR"
  FIRST_RECEIVE_HEIGHT: int = 171 # NOTE: this value must be the height of the wallet's first tx for tests
  SYNC_PERIOD_IN_MS: int = 5000 # period between wallet syncs in milliseconds
  OFFLINE_SERVER_URI: str = "offline_server_uri" # dummy server uri to remain offline because wallet2 connects to default if not given
  AUTO_CONNECT_TIMEOUT_MS: int = 3000

  @classmethod
  def assert_false(cls, expr: Any):
    assert expr == False

  @classmethod
  def assert_true(cls, expr: Any):
    assert expr == True

  @classmethod
  def assert_not_none(cls, expr: Any):
    assert expr is not None

  @classmethod
  def assert_is_none(cls, expr: Any):
    assert expr is None

  @classmethod
  def assert_equals(cls, expr1: Any, expr2: Any):
    assert expr1 == expr2

  @classmethod
  def assert_is(cls, expr: Any, what: Any):
    assert expr is what

  @classmethod
  def start_wallet_rpc_process(cls) -> MoneroWalletRpc:
    raise NotImplementedError("Not implemented")

  @classmethod
  def stop_wallet_rpc_process(cls, wallet: MoneroWalletRpc):
    raise NotImplementedError("Not implemented")

  @classmethod
  def wait_for(cls, time: int):
    raise NotImplementedError("Not implemented")

  @classmethod
  def get_daemon_rpc(cls) -> MoneroDaemonRpc:
    raise Exception("not implemented")

  @classmethod
  def get_wallet_full_config(cls, daemon_connection: MoneroRpcConnection) -> MoneroWalletConfig:
    config = MoneroWalletConfig()
    config.path = cls.WALLET_FULL_PATH
    config.password = cls.WALLET_PASSWORD
    config.network_type = cls.NETWORK_TYPE
    config.seed = cls.SEED
    config.server = daemon_connection
    config.restore_height = cls.FIRST_RECEIVE_HEIGHT

    return config
  
  @classmethod
  def get_wallet_full(cls) -> MoneroWalletFull:
    if cls._WALLET_FULL is None:
      # create wallet from seed if it doesn't exist
      if not MoneroWalletFull.wallet_exists(cls.WALLET_FULL_PATH):
        
        # create directory for test wallets if it doesn't exist
        #File testWalletsDir = new File(TestUtils.TEST_WALLETS_DIR);
        #if (!testWalletsDir.exists()) testWalletsDir.mkdirs();
        
        # create wallet with connection
        daemon_connection = MoneroRpcConnection(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)
        config = cls.get_wallet_full_config(daemon_connection)
        cls._WALLET_FULL = MoneroWalletFull.create_wallet(config)
        assert MoneroTestUtils.FIRST_RECEIVE_HEIGHT, cls._WALLET_FULL.get_restore_height()
        assert daemon_connection == cls._WALLET_FULL.get_daemon_connection()

      # otherwise open existing wallet and update daemon connection
      else:
        cls._WALLET_FULL = MoneroWalletFull.open_wallet(cls.WALLET_FULL_PATH, cls.WALLET_PASSWORD, cls.NETWORK_TYPE)
        cls._WALLET_FULL.set_daemon_connection(cls.get_daemon_rpc().get_rpc_connection())

    # sync and save wallet
    listener = WalletSyncPrinter()
    cls._WALLET_FULL.sync(listener)
    cls._WALLET_FULL.save()
    cls._WALLET_FULL.start_syncing(cls.SYNC_PERIOD_IN_MS) # start background synchronizing with sync period
        
    # ensure we're testing the right wallet
    assert MoneroTestUtils.SEED == cls._WALLET_FULL.get_seed()
    assert MoneroTestUtils.ADDRESS == cls._WALLET_FULL.get_primary_address()
    return cls._WALLET_FULL

  @classmethod
  def test_invalid_address(cls, address: Optional[str], networkType: MoneroNetworkType) -> None:
    if address is None:
      return

    cls.assert_false(MoneroUtils.is_valid_address(address, networkType))
    try:
      MoneroUtils.validate_address(address, networkType)
      raise Exception("Should have thrown exception")
    except Exception as e:
      cls.assert_false(len(str(e)) == 0)

  @classmethod
  def test_invalid_private_view_key(cls, privateViewKey: Optional[str]):
    if privateViewKey is None:
      return
    
    cls.assert_false(MoneroUtils.is_valid_private_view_key(privateViewKey))
    try:
      MoneroUtils.validate_private_view_key(privateViewKey)
      raise Exception("Should have thrown exception")
    except Exception as e:
      cls.assert_false(len(str(e)) == 0)
  
  @classmethod
  def test_invalid_public_view_key(cls, public_view_key: Optional[str]) -> None:
    if public_view_key is None:
      return

    cls.assert_false(MoneroUtils.is_valid_public_view_key(public_view_key))
    try:
      MoneroUtils.validate_public_view_key(public_view_key)
      raise Exception("Should have thrown exception")
    except Exception as e:
      cls.assert_false(len(str(e)) == 0)

  @classmethod
  def test_invalid_private_spend_key(cls, privateSpendKey: Optional[str]):
    if privateSpendKey is None:
      return

    try:
      cls.assert_false(MoneroUtils.is_valid_private_spend_key(privateSpendKey))
      MoneroUtils.validate_private_spend_key(privateSpendKey)
      raise Exception("Should have thrown exception")
    except Exception as e:
      cls.assert_false(len(str(e)) == 0)

  @classmethod
  def test_invalid_public_spend_key(cls, publicSpendKey: Optional[str]):
    if publicSpendKey is None:
      return
    
    cls.assert_false(MoneroUtils.is_valid_public_spend_key(publicSpendKey))
    try:
      MoneroUtils.validate_public_spend_key(publicSpendKey)
      raise Exception("Should have thrown exception")
    except Exception as e:
      cls.assert_false(len(str(e)) == 0)
  
  