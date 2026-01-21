import logging

from typing import Any, Optional, Union
from abc import ABC
from random import shuffle
from time import sleep, time
from os.path import exists as path_exists
from os import makedirs, getenv
from secrets import token_hex
from configparser import ConfigParser
from monero import (
    MoneroNetworkType, MoneroTx, MoneroUtils, MoneroWalletFull, MoneroRpcConnection,
    MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc, MoneroBlockHeader, MoneroBlockTemplate,
    MoneroBlock, MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult, MoneroWalletKeys,
    MoneroSubaddress, MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo, MoneroHardForkInfo,
    MoneroAltChain, MoneroTxPoolStats, MoneroWallet, MoneroRpcError, MoneroTxConfig, MoneroBan,
    MoneroAccount, MoneroTxWallet, MoneroTxQuery, MoneroConnectionSpan, SerializableStruct,
    MoneroMinerTxSum, MoneroDaemon
)

from .wallet_sync_printer import WalletSyncPrinter
from .wallet_tx_tracker import WalletTxTracker
from .test_context import TestContext
from .tx_context import TxContext
from .binary_block_context import BinaryBlockContext

logger: logging.Logger = logging.getLogger("TestUtils")


class TestUtils(ABC):
    __test__ = False
    _LOADED: bool = False

    IN_CONTAINER: bool = True
    """indicates if tests are running in docker container"""
    MIN_BLOCK_HEIGHT: int = 0
    """min blockchain height for tests"""
    WALLET_PORT_OFFSETS: dict[MoneroWalletRpc, int] = {}

    # objects cache
    _WALLET_FULL: Optional[MoneroWalletFull] = None
    """Default wallet full used for tests"""
    _WALLET_KEYS: Optional[MoneroWalletKeys] = None
    """Default wallet keys used for tests"""
    _WALLET_RPC: Optional[MoneroWalletRpc] = None
    """Default wallet rpc used for tests"""
    _DAEMON_RPC: Optional[MoneroDaemonRpc] = None
    """Default daemon rpc used for tests"""
    _WALLET_RPC_2: Optional[MoneroWalletRpc] = None
    """Additional wallet rpc instance"""

    DAEMON_RPC_URI: str = ""
    CONTAINER_DAEMON_RPC_URI: str = ""
    """monero daemon rpc endpoint configuration (change per your configuration)"""
    DAEMON_RPC_USERNAME: str = ""
    DAEMON_RPC_PASSWORD: str = ""
    TEST_NON_RELAYS: bool = True
    LITE_MODE: bool = False
    TEST_NOTIFICATIONS: bool = True

    WALLET_TX_TRACKER: WalletTxTracker

    # monero wallet rpc configuration (change per your configuration)
    WALLET_RPC_PORT_START: int = 18082
    """test wallet executables will bind to consecutive ports after these"""
    WALLET_RPC_ZMQ_ENABLED: bool = False
    WALLET_RPC_ZMQ_PORT_START: int = 58083
    WALLET_RPC_ZMQ_BIND_PORT_START: int = 48083  # TODO: zmq bind port necessary?
    WALLET_RPC_USERNAME: str = ""
    WALLET_RPC_PASSWORD: str = ""
    WALLET_RPC_ZMQ_DOMAIN: str = ""
    WALLET_RPC_DOMAIN: str = ""
    WALLET_RPC_URI: str = ""
    WALLET_RPC_URI_2: str = ""
    WALLET_RPC_ZMQ_URI: str = ""
    WALLET_RPC_ACCESS_CONTROL_ORIGINS: str = ""
    """cors access from web browser"""

    # test wallet config
    WALLET_NAME: str = ""
    WALLET_PASSWORD: str = ""
    TEST_WALLETS_DIR: str = ""
    WALLET_FULL_PATH: str = ""
    # test wallet constants
    MAX_FEE = 7500000*10000
    NETWORK_TYPE: MoneroNetworkType = MoneroNetworkType.MAINNET
    REGTEST: bool = False
    LANGUAGE: str = ""
    SEED: str = ""
    ADDRESS: str = ""
    PRIVATE_VIEW_KEY: str = ""
    PRIVATE_SPEND_KEY: str = ""
    PUBLIC_SPEND_KEY: str = ""
    PUBLIC_VIEW_KEY: str = ""
    FIRST_RECEIVE_HEIGHT: int = 0
    """NOTE: this value must be the height of the wallet's first tx for tests"""
    SYNC_PERIOD_IN_MS: int = 5000
    """period between wallet syncs in milliseconds"""
    OFFLINE_SERVER_URI: str = "offline_server_uri"
    """dummy server uri to remain offline because wallet2 connects to default if not given"""
    AUTO_CONNECT_TIMEOUT_MS: int = 3000

    # mining wallet config
    MINING_WALLET_NAME: str = ""
    MINING_WALLET_PASSWORD: str = ""
    MINING_SEED: str = ""
    MINING_ADDRESS: str = ""
    MINING_PRIVATE_VIEW_KEY: str = ""
    MINING_PRIVATE_SPEND_KEY: str = ""
    MINING_PUBLIC_SPEND_KEY: str = ""
    MINING_PUBLIC_VIEW_KEY: str = ""

    @classmethod
    def load_config(cls) -> None:
        """
        Load utils configuration from tests/config/config.ini
        """
        if cls._LOADED:
            return

        parser = ConfigParser()
        parser.read('tests/config/config.ini')

        # validate config
        assert parser.has_section("general")
        assert parser.has_section("daemon")
        assert parser.has_section("wallet")

        # parse general config
        nettype_str = parser.get('general', 'network_type')
        cls.TEST_NON_RELAYS = parser.getboolean('general', 'test_non_relays')
        cls.TEST_NOTIFICATIONS = parser.getboolean('general', 'test_notifications')
        cls.LITE_MODE = parser.getboolean('general', 'lite_mode')
        cls.AUTO_CONNECT_TIMEOUT_MS = parser.getint('general', 'auto_connect_timeout_ms')
        cls.NETWORK_TYPE = cls.parse_network_type(nettype_str)
        cls.REGTEST = cls.is_regtest(nettype_str)
        cls.WALLET_TX_TRACKER = WalletTxTracker(cls.MINING_ADDRESS)

        if cls.REGTEST:
            cls.MIN_BLOCK_HEIGHT = 250 # minimum block height for regtest environment

        # parse daemon config
        cls.DAEMON_RPC_URI = parser.get('daemon', 'rpc_uri')
        cls.CONTAINER_DAEMON_RPC_URI = cls.DAEMON_RPC_URI.replace("127.0.0.1", "node_2")
        cls.DAEMON_RPC_USERNAME = parser.get('daemon', 'rpc_username')
        cls.DAEMON_RPC_PASSWORD = parser.get('daemon', 'rpc_password')

        # parse wallet config
        cls.WALLET_NAME = parser.get('wallet', 'name')
        cls.WALLET_PASSWORD = parser.get('wallet', 'password')
        cls.ADDRESS = parser.get('wallet', 'address')
        cls.PRIVATE_VIEW_KEY = parser.get('wallet', 'private_view_key')
        cls.PRIVATE_SPEND_KEY = parser.get('wallet', 'private_spend_key')
        cls.PUBLIC_VIEW_KEY = parser.get('wallet', 'public_view_key')
        cls.PUBLIC_SPEND_KEY = parser.get('wallet', 'public_spend_key')
        cls.SEED = parser.get('wallet', 'seed')
        cls.FIRST_RECEIVE_HEIGHT = parser.getint('wallet', 'first_receive_height')
        cls.TEST_WALLETS_DIR = parser.get('wallet', 'dir')
        cls.WALLET_FULL_PATH = cls.TEST_WALLETS_DIR + "/" + cls.WALLET_NAME
        cls.LANGUAGE = parser.get('wallet', 'language')
        cls.WALLET_RPC_DOMAIN = parser.get('wallet', 'rpc_domain')
        cls.WALLET_RPC_PORT_START = parser.getint('wallet', 'rpc_port_start')
        cls.WALLET_RPC_USERNAME = parser.get('wallet', 'rpc_username')
        cls.WALLET_RPC_PASSWORD = parser.get('wallet', 'rpc_password')
        cls.WALLET_RPC_ACCESS_CONTROL_ORIGINS = parser.get('wallet', 'rpc_access_control_origins')
        cls.WALLET_RPC_ZMQ_ENABLED = parser.getboolean('wallet', 'rpc_zmq_enabled')
        cls.WALLET_RPC_ZMQ_PORT_START = parser.getint('wallet', 'rpc_zmq_port_start')
        cls.WALLET_RPC_ZMQ_BIND_PORT_START = parser.getint('wallet', 'rpc_zmq_bind_port_start')
        cls.WALLET_RPC_ZMQ_DOMAIN = parser.get('wallet', 'rpc_zmq_domain')
        cls.WALLET_RPC_URI = cls.WALLET_RPC_DOMAIN + ":" + str(cls.WALLET_RPC_PORT_START)
        cls.WALLET_RPC_URI_2 = cls.WALLET_RPC_DOMAIN + ":" + str(cls.WALLET_RPC_PORT_START + 1)
        cls.WALLET_RPC_ZMQ_URI = "tcp:#" + cls.WALLET_RPC_ZMQ_DOMAIN + ":" + str(cls.WALLET_RPC_ZMQ_PORT_START)
        cls.SYNC_PERIOD_IN_MS = parser.getint('wallet', 'sync_period_in_ms')
        in_container = getenv("IN_CONTAINER", "true")
        cls.IN_CONTAINER = in_container.lower() == "true" or in_container == "1"

        # parse mining wallet config
        cls.MINING_WALLET_NAME = parser.get('mining_wallet', 'name')
        cls.MINING_WALLET_PASSWORD = parser.get('mining_wallet', 'password')
        cls.MINING_ADDRESS = parser.get('mining_wallet', 'address')
        cls.MINING_PRIVATE_VIEW_KEY = parser.get('mining_wallet', 'private_view_key')
        cls.MINING_PRIVATE_SPEND_KEY = parser.get('mining_wallet', 'private_spend_key')
        cls.MINING_PUBLIC_VIEW_KEY = parser.get('mining_wallet', 'public_view_key')
        cls.MINING_PUBLIC_SPEND_KEY = parser.get('mining_wallet', 'public_spend_key')
        cls.MINING_SEED = parser.get('mining_wallet', 'seed')

        cls._LOADED = True

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
    def is_regtest(cls, network_type_str: Optional[str]) -> bool:
        if network_type_str is None:
            return False
        nettype = network_type_str.lower()
        return nettype == "regtest" or nettype == "reg"

    @classmethod
    def parse_network_type(cls, nettype: str) -> MoneroNetworkType:
        net = nettype.lower()
        if net == "mainnet" or net == "main" or cls.is_regtest(net):
            return MoneroNetworkType.MAINNET
        elif net == "testnet" or net == "test":
            return MoneroNetworkType.TESTNET
        elif net == "stagenet" or net == "stage":
            return MoneroNetworkType.STAGENET

        raise TypeError(f"Invalid network type provided: {str(nettype)}")

    @classmethod
    def get_network_type(cls) -> str:
        return cls.network_type_to_str(cls.NETWORK_TYPE)

    @classmethod
    def create_dir_if_not_exists(cls, dir_path: str) -> None:
        if path_exists(dir_path):
            return

        makedirs(dir_path)

    @classmethod
    def initialize_test_wallet_dir(cls) -> None:
        cls.create_dir_if_not_exists(cls.TEST_WALLETS_DIR)

    @classmethod
    def assert_false(cls, expr: Any, message: str = "assertion failed"):
        assert expr is False, message

    @classmethod
    def assert_true(cls, expr: Any, message: str = "assertion failed"):
        assert expr is True, message

    @classmethod
    def assert_not_none(cls, expr: Any, message: str = "assertion failed"):
        assert expr is not None, message

    @classmethod
    def assert_is_none(cls, expr: Any, message: str = "assertion failed"):
        assert expr is None, message

    @classmethod
    def assert_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed"):
        if isinstance(expr1, SerializableStruct) and isinstance(expr2, SerializableStruct):
            str1 = expr1.serialize()
            str2 = expr2.serialize()
            assert str1 == str2, f"{message}: {str1} == {str2}"
        elif isinstance(expr1, MoneroRpcConnection) and isinstance(expr2, MoneroRpcConnection):
            cls.assert_connection_equals(expr1, expr2)
        else:
            assert expr1 == expr2, f"{message}: {expr1} == {expr2}"

    @classmethod
    def assert_not_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed"):
        assert expr1 != expr2, f"{message}: {expr1} != {expr2}"

    @classmethod
    def assert_is(cls, expr: Any, what: Any, message: str = "assertion failed"):
        assert expr is what, f"{message}: {expr} is {what}"

    @classmethod
    def get_random_string(cls, n: int = 25) -> str:
        return token_hex(n)

    @classmethod
    def get_wallets(cls, wallet_type: str) -> list[MoneroWallet]:
        raise NotImplementedError()

    @classmethod
    def wait_for(cls, milliseconds: int):
        sleep(milliseconds / 1000)

    @classmethod
    def check_test_wallets_dir_exists(cls) -> bool:
        return path_exists(cls.TEST_WALLETS_DIR)

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
                cls.initialize_test_wallet_dir()

                # create wallet with connection
                daemon_connection = MoneroRpcConnection(
                    cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD
                )
                config = cls.get_wallet_full_config(daemon_connection)
                cls._WALLET_FULL = MoneroWalletFull.create_wallet(config)
                assert cls.FIRST_RECEIVE_HEIGHT == cls._WALLET_FULL.get_restore_height()
                # TODO implement __eq__ method
                #assert daemon_connection == cls._WALLET_FULL.get_daemon_connection()

                # otherwise open existing wallet and update daemon connection
            else:
                cls._WALLET_FULL = MoneroWalletFull.open_wallet(
                    cls.WALLET_FULL_PATH, cls.WALLET_PASSWORD, cls.NETWORK_TYPE
                )
                cls._WALLET_FULL.set_daemon_connection(cls.get_daemon_rpc().get_rpc_connection())

        # sync and save wallet
        if cls._WALLET_FULL.is_connected_to_daemon():
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
            rpc = MoneroRpcConnection(
                cls.WALLET_RPC_URI, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD,
                cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else ''
            )
            cls._WALLET_RPC = MoneroWalletRpc(rpc)

        # attempt to open test wallet
        try:
            cls._WALLET_RPC.open_wallet(cls.WALLET_NAME, cls.WALLET_PASSWORD)
        except MoneroRpcError as e:
            # -1 returned when wallet does not exist or fails to open e.g. it's already open by another application
            if e.get_code() == -1:
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
    def open_wallet_rpc(cls, c: Optional[MoneroWalletConfig]) -> MoneroWalletRpc:
        config = c if c is not None else MoneroWalletConfig()

        # assign defaults
        if config.password is None:
            config.password = cls.WALLET_PASSWORD

        if config.server is None:
            config.server = cls.get_daemon_rpc().get_rpc_connection()
            if cls.IN_CONTAINER:
                config.server.uri = "http://node_2:18081"

        if cls._WALLET_RPC_2 is not None:
            raise Exception(f"Cannot open wallet rpc: no resources left")

        if cls._WALLET_RPC_2 is None:
            rpc = MoneroRpcConnection(
                cls.WALLET_RPC_URI_2, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD,
                cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else ''
            )
            cls._WALLET_RPC_2 = MoneroWalletRpc(rpc)

        # open wallet
        cls._WALLET_RPC_2.stop_syncing()
        cls._WALLET_RPC_2.open_wallet(config)
        # TODO set trusted daemon connection
        # cls._WALLET_RPC_2.set_daemon_connection()
        if cls._WALLET_RPC_2.is_connected_to_daemon():
            cls._WALLET_RPC_2.start_syncing(TestUtils.SYNC_PERIOD_IN_MS)

        return cls._WALLET_RPC_2

    @classmethod
    def create_wallet_rpc(cls, c: Optional[MoneroWalletConfig]) -> MoneroWalletRpc:
        # assign defaults
        config = c if c is not None else MoneroWalletConfig()
        random = config.seed is None and config.primary_address is None

        if config.path is None:
            config.path = TestUtils.get_random_string()

        if config.password is None:
            config.password = TestUtils.WALLET_PASSWORD

        if config.restore_height is None and not random:
            config.restore_height = 0

        if config.server is None:
            config.server = TestUtils.get_daemon_rpc().get_rpc_connection()
            if cls.IN_CONTAINER:
                # TODO make this configurable
                config.server.uri = "http://node_2:18081"

        # create client connected to monero-wallet-rpc process
        wallet_rpc = cls._WALLET_RPC_2
        if wallet_rpc is not None:
            raise Exception(f"Cannot open wallet rpc: no resources left")

        if wallet_rpc is None:
            rpc = MoneroRpcConnection(
                cls.WALLET_RPC_URI_2, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD,
                cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else ''
            )
            wallet_rpc = MoneroWalletRpc(rpc)

        # create wallet
        wallet_rpc.stop_syncing()
        wallet_rpc.create_wallet(config)
        # TODO set trusted daemon connection
        # cls._WALLET_RPC_2.set_daemon_connection()
        if wallet_rpc.is_connected_to_daemon():
            wallet_rpc.start_syncing(TestUtils.SYNC_PERIOD_IN_MS)

        cls._WALLET_RPC_2 = wallet_rpc
        return cls._WALLET_RPC_2

    @classmethod
    def free_wallet_rpc_resources(cls) -> None:
        if cls._WALLET_RPC_2 is not None:
            try:
                cls._WALLET_RPC_2.close()
            except Exception as e:
                pass
        cls._WALLET_RPC_2 = None

    @classmethod
    def is_wallet_rpc_resource(cls, wallet: MoneroWallet) -> bool:
        return wallet is cls._WALLET_RPC_2

    @classmethod
    def free_wallet_rpc_resource(cls, wallet: MoneroWallet) -> None:
        if cls.is_wallet_rpc_resource(wallet):
            # TODO free specific wallet rpc resource
            cls.free_wallet_rpc_resources()

    @classmethod
    def create_wallet_ground_truth(
            cls,
            network_type: MoneroNetworkType,
            seed: str,
            start_height: int | None,
            restore_height: int | None
    ) -> MoneroWalletFull:
        # create directory for test wallets if it doesn't exist
        if not cls.check_test_wallets_dir_exists():
            cls.create_test_wallets_dir()

        # create ground truth wallet
        daemon_connection = MoneroRpcConnection(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)
        path = cls.TEST_WALLETS_DIR + "/gt_wallet_" + cls.current_timestamp_str()
        config = MoneroWalletConfig()
        config.path = path
        config.password = cls.WALLET_PASSWORD
        config.network_type = network_type
        config.seed = seed
        config.server = daemon_connection
        config.restore_height = restore_height

        if start_height is None:
            start_height = 0

        gt_wallet = MoneroWalletFull.create_wallet(config)
        cls.assert_equals(restore_height, gt_wallet.get_restore_height())
        gt_wallet.sync(start_height, WalletSyncPrinter())
        gt_wallet.start_syncing(cls.SYNC_PERIOD_IN_MS)

        # close the full wallet when the runtime is shutting down to release resources

        return gt_wallet

    @classmethod
    def test_invalid_address(cls, address: Optional[str], network_type: MoneroNetworkType) -> None:
        if address is None:
            return

        cls.assert_false(MoneroUtils.is_valid_address(address, network_type))

        try:
            MoneroUtils.validate_address(address, network_type)
            raise Exception("Should have thrown exception")
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_private_view_key(cls, private_view_key: Optional[str]):
        if private_view_key is None:
            return

        cls.assert_false(MoneroUtils.is_valid_private_view_key(private_view_key))

        try:
            MoneroUtils.validate_private_view_key(private_view_key)
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
    def test_invalid_private_spend_key(cls, private_spend_key: Optional[str]):
        if private_spend_key is None:
            return

        cls.assert_false(MoneroUtils.is_valid_private_spend_key(private_spend_key))

        try:
            MoneroUtils.validate_private_spend_key(private_spend_key)
            raise Exception("Should have thrown exception")
        except Exception as e:
            cls.assert_false(len(str(e)) == 0)

    @classmethod
    def test_invalid_public_spend_key(cls, public_spend_key: Optional[str]):
        if public_spend_key is None:
            return

        cls.assert_false(MoneroUtils.is_valid_public_spend_key(public_spend_key))
        try:
            MoneroUtils.validate_public_spend_key(public_spend_key)
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
        cls.assert_true(template.seed_height >= 0)
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
        if header.height == 0:
            cls.assert_true(header.timestamp == 0)
        else:
            cls.assert_true(header.timestamp > 0)
        cls.assert_not_none(header.prev_hash)
        cls.assert_not_none(header.nonce)
        if header.nonce == 0:
            # TODO (monero-project): why is header nonce 0?
            logger.warning(f"header nonce is 0 at height {header.height}")
        else:
            assert header.nonce is not None
            cls.assert_true(header.nonce > 0)
        cls.assert_is_none(header.pow_hash)  # never seen defined
        if is_full:
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
        # ctx = new TestContext()
        # ctx.has_json = false
        # ctx.is_pruned = true
        # ctx.is_full = false
        # ctx.is_confirmed = true
        # ctx.is_miner = true
        # ctx.from_get_tx_pool = true
        # cls.test_tx(miner_tx, ctx)

    @classmethod
    def test_tx(cls, tx: Optional[MoneroTx], ctx: Optional[TestContext]) -> None:
        raise NotImplementedError()

        # TODO: test block deep copy

    @classmethod
    def test_block(cls, block: Optional[MoneroBlock], ctx: TestContext):
        # test required fields
        assert block is not None, "Expected MoneroBlock, got None"
        assert block.miner_tx is not None, "Expected block miner tx"
        cls.test_miner_tx(block.miner_tx) # TODO: miner tx doesn't have as much stuff, can't call testTx?
        cls.test_block_header(block, ctx.header_is_full)

        if ctx.has_hex:
            assert block.hex is not None
            cls.assert_true(len(block.hex) > 1)
        else:
            cls.assert_is_none(block.hex)

        if ctx.has_txs:
            cls.assert_not_none(ctx.tx_context)
            for tx in block.txs:
                cls.assert_true(block == tx.block)
                cls.test_tx(tx, ctx.tx_context)

        else:
            cls.assert_is_none(ctx.tx_context)
            assert len(block.txs) == 0, "No txs expected"

    @classmethod
    def is_empty(cls, value: Union[str, list[Any], None]) -> bool:
        return value == ""

    @classmethod
    def test_update_check_result(cls, result: Union[Any, MoneroDaemonUpdateCheckResult]):
        assert result is not None
        cls.assert_true(isinstance(result, MoneroDaemonUpdateCheckResult))
        cls.assert_not_none(result.is_update_available)
        if result.is_update_available:
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
        if result.is_update_available:
            if path is not None:
                cls.assert_equals(path, result.download_path)
            else:
                cls.assert_not_none(result.download_path)
        else:
            cls.assert_is_none(result.download_path)

    @classmethod
    def test_unsigned_big_integer(cls, value: Any, bool_val: bool = False):
        if not isinstance(value, int):
            raise Exception(f"Value is not number: {value}")

        if value < 0:
            raise Exception("Value cannot be negative")

    @classmethod
    def test_account(cls, account: Optional[MoneroAccount], full: bool = True):
        # test account
        assert account is not None
        assert account.index is not None
        assert account.index >= 0
        assert account.primary_address is not None

        MoneroUtils.validate_address(account.primary_address, cls.NETWORK_TYPE)
        if full:
            cls.test_unsigned_big_integer(account.balance)
            cls.test_unsigned_big_integer(account.unlocked_balance)

            # if given, test subaddresses and that their balances add up to account balances
            if len(account.subaddresses) > 0:
                balance = 0
                unlocked_balance = 0
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
                    unlocked_balance += address_balance
                    msg1 = f"Subaddress balances {balance} != account {account.index} balance {account.balance}"
                    msg2 =  f"Subaddress unlocked balances {unlocked_balance} != account {account.index} unlocked balance {account.unlocked_balance}"
                    assert account.balance == balance, msg1
                    assert account.unlocked_balance == unlocked_balance, msg2
                    i += 1

        # tag must be undefined or non-empty
        tag = account.tag
        assert tag is None or len(tag) > 0

    @classmethod
    def test_subaddress(cls, subaddress: MoneroSubaddress, full: bool = True):
        assert subaddress.account_index is not None
        assert subaddress.index is not None
        if full:
            assert subaddress.balance is not None
            assert subaddress.num_unspent_outputs is not None
            assert subaddress.num_blocks_to_unlock is not None
            cls.test_unsigned_big_integer(subaddress.balance)
            cls.test_unsigned_big_integer(subaddress.unlocked_balance)
            cls.assert_true(subaddress.num_unspent_outputs >= 0)
            cls.assert_not_none(subaddress.is_used)
            if subaddress.balance > 0:
                cls.assert_true(subaddress.is_used)
            cls.assert_true(subaddress.num_blocks_to_unlock >= 0)

        cls.assert_true(subaddress.account_index >= 0)
        cls.assert_true(subaddress.index >= 0)
        cls.assert_not_none(subaddress.address)
        # TODO fix monero-cpp/monero_wallet_full.cpp to return boost::none on empty label
        #cls.assert_true(subaddress.label is None or subaddress.label != "")

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
            raise Exception("Number of subaddresses doesn't match")

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
        if from_connection:
            cls.assert_is_none(peer.last_seen_timestamp)
        else:
            assert peer.last_seen_timestamp is not None

            if peer.last_seen_timestamp < 0:
                logger.warning(f"Last seen timestamp is invalid: {peer.last_seen_timestamp}")
            cls.assert_true(peer.last_seen_timestamp >= 0)

        cls.assert_true(peer.pruning_seed is None or peer.pruning_seed >= 0)

    @classmethod
    def test_peer(cls, peer: Union[Any, MoneroPeer]):
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
    def test_sync_info(cls, sync_info: Union[Any, MoneroDaemonSyncInfo]):
        cls.assert_true(isinstance(sync_info, MoneroDaemonSyncInfo))
        assert sync_info.height is not None
        cls.assert_true(sync_info.height >= 0)

        for connection in sync_info.peers:
            cls.test_peer(connection)

        for span in sync_info.spans:
            cls.test_connection_span(span)

        assert sync_info.next_needed_pruning_seed is not None
        cls.assert_true(sync_info.next_needed_pruning_seed >= 0)
        cls.assert_is_none(sync_info.overview)
        cls.test_unsigned_big_integer(sync_info.credits, False) # 0 credits
        cls.assert_is_none(sync_info.top_block_hash)

    @classmethod
    def test_connection_span(cls, span: Union[MoneroConnectionSpan, Any]) -> None:
        raise NotImplementedError()

    @classmethod
    def test_hard_fork_info(cls, hard_fork_info: MoneroHardForkInfo):
        cls.assert_not_none(hard_fork_info.earliest_height)
        cls.assert_not_none(hard_fork_info.is_enabled)
        cls.assert_not_none(hard_fork_info.state)
        cls.assert_not_none(hard_fork_info.threshold)
        cls.assert_not_none(hard_fork_info.version)
        cls.assert_not_none(hard_fork_info.num_votes)
        cls.assert_not_none(hard_fork_info.voting)
        cls.assert_not_none(hard_fork_info.window)
        cls.test_unsigned_big_integer(hard_fork_info.credits, False) # 0 credits
        cls.assert_is_none(hard_fork_info.top_block_hash)

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
    def test_ban(cls, ban: Optional[MoneroBan]) -> None:
        assert ban is not None
        assert ban.host is not None
        assert ban.ip is not None
        assert ban.seconds is not None

    @classmethod
    def test_miner_tx_sum(cls, tx_sum: Optional[MoneroMinerTxSum]) -> None:
        assert tx_sum is not None
        cls.test_unsigned_big_integer(tx_sum.emission_sum, True)
        cls.test_unsigned_big_integer(tx_sum.fee_sum, True)

    @classmethod
    def get_unrelayed_tx(cls, wallet: MoneroWallet, account_idx: int):
        # TODO monero-project
        assert account_idx > 0, "Txs sent from/to same account are not properly synced from the pool"
        config = MoneroTxConfig()
        config.account_index = account_idx
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
        network_type: MoneroNetworkType | None = cls.get_daemon_rpc().get_info().network_type

        if network_type == MoneroNetworkType.STAGENET:
            # subaddress
            return "78Zq71rS1qK4CnGt8utvMdWhVNMJexGVEDM2XsSkBaGV9bDSnRFFhWrQTbmCACqzevE8vth9qhWfQ9SUENXXbLnmMVnBwgW"
        if network_type == MoneroNetworkType.TESTNET:
            # subaddress
            return "BhsbVvqW4Wajf4a76QW3hA2B3easR5QdNE5L8NwkY7RWXCrfSuaUwj1DDUsk3XiRGHBqqsK3NPvsATwcmNNPUQQ4SRR2b3V"
        if network_type == MoneroNetworkType.MAINNET:
            # subaddress
            return "87a1Yf47UqyQFCrMqqtxfvhJN9se3PgbmU7KUFWqhSu5aih6YsZYoxfjgyxAM1DztNNSdoYTZYn9xa3vHeJjoZqdAybnLzN"
        else:
            raise Exception("Invalid network type: " + str(network_type))

    @classmethod
    def get_and_test_txs(cls, wallet: MoneroWallet, a: Any, b: Any, c: bool) -> list[MoneroTxWallet]:
        raise NotImplementedError()

    @classmethod
    def get_random_transactions(
            cls,
            wallet: MoneroWallet,
            query: Optional[MoneroTxQuery] = None,
            min_txs: Optional[int] = None,
            max_txs: Optional[int] = None
    ) -> list[MoneroTxWallet]:
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

    @classmethod
    def get_confirmed_tx_hashes(cls, daemon: MoneroDaemon) -> list[str]:
        hashes: list[str] = []
        height: int = daemon.get_height()
        i = 0
        while i < 5 and height > 0:
            height -= 1
            block = daemon.get_block_by_height(height)
            for tx_hash in block.tx_hashes:
                hashes.append(tx_hash)
        return hashes

    @classmethod
    def test_rpc_connection(cls, connection: Optional[MoneroRpcConnection], uri: Optional[str], connected: bool = True) -> None:
        assert connection is not None
        assert uri is not None
        assert len(uri) > 0
        assert connection.uri == uri
        assert connection.check_connection() == connected
        assert connection.is_connected() == connected
        assert connection.is_online() == connected

    @classmethod
    def test_get_blocks_range(
        cls,
        daemon: MoneroDaemonRpc,
        start_height: Optional[int],
        end_height: Optional[int],
        chain_height: int,
        chunked: bool,
        block_ctx: BinaryBlockContext
    ) -> None:
        # fetch blocks by range
        real_start_height = 0 if start_height is None else start_height
        real_end_height = chain_height - 1 if end_height is None else end_height
        blocks = daemon.get_blocks_by_range_chunked(start_height, end_height) if chunked else daemon.get_blocks_by_range(start_height, end_height)
        cls.assert_equals(real_end_height - real_start_height + 1, len(blocks))

        # test each block
        for i, block in enumerate(blocks):
            cls.assert_equals(real_start_height + i, block.height)
            cls.test_block(block, block_ctx)

    @classmethod
    def assert_connection_equals(cls, c1: Optional[MoneroRpcConnection], c2: Optional[MoneroRpcConnection]) -> None:
        if c1 is None and c2 is None:
            return

        assert c1 is not None
        assert c2 is not None
        if not cls.IN_CONTAINER: # TODO
            assert c1.uri == c2.uri
        assert c1.username == c2.username
        assert c1.password == c2.password


TestUtils.load_config()
