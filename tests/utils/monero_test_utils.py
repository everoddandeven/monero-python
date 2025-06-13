from typing import Any, Optional, Union
from abc import ABC
from random import choices, shuffle
from time import sleep, time
from os.path import exists as pathExists
from os import makedirs
from monero import (
  MoneroNetworkType, MoneroTx, MoneroUtils, MoneroWalletFull, MoneroRpcConnection, 
  MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc, MoneroBlockHeader, MoneroBlockTemplate, 
  MoneroBlock, MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult, MoneroWalletKeys,
  MoneroSubaddress, MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo, MoneroHardForkInfo,
  MoneroAltChain, MoneroTxPoolStats, MoneroWallet, MoneroRpcError, MoneroTxConfig,
  MoneroAccount, MoneroTxWallet, MoneroTxQuery
)

from .wallet_sync_printer import WalletSyncPrinter
from .wallet_tx_tracker import WalletTxTracker
from .test_context import TestContext
from .tx_context import TxContext


class MoneroTestUtils(ABC):
  # directory with monero binaries to test (monerod and monero-wallet-rpc)
  MONERO_BINS_DIR = ""
  WALLET_PORT_OFFSETS: dict[MoneroWalletRpc, int] = {}
  BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

  _WALLET_FULL: Optional[MoneroWalletFull] = None
  _WALLET_KEYS: Optional[MoneroWalletKeys] = None
  _WALLET_RPC: Optional[MoneroWalletRpc] = None
  _DAEMON_RPC: Optional[MoneroDaemonRpc] = None
  # monero daemon rpc endpoint configuration (change per your configuration)
  DAEMON_RPC_URI: str = "localhost:28081"
  DAEMON_RPC_USERNAME: str = ""
  DAEMON_RPC_PASSWORD: str = ""
  DAEMON_LOCAL_PATH = MONERO_BINS_DIR + "/monerod"
  TEST_NON_RELAYS: bool = True

  WALLET_TX_TRACKER = WalletTxTracker()

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
  WALLET_RPC_ZMQ_ENABLED: bool = False
  WALLET_RPC_ZMQ_URI = "tcp:#" + WALLET_RPC_ZMQ_DOMAIN + ":" + str(WALLET_RPC_ZMQ_PORT_START)
  WALLET_RPC_LOCAL_PATH = MONERO_BINS_DIR + "/monero-wallet-rpc"
  WALLET_RPC_LOCAL_WALLET_DIR = MONERO_BINS_DIR
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
  def current_timestamp(cls) -> int:
    return round(time() * 1000)
  
  @classmethod
  def current_timestamp_str(cls) -> str:
    return f"{cls.current_timestamp()}"

  @classmethod
  def network_type_to_str(cls, nettype: MoneroNetworkType) -> str:
    if nettype == MoneroNetworkType.MAINNET:
      return "mainnet"
    elif nettype == MoneroNetworkType.TESTNET:
      return "testnet"
    elif nettype == MoneroNetworkType.STAGENET:
      return "stagenet"
    
    raise TypeError(f"Invalid network type provided: {str(nettype)}")

  @classmethod
  def get_network_type(cls) -> str:
    return cls.network_type_to_str(cls.NETWORK_TYPE)

  @classmethod
  def createDirIfNotExists(cls, dirPath: str) -> None:
    print(f"createDirIfNotExists(): {dirPath}")
    if pathExists(dirPath):
      return
    
    makedirs(dirPath)

  @classmethod
  def initializeTestWalletDir(cls) -> None:
    cls.createDirIfNotExists(cls.TEST_WALLETS_DIR)

  @classmethod
  def assert_false(cls, expr: Any, message: str = "assertion failed"):
    assert expr == False, message

  @classmethod
  def assert_true(cls, expr: Any, message: str = "assertion failed"):
    assert expr == True, message

  @classmethod
  def assert_not_none(cls, expr: Any, message: str = "assertion failed"):
    assert expr is not None, message

  @classmethod
  def assert_is_none(cls, expr: Any, message: str = "assertion failed"):
    assert expr is None, message

  @classmethod
  def assert_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed"):
    assert expr1 == expr2, f"{message}: {expr1} == {expr2}"

  @classmethod
  def assert_not_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed"):
    assert expr1 != expr2, f"{message}: {expr1} != {expr2}"

  @classmethod
  def assert_is(cls, expr: Any, what: Any, message: str = "assertion failed"):
    assert expr is what, f"{message}: {expr} is {what}"

  @classmethod
  def get_random_string(cls, n: int = 25) -> str:
    return ''.join(choices(cls.BASE58_ALPHABET, k=n))

  @classmethod
  def start_wallet_rpc_process(cls, offline: bool = False) -> MoneroWalletRpc:
    # get next available offset of ports to bind to
    portOffset: int = 1
    while (portOffset in cls.WALLET_PORT_OFFSETS.values()):
      portOffset += 1
    
    # create command to start client with internal monero-wallet-rpc process
    cmd: list[str] = [
        cls.WALLET_RPC_LOCAL_PATH,
        "--" + cls.get_network_type(),
        "--rpc-bind-port", f"{cls.WALLET_RPC_PORT_START + portOffset}",
        "--rpc-login", cls.WALLET_RPC_USERNAME + ":" + cls.WALLET_RPC_PASSWORD,
        "--wallet-dir", cls.WALLET_RPC_LOCAL_WALLET_DIR,
        "--rpc-access-control-origins", cls.WALLET_RPC_ACCESS_CONTROL_ORIGINS
    ]
    if (offline):
      cmd.append("--offline")
    else:
      cmd.extend(["--daemon-address", cls.DAEMON_RPC_URI])
    if cls.DAEMON_RPC_USERNAME is not None and cls.DAEMON_RPC_USERNAME != "":
      cmd.extend(["--daemon-login", cls.DAEMON_RPC_USERNAME + ":" + cls.DAEMON_RPC_PASSWORD])
    
    # start with zmq if enabled
    if (cls.WALLET_RPC_ZMQ_ENABLED):
      cmd.extend(["--zmq-rpc-bind-port", f"{cls.WALLET_RPC_ZMQ_BIND_PORT_START + portOffset}"])
      cmd.extend(["--zmq-pub", "tcp://" + cls.WALLET_RPC_ZMQ_DOMAIN + ":" + f"{cls.WALLET_RPC_ZMQ_PORT_START + portOffset}"])
    else:
      #cmd.add("--no-zmq") # TODO: enable this when zmq supported in monero-wallet-rpc
      pass
    
    # register wallet with port offset
    try:
      wallet = MoneroWalletRpc(cmd)
      cls.WALLET_PORT_OFFSETS[wallet] = portOffset
      return wallet
    except Exception as e:
      raise Exception(e)

  @classmethod
  def stop_wallet_rpc_process(cls, wallet: MoneroWalletRpc):
    del cls.WALLET_PORT_OFFSETS[wallet]
    wallet.stop_process()

  @classmethod
  def wait_for(cls, time: int):
    sleep(time / 1000)

  @classmethod
  def check_test_wallets_dir_exists(cls) -> bool:
    return pathExists(cls.TEST_WALLETS_DIR)

  @classmethod
  def create_test_wallets_dir(cls) -> None:
    makedirs(cls.TEST_WALLETS_DIR)

  @classmethod
  def get_daemon_rpc(cls) -> MoneroDaemonRpc:
    if cls._DAEMON_RPC is None:
      cls._DAEMON_RPC = MoneroDaemonRpc(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)

    return cls._DAEMON_RPC

  @classmethod
  def get_wallet_keys_config(cls) -> MoneroWalletConfig:
    config = MoneroWalletConfig()
    config.network_type = cls.NETWORK_TYPE
    config.seed = cls.SEED
    return config

  @classmethod
  def get_wallet_keys(cls) -> MoneroWalletKeys:
    if cls._WALLET_KEYS is None:
      config = cls.get_wallet_keys_config()
      cls._WALLET_KEYS = MoneroWalletKeys.create_wallet_from_seed(config)

    return cls._WALLET_KEYS

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
        cls.initializeTestWalletDir()
        
        # create wallet with connection
        daemon_connection = MoneroRpcConnection(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)
        config = cls.get_wallet_full_config(daemon_connection)
        cls._WALLET_FULL = MoneroWalletFull.create_wallet(config)
        assert cls.FIRST_RECEIVE_HEIGHT, cls._WALLET_FULL.get_restore_height()
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
    assert cls.SEED == cls._WALLET_FULL.get_seed()
    assert cls.ADDRESS == cls._WALLET_FULL.get_primary_address()
    return cls._WALLET_FULL

  @classmethod
  def get_wallet_rpc(cls) -> MoneroWalletRpc:
    if cls._WALLET_RPC is None:
      
      # construct wallet rpc instance with daemon connection
      rpc = MoneroRpcConnection(cls.WALLET_RPC_URI, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD, cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else '')
      cls._WALLET_RPC = MoneroWalletRpc(rpc)
    
    # attempt to open test wallet
    try:
      cls._WALLET_RPC.open_wallet(cls.WALLET_NAME, cls.WALLET_PASSWORD)
    except MoneroRpcError as e:
      
      # -1 returned when wallet does not exist or fails to open e.g. it's already open by another application
      if (e.get_code() == -1):
        # create wallet
        config = MoneroWalletConfig()
        config.path = cls.WALLET_NAME
        config.password = cls.WALLET_PASSWORD
        config.seed = cls.SEED
        config.restore_height = cls.FIRST_RECEIVE_HEIGHT
        cls._WALLET_RPC.create_wallet(config)
      else:
        raise e
    
    # ensure we're testing the right wallet
    assert cls.SEED == cls._WALLET_RPC.get_seed()
    assert cls.ADDRESS == cls._WALLET_RPC.get_primary_address()
    
    # sync and save wallet
    cls._WALLET_RPC.sync()
    cls._WALLET_RPC.save()
    cls._WALLET_RPC.start_syncing(cls.SYNC_PERIOD_IN_MS)
    
    # return cached wallet rpc
    return cls._WALLET_RPC

  @classmethod
  def create_wallet_ground_truth(cls, networkType: MoneroNetworkType, seed: str, startHeight: int | None, restoreHeight: int | None) -> MoneroWalletFull:
    # create directory for test wallets if it doesn't exist
    if not cls.check_test_wallets_dir_exists():
      cls.create_test_wallets_dir()
    
    # create ground truth wallet
    daemonConnection = MoneroRpcConnection(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)
    path = cls.TEST_WALLETS_DIR + "/gt_wallet_" + cls.current_timestamp_str()
    config = MoneroWalletConfig()
    config.path = path
    config.password = cls.WALLET_PASSWORD
    config.network_type = networkType
    config.seed = seed
    config.server = daemonConnection
    config.restore_height = restoreHeight

    if startHeight is None:
      startHeight = 0

    gtWallet = MoneroWalletFull.create_wallet(config)
    cls.assert_equals(restoreHeight, gtWallet.get_restore_height())
    gtWallet.sync(startHeight, WalletSyncPrinter())
    gtWallet.start_syncing(cls.SYNC_PERIOD_IN_MS)
    
    # close the full wallet when the runtime is shutting down to release resources
    
    return gtWallet

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
    assert template.seed_height is not None
    cls.assert_true(template.seed_height > 0)
    cls.assert_not_none(template.seed_hash)
    cls.assert_false(template.seed_hash == "")
    # next seed hash can be null or initialized TODO: test circumstances for each
  
  @classmethod
  def test_block_header(cls, header: MoneroBlockHeader, is_full: bool):
    cls.assert_not_none(header)
    assert header.height is not None
    cls.assert_true(header.height >= 0)
    assert header.major_version is not None
    cls.assert_true(header.major_version > 0)
    assert header.minor_version is not None
    cls.assert_true(header.minor_version >= 0)
    assert header.timestamp is not None
    if (header.height == 0):
      cls.assert_true(header.timestamp == 0)
    else:
      cls.assert_true(header.timestamp > 0)
    cls.assert_not_none(header.prev_hash)
    cls.assert_not_none(header.nonce)
    if (header.nonce == 0):
      print(f"WARNING: header nonce is 0 at height {header.height}") # TODO (monero-project): why is header nonce 0?
    else:
      assert header.nonce is not None
      cls.assert_true(header.nonce > 0)
    cls.assert_is_none(header.pow_hash)  # never seen defined
    if (is_full):
      assert header.size is not None
      assert header.depth is not None
      assert header.difficulty is not None
      assert header.cumulative_difficulty is not None
      assert header.hash is not None
      assert header.miner_tx_hash is not None
      assert header.num_txs is not None
      assert header.weight is not None
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
    assert miner_tx is not None
    cls.assert_not_none(miner_tx.is_miner_tx)
    assert miner_tx.version is not None
    cls.assert_true(miner_tx.version >= 0)
    cls.assert_not_none(miner_tx.extra)
    cls.assert_true(len(miner_tx.extra) > 0)
    assert miner_tx.unlock_time is not None
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
    assert block.miner_tx is not None
    cls.test_miner_tx(block.miner_tx)  # TODO: miner tx doesn't have as much stuff, can't call testTx?
    cls.test_block_header(block, ctx.headerIsFull)
    
    if (ctx.hasHex):
      assert block.hex is not None
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
  def is_empty(cls, value: Union[str, list, None]) -> bool:
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
      assert result.hash is not None
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
  
  @classmethod
  def test_unsigned_big_integer(cls, value: Any, boolVal: bool = False):
    if not isinstance(value, int):
      raise Exception("Value is not number")
    
    if value < 0:
      raise Exception("Value cannot be negative")

  @classmethod
  def test_account(cls, account: Optional[MoneroAccount]):
    # test account
    assert account is not None
    assert account.index is not None
    assert account.index >= 0
    assert account.primary_address is not None

    MoneroUtils.validate_address(account.primary_address, cls.NETWORK_TYPE)
    cls.test_unsigned_big_integer(account.balance)
    cls.test_unsigned_big_integer(account.unlocked_balance)
    
    # if given, test subaddresses and that their balances add up to account balances
    if account.subaddresses is not None:
      balance = 0
      unlockedBalance = 0
      i = 0
      j = len(account.subaddresses)
      while i < j:
        cls.test_subaddress(account.subaddresses[i])
        assert account.index == account.subaddresses[i].account_index
        assert i == account.subaddresses[i].index
        address_balance = account.subaddresses[i].balance
        assert address_balance is not None
        balance += address_balance
        address_balance = account.subaddresses[i].unlocked_balance
        assert address_balance is not None
        unlockedBalance += address_balance
      
      assert account.balance == balance, "Subaddress balances " + str(balance) + " != account " + str(account.index) + " balance " + str(account.balance)
      assert account.unlocked_balance == unlockedBalance, "Subaddress unlocked balances " + str(unlockedBalance) + " != account " + str(account.index) + " unlocked balance " + str(account.unlocked_balance)
    
    # tag must be undefined or non-empty
    tag = account.tag
    assert tag is None or len(tag) > 0

  @classmethod
  def test_subaddress(cls, subaddress: MoneroSubaddress):
    assert subaddress.account_index is not None
    assert subaddress.index is not None
    assert subaddress.balance is not None
    assert subaddress.num_unspent_outputs is not None
    assert subaddress.num_blocks_to_unlock is not None

    cls.assert_true(subaddress.account_index >= 0)
    cls.assert_true(subaddress.index >= 0)
    cls.assert_not_none(subaddress.address)
    cls.assert_true(subaddress.label is None or subaddress.label != "")
    cls.test_unsigned_big_integer(subaddress.balance)
    cls.test_unsigned_big_integer(subaddress.unlocked_balance)
    cls.assert_true(subaddress.num_unspent_outputs >= 0)
    cls.assert_not_none(subaddress.is_used)
    if subaddress.balance > 0:
      cls.assert_true(subaddress.is_used)
    cls.assert_true(subaddress.num_blocks_to_unlock >= 0)
  
  @classmethod
  def assert_subaddress_equal(cls, subaddress: Optional[MoneroSubaddress], other: Optional[MoneroSubaddress]):
    if subaddress is None and other is None:
      return
    assert not (subaddress is None or other is None)
    assert subaddress.address == other.address
    assert subaddress.account_index == other.account_index
    assert subaddress.balance == other.balance
    assert subaddress.index == other.index
    assert subaddress.is_used == other.is_used
    assert subaddress.label == other.label
    assert subaddress.num_blocks_to_unlock == other.num_blocks_to_unlock
    assert subaddress.num_unspent_outputs == other.num_unspent_outputs
    assert subaddress.unlocked_balance == other.unlocked_balance

  @classmethod
  def assert_subaddresses_equal(cls, subaddresses1: list[MoneroSubaddress], subaddresses2: list[MoneroSubaddress]):
    size1 = len(subaddresses1)
    size2 = len(subaddresses2)
    if size1 != size2:
      raise Exception("Number of subaddresses doens't match")
    
    i = 0

    while i < size1:
      cls.assert_subaddress_equal(subaddresses1[i], subaddresses2[i])
      i += 1

  @classmethod
  def test_known_peer(cls, peer: Optional[MoneroPeer], from_connection: bool):
    assert peer is not None, "Peer is null"
    assert peer.id is not None
    assert peer.host is not None
    assert peer.port is not None
    cls.assert_false(len(peer.id) == 0)
    cls.assert_false(len(peer.host) == 0)
    cls.assert_true(peer.port > 0)
    cls.assert_true(peer.rpc_port is None or peer.rpc_port >= 0)
    cls.assert_not_none(peer.is_online)
    if peer.rpc_credits_per_hash is not None: 
      cls.test_unsigned_big_integer(peer.rpc_credits_per_hash)
    if (from_connection): 
      cls.assert_is_none(peer.last_seen_timestamp)
    else:
      assert peer.last_seen_timestamp is not None

      if (peer.last_seen_timestamp < 0): 
        print(f"Last seen timestamp is invalid: {peer.last_seen_timestamp}")
      cls.assert_true(peer.last_seen_timestamp >= 0)
    
    cls.assert_true(peer.pruning_seed is None or peer.pruning_seed >= 0)

  @classmethod
  def test_peer(cls, peer: MoneroPeer):
    cls.assert_true(isinstance(peer, MoneroPeer))
    cls.test_known_peer(peer, True)
    assert peer.hash is not None
    assert peer.avg_download is not None
    assert peer.avg_upload is not None
    assert peer.current_download is not None
    assert peer.current_upload is not None
    assert peer.height is not None
    assert peer.live_time is not None
    assert peer.num_receives is not None
    assert peer.receive_idle_time is not None
    assert peer.num_sends is not None
    assert peer.send_idle_time is not None
    assert peer.num_support_flags is not None

    cls.assert_false(len(peer.hash) == 0)
    cls.assert_true(peer.avg_download >= 0)
    cls.assert_true(peer.avg_upload >= 0)
    cls.assert_true(peer.current_download >= 0)
    cls.assert_true(peer.current_upload >= 0)
    cls.assert_true(peer.height >= 0)
    cls.assert_true(peer.live_time >= 0)
    cls.assert_not_none(peer.is_local_ip)
    cls.assert_not_none(peer.is_local_host)
    cls.assert_true(peer.num_receives >= 0)
    cls.assert_true(peer.receive_idle_time >= 0)
    cls.assert_true(peer.num_sends >= 0)
    cls.assert_true(peer.send_idle_time >= 0)
    cls.assert_not_none(peer.state)
    cls.assert_true(peer.num_support_flags >= 0)
    cls.assert_not_none(peer.connection_type)

  @classmethod
  def test_info(cls, info: MoneroDaemonInfo):
    assert info.num_alt_blocks is not None
    assert info.block_size_limit is not None
    assert info.block_size_median is not None
    assert info.num_offline_peers is not None
    assert info.num_online_peers is not None
    assert info.height is not None
    assert info.height_without_bootstrap is not None
    assert info.num_incoming_connections is not None
    assert info.num_outgoing_connections is not None
    assert info.num_rpc_connections is not None
    assert info.start_timestamp is not None
    assert info.adjusted_timestamp is not None
    assert info.target is not None
    assert info.target_height is not None
    assert info.num_txs is not None
    assert info.num_txs_pool is not None
    assert info.block_weight_limit is not None
    assert info.block_weight_median is not None
    assert info.database_size is not None

    cls.assert_not_none(info.version)
    cls.assert_true(info.num_alt_blocks >= 0)
    cls.assert_true(info.block_size_limit > 0)
    cls.assert_true(info.block_size_median > 0)
    cls.assert_true(info.bootstrap_daemon_address is None or not cls.is_empty(info.bootstrap_daemon_address))
    cls.test_unsigned_big_integer(info.cumulative_difficulty)
    cls.test_unsigned_big_integer(info.free_space)
    cls.assert_true(info.num_offline_peers >= 0)
    cls.assert_true(info.num_online_peers >= 0)
    cls.assert_true(info.height >= 0)
    cls.assert_true(info.height_without_bootstrap > 0)
    cls.assert_true(info.num_incoming_connections >= 0)
    cls.assert_not_none(info.network_type)
    cls.assert_not_none(info.is_offline)
    cls.assert_true(info.num_outgoing_connections >= 0)
    cls.assert_true(info.num_rpc_connections >= 0)
    cls.assert_true(info.start_timestamp > 0)
    cls.assert_true(info.adjusted_timestamp > 0)
    cls.assert_true(info.target > 0)
    cls.assert_true(info.target_height >= 0)
    cls.assert_true(info.num_txs >= 0)
    cls.assert_true(info.num_txs_pool >= 0)
    cls.assert_not_none(info.was_bootstrap_ever_used)
    cls.assert_true(info.block_weight_limit > 0)
    cls.assert_true(info.block_weight_median > 0)
    cls.assert_true(info.database_size > 0)
    cls.assert_not_none(info.update_available)
    cls.test_unsigned_big_integer(info.credits, False) # 0 credits
    cls.assert_false(cls.is_empty(info.top_block_hash))
    cls.assert_not_none(info.is_busy_syncing)
    cls.assert_not_none(info.is_synchronized)

  @classmethod
  def test_sync_info(cls, syncInfo: MoneroDaemonSyncInfo):
    cls.assert_true(isinstance(syncInfo, MoneroDaemonSyncInfo))
    assert syncInfo.height is not None
    cls.assert_true(syncInfo.height >= 0)
    if syncInfo.peers is not None:
      cls.assert_true(len(syncInfo.peers) > 0)
      for connection in syncInfo.peers:
        cls.test_peer(connection)

    # TODO: test that this is being hit, so far not used
    if (syncInfo.spans is None):
      cls.assert_true(len(syncInfo.spans) > 0)
      for span in syncInfo.spans:
        testConnectionSpan(span)

    assert syncInfo.next_needed_pruning_seed is not None    
    cls.assert_true(syncInfo.next_needed_pruning_seed >= 0)
    cls.assert_is_none(syncInfo.overview)
    cls.test_unsigned_big_integer(syncInfo.credits, False) # 0 credits
    cls.assert_is_none(syncInfo.top_block_hash)

  @classmethod
  def test_hard_fork_info(cls, hardForkInfo: MoneroHardForkInfo):
    cls.assert_not_none(hardForkInfo.earliest_height)
    cls.assert_not_none(hardForkInfo.is_enabled)
    cls.assert_not_none(hardForkInfo.state)
    cls.assert_not_none(hardForkInfo.threshold)
    cls.assert_not_none(hardForkInfo.version)
    cls.assert_not_none(hardForkInfo.num_votes)
    cls.assert_not_none(hardForkInfo.voting)
    cls.assert_not_none(hardForkInfo.window)
    cls.test_unsigned_big_integer(hardForkInfo.credits, False) # 0 credits
    cls.assert_is_none(hardForkInfo.top_block_hash)

  @classmethod
  def test_alt_chain(cls, alt_chain: MoneroAltChain):
    cls.assert_not_none(alt_chain)
    cls.assert_false(len(alt_chain.block_hashes) == 0)
    cls.test_unsigned_big_integer(alt_chain.difficulty, True)
    assert alt_chain.height is not None
    assert alt_chain.length is not None
    assert alt_chain.main_chain_parent_block_hash is not None
    cls.assert_true(alt_chain.height > 0)
    cls.assert_true(alt_chain.length > 0)
    cls.assert_equals(64, len(alt_chain.main_chain_parent_block_hash))

  @classmethod
  def get_unrelayed_tx(cls, wallet: MoneroWallet, accountIdx: int):
    assert accountIdx > 0, "Txs sent from/to same account are not properly synced from the pool" # TODO monero-project
    config = MoneroTxConfig()
    config.account_index = accountIdx
    config.address = wallet.get_primary_address()
    config.amount = cls.MAX_FEE

    tx = wallet.create_tx(config)
    assert (tx.full_hex is None or tx.full_hex == "") is False
    assert tx.relay is False
    return tx

  @classmethod
  def test_tx_pool_stats(cls, stats: MoneroTxPoolStats):
    cls.assert_not_none(stats)
    assert stats.num_txs is not None
    cls.assert_true(stats.num_txs >= 0)
    if stats.num_txs > 0:
      #if (stats.num_txs == 1):
      #  cls.assert_is_none(stats.histo)
      #else:
      #  histo: dict[int, int] = stats.histo
      #  cls.assert_not_none(histo)
      #  cls.assert_true(len(histo) > 0)
        #for (Long key : histo.keySet()) {
        #  cls.assert_true(histo.get(key) >= 0)

      assert stats.bytes_max is not None     
      assert stats.bytes_med is not None
      assert stats.bytes_min is not None
      assert stats.bytes_total is not None
      assert stats.oldest_timestamp is not None
      assert stats.num10m is not None
      assert stats.num_double_spends is not None
      assert stats.num_failing is not None
      assert stats.num_not_relayed is not None

      cls.assert_true(stats.bytes_max > 0)
      cls.assert_true(stats.bytes_med > 0)
      cls.assert_true(stats.bytes_min > 0)
      cls.assert_true(stats.bytes_total > 0)
      cls.assert_true(stats.histo98pc is None or stats.histo98pc > 0)
      cls.assert_true(stats.oldest_timestamp > 0)
      cls.assert_true(stats.num10m >= 0)
      cls.assert_true(stats.num_double_spends >= 0)
      cls.assert_true(stats.num_failing >= 0)
      cls.assert_true(stats.num_not_relayed >= 0)

    else:
      cls.assert_is_none(stats.bytes_max)
      cls.assert_is_none(stats.bytes_med)
      cls.assert_is_none(stats.bytes_min)
      cls.assert_equals(0, stats.bytes_total)
      cls.assert_is_none(stats.histo98pc)
      cls.assert_is_none(stats.oldest_timestamp)
      cls.assert_equals(0, stats.num10m)
      cls.assert_equals(0, stats.num_double_spends)
      cls.assert_equals(0, stats.num_failing)
      cls.assert_equals(0, stats.num_not_relayed)
      #cls.assert_is_none(stats.histo)

  @classmethod
  def get_external_wallet_address(cls) -> str:
    networkType: MoneroNetworkType | None = cls.get_daemon_rpc().get_info().network_type

    if networkType == MoneroNetworkType.STAGENET:
      return "78Zq71rS1qK4CnGt8utvMdWhVNMJexGVEDM2XsSkBaGV9bDSnRFFhWrQTbmCACqzevE8vth9qhWfQ9SUENXXbLnmMVnBwgW" # subaddress
    if networkType == MoneroNetworkType.TESTNET:
        return "BhsbVvqW4Wajf4a76QW3hA2B3easR5QdNE5L8NwkY7RWXCrfSuaUwj1DDUsk3XiRGHBqqsK3NPvsATwcmNNPUQQ4SRR2b3V" # subaddress
    if networkType == MoneroNetworkType.MAINNET:
        return "87a1Yf47UqyQFCrMqqtxfvhJN9se3PgbmU7KUFWqhSu5aih6YsZYoxfjgyxAM1DztNNSdoYTZYn9xa3vHeJjoZqdAybnLzN" # subaddress
    else:
      raise Exception("Invalid network type: " + str(networkType))
  
  @classmethod
  def get_and_test_txs(cls, wallet: MoneroWallet, a, b, c: bool) -> list[MoneroTxWallet]:
    raise NotImplementedError()
  
  @classmethod
  def get_random_transactions(cls, wallet: MoneroWallet, query: Optional[MoneroTxQuery] = None, min_txs: Optional[int] = None, max_txs: Optional[int] = None) -> list[MoneroTxWallet]:
    txs = wallet.get_txs(query if query is not None else MoneroTxQuery())
    
    if min_txs is not None:
      assert len(txs) >= min_txs, f"{len(txs)}/{min_txs} transactions found with the query"

    shuffle(txs)

    if max_txs is None:
      return txs
    
    result: list[MoneroTxWallet] = []
    i = 0

    for tx in txs:
      result.append(tx)      
      if i >= max_txs - 1:
        break
      i += 1

    return result
  
  @classmethod
  def test_tx_wallet(cls, tx: MoneroTxWallet, ctx: TxContext) -> None:
    raise NotImplementedError()
  