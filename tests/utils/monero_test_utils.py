from typing import Any, Optional
from monero import (
  MoneroNetworkType, MoneroTx, MoneroUtils, MoneroWalletFull, MoneroRpcConnection, 
  MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc, MoneroBlockHeader, MoneroBlockTemplate, 
  MoneroBlock, MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult
)

from .wallet_sync_printer import WalletSyncPrinter
from .test_context import TestContext

class MoneroTestUtils:
  _WALLET_FULL: MoneroWalletFull
  # monero daemon rpc endpoint configuration (change per your configuration)
  DAEMON_RPC_URI: str = "localhost:28081"
  DAEMON_RPC_USERNAME: str = ""
  DAEMON_RPC_PASSWORD: str = ""
  TEST_NON_RELAYS: bool = True

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
  def assert_false(cls, expr: Any, message: Optional[str] = None):
    assert expr == False

  @classmethod
  def assert_true(cls, expr: Any, message: Optional[str] = None):
    assert expr == True

  @classmethod
  def assert_not_none(cls, expr: Any, message: Optional[str] = None):
    assert expr is not None

  @classmethod
  def assert_is_none(cls, expr: Any, message: Optional[str] = None):
    assert expr is None

  @classmethod
  def assert_equals(cls, expr1: Any, expr2: Any, message: Optional[str] = None):
    assert expr1 == expr2

  @classmethod
  def assert_not_equals(cls, expr1: Any, expr2: Any, message: Optional[str] = None):
    assert expr1 != expr2

  @classmethod
  def assert_is(cls, expr: Any, what: Any, message: Optional[str] = None):
    assert expr is what

  @classmethod
  def get_random_string(cls) -> str:
    raise NotImplementedError()

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
        #File testWalletsDir = new File(TestUtils.TEST_WALLETS_DIR)
        #if (!testWalletsDir.exists()) testWalletsDir.mkdirs()
        
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
  def get_wallet_rpc(cls) -> MoneroWalletRpc:
    raise NotImplementedError()

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
  
  @classmethod
  def test_block_template(cls, template: MoneroBlockTemplate):
    cls.assert_not_none(template)
    cls.assert_not_none(template.block_template_blob)
    cls.assert_not_none(template.block_hashing_blob)
    cls.assert_not_none(template.difficulty)
    cls.assert_not_none(template.expected_reward)
    cls.assert_not_none(template.height)
    cls.assert_not_none(template.prev_hash)
    cls.assert_not_none(template.reserved_offset)
    cls.assert_not_none(template.seed_height)
    cls.assert_true(template.seed_height > 0)
    cls.assert_not_none(template.seed_hash)
    cls.assert_false(template.seed_hash == "")
    # next seed hash can be null or initialized TODO: test circumstances for each
  
  @classmethod
  def test_block_header(cls, header: MoneroBlockHeader, is_full: bool):
    cls.assert_not_none(header)
    cls.assert_true(header.height >= 0)
    cls.assert_true(header.major_version > 0)
    cls.assert_true(header.minor_version >= 0)
    if (header.height == 0):
      cls.assert_true(header.timestamp == 0)
    else:
      cls.assert_true(header.timestamp > 0)
    cls.assert_not_none(header.prev_hash)
    cls.assert_not_none(header.nonce)
    if (header.nonce == 0):
      print(f"WARNING: header nonce is 0 at height {header.height}") # TODO (monero-project): why is header nonce 0?
    else:
      cls.assert_true(header.nonce > 0)
    cls.assert_is_none(header.pow_hash)  # never seen defined
    if (is_full):
      cls.assert_true(header.size > 0)
      cls.assert_true(header.depth >= 0)
      cls.assert_true(header.difficulty > 0)
      cls.assert_true(header.cumulative_difficulty > 0)
      cls.assert_equals(64, len(header.hash))
      cls.assert_equals(64, len(header.miner_tx_hash))
      cls.assert_true(header.num_txs >= 0)
      cls.assert_not_none(header.orphan_status)
      cls.assert_not_none(header.reward)
      cls.assert_not_none(header.weight)
      cls.assert_true(header.weight > 0)
    else:
      cls.assert_is_none(header.size)
      cls.assert_is_none(header.depth)
      cls.assert_is_none(header.difficulty)
      cls.assert_is_none(header.cumulative_difficulty)
      cls.assert_is_none(header.hash)
      cls.assert_is_none(header.miner_tx_hash)
      cls.assert_is_none(header.num_txs)
      cls.assert_is_none(header.orphan_status)
      cls.assert_is_none(header.reward)
      cls.assert_is_none(header.weight)
  
  @classmethod
  def test_miner_tx(cls, miner_tx: MoneroTx):
    cls.assert_not_none(miner_tx)
    cls.assert_not_none(miner_tx.is_miner_tx)
    cls.assert_true(miner_tx.version >= 0)
    cls.assert_not_none(miner_tx.extra)
    cls.assert_true(len(miner_tx.extra) > 0)
    cls.assert_true(miner_tx.unlock_time >= 0)

    # TODO: miner tx does not have hashes in binary requests so this will fail, need to derive using prunable data
    # TestContext ctx = new TestContext()
    # ctx.hasJson = false
    # ctx.isPruned = true
    # ctx.is_full = false
    # ctx.isConfirmed = true
    # ctx.isMiner = true
    # ctx.fromGetTxPool = true
    # testTx(miner_tx, ctx)
  
  @classmethod
  def test_tx(cls, tx: MoneroTx, ctx: TestContext):
    raise NotImplementedError()

  # TODO: test block deep copy
  @classmethod
  def test_block(cls, block: MoneroBlock, ctx: TestContext):    
    # test required fields
    cls.assert_not_none(block)
    cls.test_miner_tx(block.miner_tx)  # TODO: miner tx doesn't have as much stuff, can't call testTx?
    cls.test_block_header(block, ctx.headerIsFull)
    
    if (ctx.hasHex):
      cls.assert_not_none(block.hex)
      cls.assert_true(len(block.hex) > 1)
    else:
      cls.assert_is_none(block.hex)
    
    if (ctx.hasTxs):
      cls.assert_not_none(ctx.txContext)
      for tx in block.txs:
        cls.assert_true(block == tx.block)
        cls.test_tx(tx, ctx.txContext)
      
    else:
      cls.assert_is_none(ctx.txContext)
      cls.assert_is_none(block.txs)

  @classmethod
  def is_empty(cls, value: str) -> bool:
    return value == ""

  @classmethod
  def test_update_check_result(cls, result: MoneroDaemonUpdateCheckResult):
    cls.assert_true(isinstance(result,MoneroDaemonUpdateCheckResult))
    cls.assert_not_none(result.is_update_available)
    if (result.is_update_available):
      cls.assert_false(cls.is_empty(result.auto_uri), "No auto uri is daemon online?")
      cls.assert_false(cls.is_empty(result.user_uri))
      cls.assert_false(cls.is_empty(result.version))
      cls.assert_false(cls.is_empty(result.hash))
      cls.assert_equals(64, len(result.hash))
    else:
      cls.assert_is_none(result.auto_uri)
      cls.assert_is_none(result.user_uri)
      cls.assert_is_none(result.version)
      cls.assert_is_none(result.hash)

  @classmethod
  def test_update_download_result(cls, result: MoneroDaemonUpdateDownloadResult, path: Optional[str]):
    cls.test_update_check_result(result)
    if (result.is_update_available):
      if path is not None:
        cls.assert_equals(path, result.download_path)
      else:
        cls.assert_not_none(result.download_path)
    else:
      cls.assert_is_none(result.download_path)
  