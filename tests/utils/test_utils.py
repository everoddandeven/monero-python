import logging

from typing import Optional
from abc import ABC
from os.path import exists as path_exists
from os import makedirs, getenv
from configparser import ConfigParser
from monero import (
    MoneroNetworkType, MoneroWalletFull, MoneroRpcConnection,
    MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc, MoneroWalletKeys,
    MoneroWallet, MoneroRpcError
)

from .wallet_sync_printer import WalletSyncPrinter
from .wallet_tx_tracker import WalletTxTracker
from .gen_utils import GenUtils
from .os_utils import OsUtils
from .string_utils import StringUtils
from .assert_utils import AssertUtils
from .daemon_utils import DaemonUtils

logger: logging.Logger = logging.getLogger("TestUtils")


class TestUtils(ABC):
    """Test utilities and constants"""

    __test__ = False
    _LOADED: bool = False
    """Indicates if test configuration is loaded"""

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
    """Monero daemon rpc uri"""
    CONTAINER_DAEMON_RPC_URI: str = ""
    """Monero daemon rpc endpoint configuration (change per your configuration)"""
    DAEMON_RPC_USERNAME: str = ""
    """Monero daemon rpc username"""
    DAEMON_RPC_PASSWORD: str = ""
    """Monero daemon rpc password"""
    TEST_NON_RELAYS: bool = True
    """Indicates if relays tests are enabled"""
    LITE_MODE: bool = False
    """Indicates if running tests in light mode"""
    TEST_NOTIFICATIONS: bool = True
    """Indicates if notifications tests are enabled"""

    WALLET_TX_TRACKER: WalletTxTracker
    """Test wallet tx tracker"""

    # monero wallet rpc configuration (change per your configuration)
    WALLET_RPC_PORT_START: int = 18082
    """test wallet executables will bind to consecutive ports after these"""
    WALLET_RPC_ZMQ_ENABLED: bool = False
    """Indicates if test wallet rpc zmq is enabled"""
    WALLET_RPC_ZMQ_PORT_START: int = 58083
    WALLET_RPC_ZMQ_BIND_PORT_START: int = 48083  # TODO: zmq bind port necessary?
    WALLET_RPC_USERNAME: str = ""
    """Test wallet rpc username"""
    WALLET_RPC_PASSWORD: str = ""
    """Test wallet rpc password"""
    WALLET_RPC_ZMQ_DOMAIN: str = ""
    """Test wallet rpc zmq domain"""
    WALLET_RPC_DOMAIN: str = ""
    """Test wallet rpc domain"""
    WALLET_RPC_URI: str = ""
    """Test wallet rpc uri"""
    WALLET_RPC_URI_2: str = ""
    WALLET_RPC_ZMQ_URI: str = ""
    """Test wallet rpc zmq uri"""
    WALLET_RPC_ACCESS_CONTROL_ORIGINS: str = ""
    """cors access from web browser"""

    # test wallet config
    WALLET_NAME: str = ""
    """Test wallet name"""
    WALLET_PASSWORD: str = ""
    """Test wallet password"""
    TEST_WALLETS_DIR: str = ""
    """Directory containing wallets used in tests"""
    WALLET_FULL_PATH: str = ""
    """Test wallet full path"""
    # test wallet constants
    NETWORK_TYPE: MoneroNetworkType = MoneroNetworkType.MAINNET
    """Test network type"""
    REGTEST: bool = False
    """Indicates if running on fakechain"""
    LANGUAGE: str = ""
    """Test wallet language"""
    SEED: str = ""
    """Test wallet seed"""
    ADDRESS: str = ""
    """Test wallet primary address"""
    PRIVATE_VIEW_KEY: str = ""
    """Test wallet private view key"""
    PRIVATE_SPEND_KEY: str = ""
    """Test wallet private spend key"""
    PUBLIC_SPEND_KEY: str = ""
    """Test wallet public spend key"""
    PUBLIC_VIEW_KEY: str = ""
    """Test wallet public view key"""
    FIRST_RECEIVE_HEIGHT: int = 0
    """NOTE: this value must be the height of the wallet's first tx for tests"""
    SYNC_PERIOD_IN_MS: int = 5000
    """period between wallet syncs in milliseconds"""
    OFFLINE_SERVER_URI: str = "offline_server_uri"
    """dummy server uri to remain offline because wallet2 connects to default if not given"""
    AUTO_CONNECT_TIMEOUT_MS: int = 3000
    """Default connection timeout in milliseconds"""

    # mining wallet config
    MINING_WALLET_NAME: str = ""
    """Mining wallet name"""
    MINING_WALLET_PASSWORD: str = ""
    """Mining wallet password"""
    MINING_SEED: str = ""
    """Mining wallet seed"""
    MINING_ADDRESS: str = ""
    """Mining wallet primary address"""
    MINING_PRIVATE_VIEW_KEY: str = ""
    """Mining wallet private view key"""
    MINING_PRIVATE_SPEND_KEY: str = ""
    """Mining wallet private spend key"""
    MINING_PUBLIC_SPEND_KEY: str = ""
    """Mining wallet public spend key"""
    MINING_PUBLIC_VIEW_KEY: str = ""
    """Mining wallet public view key"""
    MINING_WALLET_FULL_PATH: str = ""
    """Mining wallet full path"""

    @classmethod
    def load_config(cls) -> None:
        """
        Load tests configuration from `tests/config/config.ini`
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
        cls.NETWORK_TYPE = DaemonUtils.parse_network_type(nettype_str)
        cls.REGTEST = DaemonUtils.is_regtest(nettype_str)
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
        cls.MINING_WALLET_FULL_PATH = cls.TEST_WALLETS_DIR + "/" + cls.MINING_WALLET_NAME
        cls.MINING_WALLET_PASSWORD = parser.get('mining_wallet', 'password')
        cls.MINING_ADDRESS = parser.get('mining_wallet', 'address')
        cls.MINING_PRIVATE_VIEW_KEY = parser.get('mining_wallet', 'private_view_key')
        cls.MINING_PRIVATE_SPEND_KEY = parser.get('mining_wallet', 'private_spend_key')
        cls.MINING_PUBLIC_VIEW_KEY = parser.get('mining_wallet', 'public_view_key')
        cls.MINING_PUBLIC_SPEND_KEY = parser.get('mining_wallet', 'public_spend_key')
        cls.MINING_SEED = parser.get('mining_wallet', 'seed')

        # create directory for test wallets if it doesn't exist
        cls.initialize_test_wallet_dir()

        cls._LOADED = True

    @classmethod
    def get_network_type(cls) -> str:
        """Get test network type"""
        return DaemonUtils.network_type_to_str(cls.NETWORK_TYPE)

    @classmethod
    def initialize_test_wallet_dir(cls) -> None:
        """Initialize test wallets directory"""
        GenUtils.create_dir_if_not_exists(cls.TEST_WALLETS_DIR)

    @classmethod
    def check_test_wallets_dir_exists(cls) -> bool:
        """Checks if tests wallets directory exists"""
        return path_exists(cls.TEST_WALLETS_DIR)

    @classmethod
    def create_test_wallets_dir(cls) -> None:
        """Create test wallets directory"""
        makedirs(cls.TEST_WALLETS_DIR)

    @classmethod
    def get_daemon_rpc(cls) -> MoneroDaemonRpc:
        """Get test daemon rpc"""
        if OsUtils.is_windows():
            return None # type: ignore

        if cls._DAEMON_RPC is None:
            cls._DAEMON_RPC = MoneroDaemonRpc(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)

        return cls._DAEMON_RPC

    @classmethod
    def get_daemon_rpc_connection(cls) -> MoneroRpcConnection:
        """Get test daemon rpc connection"""
        return cls.get_daemon_rpc().get_rpc_connection()

    @classmethod
    def get_wallet_keys_config(cls) -> MoneroWalletConfig:
        """Get test wallet keys configuration"""
        config = MoneroWalletConfig()
        config.network_type = cls.NETWORK_TYPE
        config.seed = cls.SEED
        return config

    @classmethod
    def get_wallet_keys(cls) -> MoneroWalletKeys:
        """Get test wallet keys"""
        if cls._WALLET_KEYS is None:
            config = cls.get_wallet_keys_config()
            cls._WALLET_KEYS = MoneroWalletKeys.create_wallet_from_seed(config)

        return cls._WALLET_KEYS

    @classmethod
    def get_wallet_full_config(cls, daemon_connection: MoneroRpcConnection) -> MoneroWalletConfig:
        """Get test wallet full configuration"""
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
        """Get test wallet full"""
        if OsUtils.is_windows():
            return None # type: ignore

        if cls._WALLET_FULL is None:
            # create wallet from seed if it doesn't exist
            if not MoneroWalletFull.wallet_exists(cls.WALLET_FULL_PATH):
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
                cls._WALLET_FULL.set_daemon_connection(cls.get_daemon_rpc_connection())

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
    def get_mining_wallet_config(cls) -> MoneroWalletConfig:
        """Get mining wallet configuration"""
        connection = MoneroRpcConnection(
            cls.DAEMON_RPC_URI,
            cls.DAEMON_RPC_USERNAME,
            cls.DAEMON_RPC_PASSWORD
        )
        config = cls.get_wallet_full_config(connection)
        config.path = cls.MINING_WALLET_FULL_PATH
        config.password = cls.MINING_WALLET_PASSWORD
        config.seed = cls.MINING_SEED
        config.restore_height = 0
        return config

    @classmethod
    def get_mining_wallet(cls) -> MoneroWalletFull:
        """Get mining wallet"""
        if not MoneroWalletFull.wallet_exists(cls.MINING_WALLET_FULL_PATH):
            wallet = MoneroWalletFull.create_wallet(cls.get_mining_wallet_config())
        else:
            wallet = MoneroWalletFull.open_wallet(cls.MINING_WALLET_FULL_PATH, cls.MINING_WALLET_PASSWORD, cls.NETWORK_TYPE)
            wallet.set_daemon_connection(cls.get_daemon_rpc_connection())

        assert wallet.is_connected_to_daemon(), "Mining wallet is not connected to daemon"
        listener = WalletSyncPrinter()
        wallet.sync(listener)
        wallet.save()
        wallet.start_syncing(cls.SYNC_PERIOD_IN_MS)

        assert cls.MINING_SEED == wallet.get_seed()
        assert cls.MINING_ADDRESS == wallet.get_primary_address()
        return wallet

    @classmethod
    def get_wallet_rpc(cls) -> MoneroWalletRpc:
        """Get test wallet rpc"""
        if OsUtils.is_windows():
            return None # type: ignore

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
        """Open a rpc wallet"""
        config = c if c is not None else MoneroWalletConfig()

        # assign defaults
        if config.password is None:
            config.password = cls.WALLET_PASSWORD

        if config.server is None:
            config.server = cls.get_daemon_rpc().get_rpc_connection()
            if cls.IN_CONTAINER:
                config.server.uri = "http://node_2:18081"

        if cls._WALLET_RPC_2 is not None:
            raise Exception("Cannot open wallet: no rpc resources left")

        if cls._WALLET_RPC_2 is None:
            rpc = MoneroRpcConnection(
                cls.WALLET_RPC_URI_2, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD,
                cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else ''
            )
            cls._WALLET_RPC_2 = MoneroWalletRpc(rpc)

        # open wallet
        cls._WALLET_RPC_2.stop_syncing()
        cls._WALLET_RPC_2.open_wallet(config)
        cls._WALLET_RPC_2.set_daemon_connection(cls._WALLET_RPC_2.get_daemon_connection(), True, None)
        if cls._WALLET_RPC_2.is_connected_to_daemon():
            cls._WALLET_RPC_2.start_syncing(TestUtils.SYNC_PERIOD_IN_MS)

        return cls._WALLET_RPC_2

    @classmethod
    def create_wallet_rpc(cls, c: Optional[MoneroWalletConfig]) -> MoneroWalletRpc:
        """Create rpc wallet"""
        # assign defaults
        config = c if c is not None else MoneroWalletConfig()
        random = config.seed is None and config.primary_address is None

        if config.path is None:
            config.path = StringUtils.get_random_string()

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
            raise Exception("Cannot open wallet rpc: no resources left")

        if wallet_rpc is None:
            rpc = MoneroRpcConnection(
                cls.WALLET_RPC_URI_2, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD,
                cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else ''
            )
            wallet_rpc = MoneroWalletRpc(rpc)

        # create wallet
        wallet_rpc.stop_syncing()
        wallet_rpc.create_wallet(config)
        wallet_rpc.set_daemon_connection(wallet_rpc.get_daemon_connection(), True, None)
        if wallet_rpc.is_connected_to_daemon():
            wallet_rpc.start_syncing(TestUtils.SYNC_PERIOD_IN_MS)

        cls._WALLET_RPC_2 = wallet_rpc
        return cls._WALLET_RPC_2

    @classmethod
    def get_wallets(cls, wallet_type: str) -> list[MoneroWallet]:
        """Get all test wallets"""
        raise NotImplementedError()

    @classmethod
    def free_wallet_rpc_resources(cls) -> None:
        """Free all docker wallet rpc resources"""
        if cls._WALLET_RPC_2 is not None:
            try:
                cls._WALLET_RPC_2.close()
            except Exception as e:
                logger.debug(str(e))
                pass
        cls._WALLET_RPC_2 = None

    @classmethod
    def is_wallet_rpc_resource(cls, wallet: MoneroWallet) -> bool:
        """Indicates if wallet is using a docker rpc instance"""
        return wallet is cls._WALLET_RPC_2

    @classmethod
    def free_wallet_rpc_resource(cls, wallet: MoneroWallet) -> None:
        """Free docker resource used by wallet"""
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
        """Create a full wallet to use in equality tests"""
        # create directory for test wallets if it doesn't exist
        if not cls.check_test_wallets_dir_exists():
            cls.create_test_wallets_dir()

        # create ground truth wallet
        daemon_connection = MoneroRpcConnection(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)
        path = cls.TEST_WALLETS_DIR + "/gt_wallet_" + GenUtils.current_timestamp_str()
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
        AssertUtils.assert_equals(restore_height, gt_wallet.get_restore_height())
        gt_wallet.sync(start_height, WalletSyncPrinter())
        gt_wallet.start_syncing(cls.SYNC_PERIOD_IN_MS)

        # close the full wallet when the runtime is shutting down to release resources

        return gt_wallet

    @classmethod
    def get_external_wallet_address(cls) -> str:
        """Return an external wallet address"""
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

TestUtils.load_config()
