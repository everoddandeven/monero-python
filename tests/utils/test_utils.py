import logging

from time import time
from typing import Optional
from abc import ABC
from os.path import exists as path_exists
from os import makedirs, getenv
from configparser import ConfigParser
from monero import (
    MoneroNetworkType, MoneroWalletFull, MoneroRpcConnection,
    MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc,
    MoneroWallet, MoneroRpcError,  MoneroWalletKeys
)

from .wallet_sync_printer import WalletSyncPrinter
from .wallet_tx_tracker import WalletTxTracker
from .gen_utils import GenUtils
from .daemon_utils import DaemonUtils
from .docker_wallet_rpc_manager import DockerWalletRpcManager

logger: logging.Logger = logging.getLogger("TestUtils")


class TestUtils(ABC):
    """Test utilities and constants."""

    __test__ = False
    _LOADED: bool = False
    """Indicates if test configuration is loaded."""

    IN_CONTAINER: bool = True
    """indicates if tests are running in docker container."""
    MIN_BLOCK_HEIGHT: int = 0
    """min blockchain height for tests."""
    WALLET_PORT_OFFSETS: dict[MoneroWalletRpc, int] = {}

    # objects cache
    _WALLET_FULL: Optional[MoneroWalletFull] = None
    """Default wallet full used for tests."""
    _WALLET_KEYS: Optional[MoneroWalletKeys] = None
    """Default wallet keys used for tests."""
    _WALLET_RPC: Optional[MoneroWalletRpc] = None
    """Default wallet rpc used for tests."""
    _WALLET_MINING: Optional[MoneroWalletFull] = None
    """Mining wallet used for funding test wallets."""
    _DAEMON_RPC: Optional[MoneroDaemonRpc] = None
    """Default daemon rpc used for tests."""
    _MINING_DAEMON: Optional[MoneroDaemonRpc] = None
    """Internal daemon used for mining."""
    _WALLET_RPC_2: Optional[MoneroWalletRpc] = None
    """Additional wallet rpc instance."""

    DAEMON_RPC_URI: str = ""
    """Monero daemon rpc uri."""
    CONTAINER_DAEMON_RPC_URI: str = ""
    """Monero daemon rpc endpoint configuration (change per your configuration)."""
    DAEMON_RPC_USERNAME: str = ""
    """Monero daemon rpc username."""
    DAEMON_RPC_PASSWORD: str = ""
    """Monero daemon rpc password."""
    TEST_NON_RELAYS: bool = True
    """Indicates if non-relays tests are enabled."""
    TEST_RELAYS: bool = True
    """Indicates if relays tests are enabled."""
    LITE_MODE: bool = False
    """Indicates if running tests in light mode."""
    TEST_NOTIFICATIONS: bool = True
    """Indicates if notifications tests are enabled."""
    TEST_RESETS: bool = True
    """Indicates if reset tests are enabled."""

    WALLET_TX_TRACKER: WalletTxTracker
    """Test wallet tx tracker."""

    # monero wallet rpc configuration (change per your configuration)
    WALLET_RPC_PORT_START: int = 18082
    """test wallet executables will bind to consecutive ports after these."""
    WALLET_RPC_ZMQ_ENABLED: bool = False
    """Indicates if test wallet rpc zmq is enabled."""
    WALLET_RPC_ZMQ_PORT_START: int = 58083
    WALLET_RPC_ZMQ_BIND_PORT_START: int = 48083  # TODO: zmq bind port necessary?
    WALLET_RPC_USERNAME: str = ""
    """Test wallet rpc username."""
    WALLET_RPC_PASSWORD: str = ""
    """Test wallet rpc password."""
    WALLET_RPC_ZMQ_DOMAIN: str = ""
    """Test wallet rpc zmq domain."""
    WALLET_RPC_DOMAIN: str = ""
    """Test wallet rpc domain."""
    WALLET_RPC_URI: str = ""
    """Test wallet rpc uri."""
    WALLET_RPC_ZMQ_URI: str = ""
    """Test wallet rpc zmq uri."""
    WALLET_RPC_ACCESS_CONTROL_ORIGINS: str = ""
    """cors access from web browser."""
    WALLET_FULL_TESTS_RUN: bool = False
    """Indicates if full tests run."""

    # test wallet config
    WALLET_NAME: str = ""
    """Test wallet name."""
    WALLET_PASSWORD: str = ""
    """Test wallet password."""
    TEST_WALLETS_DIR: str = ""
    """Directory containing wallets used in tests."""
    WALLET_FULL_PATH: str = ""
    """Test wallet full path."""
    # test wallet constants
    NETWORK_TYPE: MoneroNetworkType = MoneroNetworkType.MAINNET
    """Test network type."""
    REGTEST: bool = False
    """Indicates if running on fakechain."""
    LANGUAGE: str = ""
    """Test wallet language."""
    SEED: str = ""
    """Test wallet seed."""
    ADDRESS: str = ""
    """Test wallet primary address."""
    PRIVATE_VIEW_KEY: str = ""
    """Test wallet private view key."""
    PRIVATE_SPEND_KEY: str = ""
    """Test wallet private spend key."""
    PUBLIC_SPEND_KEY: str = ""
    """Test wallet public spend key."""
    PUBLIC_VIEW_KEY: str = ""
    """Test wallet public view key."""
    FIRST_RECEIVE_HEIGHT: int = 0
    """NOTE: this value must be the height of the wallet's first tx for tests."""
    SYNC_PERIOD_IN_MS: int = 5000
    """period between wallet syncs in milliseconds."""
    OFFLINE_SERVER_URI: str = "offline_server_uri"
    """dummy server uri to remain offline because wallet2 connects to default if not given."""
    AUTO_CONNECT_TIMEOUT_MS: int = 3000
    """Default connection timeout in milliseconds."""

    # mining wallet config
    MINING_WALLET_NAME: str = ""
    """Mining wallet name."""
    MINING_WALLET_PASSWORD: str = ""
    """Mining wallet password."""
    MINING_SEED: str = ""
    """Mining wallet seed."""
    MINING_ADDRESS: str = ""
    """Mining wallet primary address."""
    MINING_PRIVATE_VIEW_KEY: str = ""
    """Mining wallet private view key."""
    MINING_PRIVATE_SPEND_KEY: str = ""
    """Mining wallet private spend key."""
    MINING_PUBLIC_SPEND_KEY: str = ""
    """Mining wallet public spend key."""
    MINING_PUBLIC_VIEW_KEY: str = ""
    """Mining wallet public view key."""
    MINING_WALLET_FULL_PATH: str = ""
    """Mining wallet full path."""

    RPC_WALLET_MANAGER: DockerWalletRpcManager

    @classmethod
    def load_config(cls) -> None:
        """Load tests configuration from `tests/config/config.ini`."""
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
        cls.TEST_RELAYS = parser.getboolean('general', 'test_relays')
        cls.TEST_NOTIFICATIONS = parser.getboolean('general', 'test_notifications')
        cls.LITE_MODE = parser.getboolean('general', 'lite_mode')
        cls.TEST_RESETS = parser.getboolean('general', 'test_resets')
        cls.AUTO_CONNECT_TIMEOUT_MS = parser.getint('general', 'auto_connect_timeout_ms')
        cls.NETWORK_TYPE = DaemonUtils.parse_network_type(nettype_str)
        cls.REGTEST = DaemonUtils.is_regtest(nettype_str)

        if cls.REGTEST:
            cls.MIN_BLOCK_HEIGHT = 100 # minimum block height for regtest environment

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
        cls.WALLET_TX_TRACKER = WalletTxTracker(cls.get_daemon_rpc(), cls.SYNC_PERIOD_IN_MS, cls.MINING_ADDRESS)

        # create directory for test wallets if it doesn't exist
        cls.initialize_test_wallet_dir()

        cls._LOADED = True

    @classmethod
    def load(cls) -> None:
        """Load configuration and wallet rpc manager."""
        if cls._LOADED:
            return

        cls.load_config()
        cls.RPC_WALLET_MANAGER = DockerWalletRpcManager(
            cls.WALLET_RPC_DOMAIN,
            cls.WALLET_RPC_PORT_START,
            cls.get_daemon_rpc(),
            cls.WALLET_PASSWORD,
            cls.SYNC_PERIOD_IN_MS,
            cls.AUTO_CONNECT_TIMEOUT_MS
        )
        cls.RPC_WALLET_MANAGER.set_connection_credentials(cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD)

    @classmethod
    def get_network_type(cls) -> str:
        """Get test network type.

        :returns str: network type string.
        """
        return DaemonUtils.network_type_to_str(cls.NETWORK_TYPE)

    @classmethod
    def initialize_test_wallet_dir(cls) -> None:
        """Initialize test wallets directory."""
        GenUtils.create_dir_if_not_exists(cls.TEST_WALLETS_DIR)

    @classmethod
    def check_test_wallets_dir_exists(cls) -> bool:
        """Checks if tests wallets directory exists.

        :returns bool: `True` if test wallet directory already exists, `False` other.
        """
        return path_exists(cls.TEST_WALLETS_DIR)

    @classmethod
    def create_test_wallets_dir(cls) -> None:
        """Create test wallets directory."""
        makedirs(cls.TEST_WALLETS_DIR)

    @classmethod
    def get_random_wallet_path(cls) -> str:
        """Get random test wallet path.

        :returns str: random test wallet path.
        """
        return f"{cls.TEST_WALLETS_DIR}/test_wallet_{int(time() * 1000)}"

    @classmethod
    def get_daemon_rpc(cls) -> MoneroDaemonRpc:
        """Get test daemon rpc.

        :returns MoneroDaemonRpc: test daemon rpc instance.
        """

        if cls._DAEMON_RPC is None:
            cls._DAEMON_RPC = MoneroDaemonRpc(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)

        return cls._DAEMON_RPC

    @classmethod
    def get_mining_daemon_rpc_connection(cls) -> MoneroRpcConnection:
        """Get the rpc connection of the daemon used for internal mining.

        :returns MoneroRpcConnection: rpc connection to internal mining daemon.
        """
        return MoneroRpcConnection("http://127.0.0.1:18089", cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)

    @classmethod
    def get_mining_daemon(cls) -> MoneroDaemonRpc:
        """Get daemon used for mining.

        :returns MoneroDaemonRpc: internal mining daemon.
        """

        if cls._MINING_DAEMON is None:
            cls._MINING_DAEMON = MoneroDaemonRpc(cls.get_mining_daemon_rpc_connection())

        return cls._MINING_DAEMON

    @classmethod
    def get_daemon_rpc_connection(cls) -> MoneroRpcConnection:
        """Get test daemon rpc connection.

        :returns MoneroRpcConnection: new test daemon rpc connection instance.
        """
        return MoneroRpcConnection(cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD)

    @classmethod
    def get_wallet_keys_config(cls) -> MoneroWalletConfig:
        """Get test wallet keys configuration.

        :returns MoneroWalletConfig: new test wallet keys configuration.
        """
        config = MoneroWalletConfig()
        config.network_type = cls.NETWORK_TYPE
        config.seed = cls.SEED
        return config

    @classmethod
    def get_wallet_keys(cls) -> MoneroWalletKeys:
        """Get keys-only test wallet.

        :returns MoneroWalletKeys: keys-only test wallet.
        """
        if cls._WALLET_KEYS is None:
            config = cls.get_wallet_keys_config()
            cls._WALLET_KEYS = MoneroWalletKeys.create_wallet_from_seed(config)

        return cls._WALLET_KEYS

    @classmethod
    def get_wallet_full_config(cls, daemon_connection: MoneroRpcConnection) -> MoneroWalletConfig:
        """Get test wallet full configuration.

        :param MoneroRpcConnection daemon_connection: rpc daemon connection.
        :returns MoneroWalletConfig: full wallet test configuration.
        """
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
        """Get test wallet full.

        :returns MoneroWalletFull: full test wallet.
        """

        if cls._WALLET_FULL is None:
            # create wallet from seed if it doesn't exist
            if not MoneroWalletFull.wallet_exists(cls.WALLET_FULL_PATH):
                # create wallet with connection
                daemon_connection = MoneroRpcConnection(
                    cls.DAEMON_RPC_URI, cls.DAEMON_RPC_USERNAME, cls.DAEMON_RPC_PASSWORD
                )
                config = cls.get_wallet_full_config(daemon_connection)
                logger.debug("Creating full wallet...")
                cls._WALLET_FULL = MoneroWalletFull.create_wallet(config)
                logger.debug(f"Created full wallet at path '{cls.WALLET_FULL_PATH}'")
                assert cls.FIRST_RECEIVE_HEIGHT == cls._WALLET_FULL.get_restore_height()
                # TODO implement __eq__ method
                #assert daemon_connection == cls._WALLET_FULL.get_daemon_connection()

                # otherwise open existing wallet and update daemon connection
            else:
                logger.debug("Opening full wallet...")
                cls._WALLET_FULL = MoneroWalletFull.open_wallet(
                    cls.WALLET_FULL_PATH, cls.WALLET_PASSWORD, cls.NETWORK_TYPE
                )
                logger.debug(f"Opened full wallet at path '{cls.WALLET_FULL_PATH}")
                cls._WALLET_FULL.set_daemon_connection(cls.get_daemon_rpc_connection())

            # sync and save wallet
            if cls._WALLET_FULL.is_connected_to_daemon():
                logger.debug("Wallet full is connected to daemon")
                listener = WalletSyncPrinter(0.25)
                cls._WALLET_FULL.sync(listener)
                logger.debug("Synced full wallet")
                cls._WALLET_FULL.save()
                # start background synchronizing with sync period
                cls._WALLET_FULL.start_syncing(cls.SYNC_PERIOD_IN_MS)
                logger.debug("Started full wallet background synchronizing")
            else:
                logger.critical("Wallet full is not connected to daemon!")

        # ensure we're testing the right wallet
        assert cls.SEED == cls._WALLET_FULL.get_seed()
        assert cls.ADDRESS == cls._WALLET_FULL.get_primary_address()
        return cls._WALLET_FULL

    @classmethod
    def get_mining_wallet_config(cls) -> MoneroWalletConfig:
        """Get mining wallet configuration.

        :returns MoneroWalletConfig: mining wallet configuration.
        """
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
        """Get mining wallet.

        :returns MoneroWalletFull: mining wallet.
        """
        if cls._WALLET_MINING is not None:
            return cls._WALLET_MINING
        if not MoneroWalletFull.wallet_exists(cls.MINING_WALLET_FULL_PATH):
            logger.debug("Creating mining wallet...")
            wallet = MoneroWalletFull.create_wallet(cls.get_mining_wallet_config())
            logger.debug("Mining wallet created")
        else:
            logger.debug("Opening mining wallet...")
            wallet = MoneroWalletFull.open_wallet(cls.MINING_WALLET_FULL_PATH, cls.MINING_WALLET_PASSWORD, cls.NETWORK_TYPE)
            logger.debug("Loaded mining wallet")
            wallet.set_daemon_connection(cls.get_daemon_rpc_connection())

        assert wallet.is_connected_to_daemon(), "Mining wallet is not connected to daemon"
        listener = WalletSyncPrinter(0.25)
        wallet.sync(listener)
        wallet.save()
        wallet.start_syncing(cls.SYNC_PERIOD_IN_MS)

        assert cls.MINING_SEED == wallet.get_seed()
        assert cls.MINING_ADDRESS == wallet.get_primary_address()
        cls._WALLET_MINING = wallet
        return wallet

    @classmethod
    def get_wallet_rpc_connection(cls) -> MoneroRpcConnection:
        """Get test wallet rpc connection.

        :returns MoneroRpcConnection: test wallet rpc connection.
        """
        return MoneroRpcConnection(
            cls.WALLET_RPC_URI, cls.WALLET_RPC_USERNAME, cls.WALLET_RPC_PASSWORD,
            cls.WALLET_RPC_ZMQ_URI if cls.WALLET_RPC_ZMQ_ENABLED else ''
        )

    @classmethod
    def get_wallet_rpc(cls) -> MoneroWalletRpc:
        """Get rpc test wallet.

        :returns MoneroWalletRpc: rpc test wallet.
        """

        if cls._WALLET_RPC is None:

            # construct wallet rpc instance with daemon connection
            rpc = cls.get_wallet_rpc_connection()
            cls._WALLET_RPC = MoneroWalletRpc(rpc)

        # attempt to open test wallet
        try:
            cls._WALLET_RPC.open_wallet(cls.WALLET_NAME, cls.WALLET_PASSWORD)
        except MoneroRpcError as e:
            # -1 returned when wallet does not exist or fails to open e.g. it's already open by another application
            if e.code == -1:
                # create wallet
                config = MoneroWalletConfig()
                config.path = cls.WALLET_NAME
                config.password = cls.WALLET_PASSWORD
                config.seed = cls.SEED
                config.restore_height = cls.FIRST_RECEIVE_HEIGHT
                cls._WALLET_RPC.create_wallet(config)
            else:
                raise

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
        """Open a rpc wallet.

        :params MoneroWalletConfig | None c: rpc wallet configuration.
        :returns MoneroWalletRpc: opened rpc wallet.
        """
        return cls.RPC_WALLET_MANAGER.open_wallet(c, cls.IN_CONTAINER)

    @classmethod
    def create_wallet_rpc(cls, c: Optional[MoneroWalletConfig]) -> MoneroWalletRpc:
        """Create rpc wallet.

        :param MoneroWalletConfig | None c: rpc wallet configuration.
        :returns MoneroWalletRpc: created rpc wallet.
        """
        return cls.RPC_WALLET_MANAGER.create_wallet(c, cls.IN_CONTAINER)

    @classmethod
    def get_all_rpc_connections(cls) -> list[MoneroRpcConnection]:
        """Get all daemon and wallets rpc connections used in tests (ordered by connection uri).

        :returns list[MoneroDaemonRpc | MoneroWalletRpc]: rpc connections to a daemon or wallet rpc.
        """
        result: list[MoneroRpcConnection] = []
        # ordered by connection uri
        result.append(cls.get_daemon_rpc_connection())
        result.append(cls.get_wallet_rpc_connection())
        result.extend(cls.RPC_WALLET_MANAGER.get_rpc_connections())
        result.append(cls.get_mining_daemon_rpc_connection())
        for connection in result:
            connection.timeout = cls.AUTO_CONNECT_TIMEOUT_MS
        return result

    @classmethod
    def free_wallet_rpc_resources(cls, save: bool = False) -> None:
        """Free all docker wallet rpc resources.

        :param bool save: save wallets (default `False`).
        """
        cls.RPC_WALLET_MANAGER.clear(save)

    @classmethod
    def free_wallet_rpc_resource(cls, wallet: MoneroWallet, save: bool = False) -> None:
        """Free docker resource used by wallet.

        :param MoneroWallet wallet: wallet to free docker resource.
        :param bool save: save wallet before closing (default `False`).
        """
        if cls.RPC_WALLET_MANAGER.is_docker_instance(wallet):
            cls.RPC_WALLET_MANAGER.free_slot(wallet, save)

    @classmethod
    def create_wallet_ground_truth(
        cls,
        network_type: MoneroNetworkType,
        seed: str,
        start_height: int | None,
        restore_height: int | None
    ) -> MoneroWalletFull:
        """Create a full wallet to use in equality tests.

        :param MoneroNetworkType network_type: wallet network type.
        :param str seed: wallet seed.
        :param int | None start_height: wallet sync start height.
        :param int | None restore_height: wallet restore height.
        :returns MoneroWalletFull: ground-truth full wallet.
        """
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
            start_height = 0 if restore_height is None else restore_height

        gt_wallet = MoneroWalletFull.create_wallet(config)
        assert restore_height == gt_wallet.get_restore_height()
        gt_wallet.sync(start_height, WalletSyncPrinter(0.25))
        gt_wallet.start_syncing(cls.SYNC_PERIOD_IN_MS)

        # close the full wallet when the runtime is shutting down to release resources

        return gt_wallet

    @classmethod
    def clear_wallet_full_txs_pool(cls) -> None:
        """Clear full wallet txs pool and save."""
        wallet_full = cls.get_wallet_full()
        cls.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet_full)
        wallet_full.close(True)

    @classmethod
    def dispose(cls) -> None:
        """Dispose wallet resources."""
        # dispose mining wallet
        if cls._WALLET_MINING is not None:
            cls._WALLET_MINING.close(True)

        # dispose full wallet
        if cls._WALLET_FULL is not None:
            cls._WALLET_FULL.close(True)

        # dispose rpc wallet
        if cls._WALLET_RPC is not None:
            cls._WALLET_RPC.close(True)

        # dispose rpc wallet 2
        if cls._WALLET_RPC_2 is not None:
            cls._WALLET_RPC_2.close(True)


# load configuration
TestUtils.load()
