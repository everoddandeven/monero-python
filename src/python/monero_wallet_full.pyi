from .monero_wallet import MoneroWallet
from .monero_wallet_config import MoneroWalletConfig
from .monero_network_type import MoneroNetworkType
from .monero_rpc_connection import MoneroRpcConnection


class MoneroWalletFull(MoneroWallet):
    """Monero wallet implementation which uses monero-project's wallet2."""

    @staticmethod
    def create_wallet(config: MoneroWalletConfig) -> MoneroWalletFull:
        """
        Create a new wallet with the given configuration.

        :param MoneroWalletConfig config: the wallet configuration.
        :returns MoneroWalletFull: reference to the wallet instance.
        """
        ...

    @staticmethod
    def get_seed_languages() -> list[str]:
        """
        Get a list of available languages for the wallet's seed.

        :returns list[str]: the available languages for the wallet's seed.
        """
        ...

    @staticmethod
    def open_wallet(path: str, password: str, nettype: MoneroNetworkType, regtest: bool = False) -> MoneroWalletFull:
        """
        Open an existing wallet from disk.

        :param str path: is the path to the wallet file to open.
        :param str password: is the password of the wallet file to open.
        :param MoneroNetworkType nettype: is the wallet's network type.
        :param bool regtest: indicates if wallet to open is a regtest wallet (optional).
        :returns MoneroWalletFull: reference to the wallet instance.
        """
        ...

    @staticmethod
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str, daemon_connection: MoneroRpcConnection = MoneroRpcConnection(), regtest: bool = False) -> MoneroWalletFull:
        """
        Open an in-memory wallet from existing data buffers.

        :param str password: is the password of the wallet file to open.
        :param MoneroNetworkType nettype: is the wallet's network type.
        :param str keys_data: contains the contents of the ".keys" file.
        :param str cache_data: contains the contents of the wallet cache file (no extension).
        :param MoneroRpcConnection daemon_connection: is connection information to a daemon (default = an unconnected wallet).
        :param bool regtest: indicates if wallet to open is a regtest wallet (optional).
        :returns MoneroWalletFull: reference to the wallet instance.
        """
        ...

    @staticmethod
    def wallet_exists(path: str) -> bool:
        """
        Indicates if a wallet exists at the given path.

        :param str path: is the path to check for a wallet.
        :returns bool: `True` if a wallet exists at the given path, `False` otherwise.
        """
        ...

    def get_cache_file_buffer(self) -> str:
        """
        Get wallet cache file without using filesystem.

        :returns str: Cache file buffer.
        """
        ...

    def get_keys_file_buffer(self, password: str, view_only: bool) -> str:
        """
        Get wallet keys file without using filesystem.

        :param str password: The wallet password.
        :param bool view_only: Get view-only keys.
        :returns str: Keys file buffer.
        """
        ...
