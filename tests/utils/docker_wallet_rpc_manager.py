import logging

from monero import (
    MoneroWallet,
    MoneroDaemonRpc, MoneroRpcConnection,
    MoneroWalletRpc, MoneroWalletConfig
)

from .string_utils import StringUtils

logger: logging.Logger = logging.getLogger("DockerWalletRpcManager")


# TODO use some docker python package for managing instances dynamically
class DockerWalletRpcManager:
    """Manager for wallet rpc clients connected to monero-wallet-rpc docker instances."""

    MAX_SLOTS: int = 2
    """Maximum docker wallet rpc slots."""

    #region Private Attributes

    _domain: str
    """Rpc wallet domain."""
    _rpc_port_start: int
    """Rpc wallet port start."""
    _daemon: MoneroDaemonRpc
    """Daemon rpc."""
    _wallet_password: str
    """Rpc wallet password."""
    _wallets: dict[int, MoneroWalletRpc]
    """Rpc wallets connected to docker instances."""
    _rpc_user: str
    """Rpc user used to authenticate with monero-wallet-rpc."""
    _rpc_password: str
    """Rpc password used to authenticate with monero-wallet-rpc."""
    _sync_period_ms: int
    """Sync period in milliseconds."""
    _timeout_ms: int | None
    """Connection timeout in milliseconds."""

    #endregion

    #region Public Properties

    @property
    def used_slots(self) -> int:
        """Number of docker slots used."""
        return len(self._wallets)

    @property
    def free_slots(self) -> int:
        """Number of docker slots not used."""
        return self.MAX_SLOTS - self.used_slots

    @property
    def no_slot_left(self) -> bool:
        """Indicates if no docker slot is left."""
        return self.free_slots == 0

    @property
    def first_free_slot(self) -> int:
        """The first free docker slot index (-1 for none)."""
        slot_idxs: list[int] = list(self._wallets.keys())
        slot_range: list[int] = list(range(self.MAX_SLOTS))
        for slot_idx in slot_range:
            if slot_idx not in slot_idxs:
                return slot_idx
        return -1

    #endregion

    def __init__(
            self,
            domain: str,
            rpc_port_start: int,
            daemon: MoneroDaemonRpc,
            wallet_password: str,
            sync_period_ms: int,
            timeout_ms: int | None = None
            ) -> None:
        """Initialize a new docker wallet rpc manager.

        :param str domain: RPC domain.
        :param int rpc_port_start: RPC port start.
        :param MoneroDaemonRpc daemon: daemon to use as wallet connection.
        :param str wallet_password: password used by wallets.
        :param int sync_period_ms: wallet sync period in milliseconds.
        :param int timeout_ms: wallet connection timeout in milliseconds.
        """
        self._domain = domain
        self._rpc_port_start = rpc_port_start
        self._daemon = daemon
        self._wallet_password = wallet_password
        self._wallets = {}
        self._sync_period_ms = sync_period_ms
        self._timeout_ms = timeout_ms
        self._rpc_user = ''
        self._rpc_password = ''

    def set_connection_credentials(self, username: str, password: str) -> None:
        """Set wallet rpc global connection credentials.

        :param str username: connection auth username.
        :param str password: connection auth password.
        """
        self._rpc_user = username
        self._rpc_password = password

    def get_rpc_uri(self, slot: int) -> str:
        """Get wallet rpc uri associated to slot.

        :param int slot: docker slot index.
        :returns str: docker rpc uri.
        """
        assert slot >= 0
        assert slot < self.MAX_SLOTS
        # first docker instance is reserved to test wallet
        return f"{self._domain}:{self._rpc_port_start + slot + 1}"

    def setup_create_wallet_config(self, config: MoneroWalletConfig) -> MoneroWalletConfig:
        """Setup a `create` wallet configuration.

        :param MoneroWalletConfig config: configuration to setup for wallet creation.
        :returns MoneroWalletConfig: setup config.
        """
        random = config.seed is None and config.primary_address is None

        if config.path is None:
            # set random wallet path
            config.path = StringUtils.get_random_string()

        if config.restore_height is None and not random:
            # set restore height
            config.restore_height = 0

        return config

    def setup_wallet_config(self, c: MoneroWalletConfig | None, create: bool, in_container: bool) -> MoneroWalletConfig:
        """Setup a wallet configuration.

        :param MoneroWalletConfig | None c: wallet configuration to setup (optional).
        :param bool create: setup wallet creation configuration.
        :returns MoneroWalletConfig: setup configuration.
        """
        config = c if c is not None else MoneroWalletConfig()

        # assign defaults
        if config.password is None:
            config.password = self._wallet_password

        if config.server is None:
            config.server = MoneroRpcConnection(self._daemon.get_rpc_connection())
            if in_container:
                config.server.uri = "http://node_2:18081"

        if create:
            return self.setup_create_wallet_config(config)

        logger.debug(f"Setup docker wallet config: {config.serialize()}")

        return config

    def get_rpc_connection(self, slot: int) -> MoneroRpcConnection:
        """Get specific docker wallet rpc connection.

        :param int slot: docker slot to use.
        :returns MoneroRpcConnection: wallet rpc docker connection.
        """
        rpc_uri: str = self.get_rpc_uri(slot)
        return MoneroRpcConnection(rpc_uri, self._rpc_user, self._rpc_password, timeout_ms=self._timeout_ms)

    def get_rpc_connections(self) -> list[MoneroRpcConnection]:
        """Get all docker wallet rpc connections.

        :returns list[MoneroRpcConnection]: all wallet rpc docker connections.
        """
        connections: list[MoneroRpcConnection] = []
        for i in range(self.MAX_SLOTS):
            connections.append(self.get_rpc_connection(i))
        return connections

    def setup_wallet(self, c: MoneroWalletConfig | None, create: bool, in_container: bool) -> MoneroWalletRpc:
        """Setup a rpc wallet.

        :param MoneroWalletConfig | None c: wallet configuration.
        :param bool create: create the wallet.
        :returns MoneroWalletRpc: wallet rpc client.
        """
        if self.no_slot_left:
            raise Exception("Cannot open wallet: no rpc resources left")

        # setup open wallet configuration
        config: MoneroWalletConfig = self.setup_wallet_config(c, create, in_container)

        # get first free slot and build wallet rpc uri
        slot: int = self.first_free_slot
        # create client connected to monero-wallet-rpc process

        wallet: MoneroWalletRpc = MoneroWalletRpc(self.get_rpc_connection(slot))

        # open wallet
        wallet.stop_syncing()
        if create:
            wallet.create_wallet(config)
        else:
            wallet.open_wallet(config)
        wallet.set_daemon_connection(wallet.get_daemon_connection(), True, None)
        if wallet.is_connected_to_daemon():
            wallet.start_syncing(self._sync_period_ms)

        # cache wallet
        self._wallets[slot] = wallet

        return wallet

    def create_wallet(self, c: MoneroWalletConfig | None, in_container: bool) -> MoneroWalletRpc:
        """Create a rpc wallet.

        :param MoneroWalletConfig | None c: wallet configuration.
        :returns MoneroWalletRpc: wallet rpc client.
        """
        return self.setup_wallet(c, True, in_container)

    def open_wallet(self, c: MoneroWalletConfig | None, in_container: bool) -> MoneroWalletRpc:
        """Open a rpc wallet.

        :param MoneroWalletConfig | None: wallet configuration.
        :returns MoneroWalletRpc: wallet rpc client.
        """
        return self.setup_wallet(c, False, in_container)

    def is_docker_instance(self, wallet: MoneroWallet) -> bool:
        """Check if wallet is a managed docker instance.

        :param MoneroWallet wallet: wallet to check if it is a docker instance.
        :returns bool: `True` if `wallet` is a managed docker instance, `False` otherwise.
        """
        for w in self._wallets.values():
            if w == wallet:
                return True

        return False

    def free_slot(self, wallet: MoneroWallet, save: bool = False) -> None:
        """Free wallet rpc docker slot.

        :param MoneroWallet wallet: wallet to free docker resource.
        :param bool save: save the wallet before closing.
        """
        found: bool = False
        for w_idx in self._wallets.keys():
            w: MoneroWallet = self._wallets[w_idx]
            if w == wallet:
                found = True
                try:
                    wallet.close(save)
                except Exception as e:
                    e_msg: str = str(e)
                    if e_msg != "No wallet file":
                        logger.warning(e_msg)

                del self._wallets[w_idx]
                break

        assert found, "wallet is not rpc docker instance"

    def clear(self, save: bool = False) -> None:
        """Free all docker wallet rpc resources.

        :param bool save: save wallets (default `False`).
        """
        for wallet in self._wallets.values():
            if not wallet.is_closed():
                rpc_connection = wallet.get_rpc_connection()
                try:
                    wallet.close(save)
                except Exception as e:
                    e_str: str = str(e)
                    if "No wallet file" != e_str:
                        raise

                logger.debug(f"Closed docker wallet rpc: {rpc_connection.uri if rpc_connection is not None else 'None'}")

        self._wallets.clear()
