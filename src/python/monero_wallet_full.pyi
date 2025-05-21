import typing

from .monero_wallet import MoneroWallet
from .monero_wallet_config import MoneroWalletConfig
from .monero_network_type import MoneroNetworkType
from .monero_rpc_connection import MoneroRpcConnection


class MoneroWalletFull(MoneroWallet):
    """
    Monero wallet implementation which uses monero-project's wallet2.
    """
    @staticmethod
    def create_wallet(config: MoneroWalletConfig) -> MoneroWalletFull:
        """
        Create a new wallet with the given configuration.

        :param MoneroWalletConfig config; The wallet configuration.
        :return MoneroWalletFull: A pointer to the wallet instance.
        """
        ...
    @staticmethod
    def get_seed_languages() -> list[str]:
        """
        Get a list of available languages for the wallet's seed.

        :return list[str]: The available languages for the wallet's seed.
        """
        ...
    @staticmethod
    def open_wallet(path: str, password: str, nettype: MoneroNetworkType) -> MoneroWalletFull:
        """
        Open an existing wallet from disk.

        :param str path: is the path to the wallet file to open.
        :param str password: is the password of the wallet file to open.
        :param MoneroNetworkType network_type: is the wallet's network type.
        :return MoneroWalletFull: a pointer to the wallet instance.
        """
        ...
    @staticmethod
    @typing.overload
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str) -> MoneroWalletFull:
        """
        Open an in-memory wallet from existing data buffers.

        :param string password: is the password of the wallet file to open.
        :param MoneroNetworkType nettype: is the wallet's network type.
        :param str keys_data: contains the contents of the ".keys" file.
        :param str cache_data: contains the contents of the wallet cache file (no extension).
        :return MoneroWalletFull: a pointer to the wallet instance.
        """
        ...
    @staticmethod
    @typing.overload
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str, daemon_connection: MoneroRpcConnection) -> MoneroWalletFull:
        """
        Open an in-memory wallet from existing data buffers.

        :param str password: is the password of the wallet file to open.
        :param MoneroNetworkType nettype: is the wallet's network type.
        :param str keys_data: contains the contents of the ".keys" file.
        :param str cache_data: contains the contents of the wallet cache file (no extension).
        :param MoneroRpcConnection daemon_connection: is connection information to a daemon (default = an unconnected wallet).
        :return MoneroWalletFull: a pointer to the wallet instance.
        """
        ...
    @staticmethod
    def wallet_exists(path: str) -> bool:
        """
        Indicates if a wallet exists at the given path.

        :param str path: is the path to check for a wallet.
        :return bool: true if a wallet exists at the given path, false otherwise.
        """
        ...
    def get_cache_file_buffer(self) -> str:
        """
        Get wallet cache file without using filesystem.
        
        :return str: Cache file buffer.
        """
        ...
    def get_keys_file_buffer(self, password: str, view_only: bool) -> str:
        """
        Get wallet keys file without using filesystem.
        
        :param str password: The wallet password.
        :param bool view_only: Get view-only keys.
        :return str: Keys file buffer.
        """
        ...
