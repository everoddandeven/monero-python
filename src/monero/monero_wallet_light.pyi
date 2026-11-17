from typing import overload

from .monero_rpc_connection import MoneroRpcConnection
from .monero_wallet_config import MoneroWalletConfig
from .monero_wallet_keys import MoneroWalletKeys


class MoneroWalletLight(MoneroWalletKeys):
    """
    Implements a Monero wallet using `monero-lws`_.

    .. _monero-lws: https://github.com/vtnerd/monero-lws
    """

    @staticmethod
    @overload
    def wallet_exists(primary_address: str, private_view_key: str, rpc: MoneroRpcConnection) -> bool:
        """
        Check if a wallet exists on the server.

        :param str primary_address: The primary address of the wallet.
        :param str private_view_key: The private view key of the wallet.
        :param MoneroRpcConnection rpc: The RPC connection to the Monero server.
        :returns bool: `True` if the wallet exists, `False` otherwise.
        """
        ...

    @staticmethod
    @overload
    def wallet_exists(config: MoneroWalletConfig, rpc: MoneroRpcConnection) -> bool:
        """
        Check if a wallet exists on the server.

        :param MoneroWalletConfig config: The wallet configuration.
        :param MoneroRpcConnection rpc: The RPC connection to the Monero server.
        :returns bool: `True` if the wallet exists, `False` otherwise.
        """
        ...

    @staticmethod
    def open_wallet(config: MoneroWalletConfig, rpc: MoneroRpcConnection) -> MoneroWalletLight:
        """
        Open an existing light wallet with the given configuration.

        :param MoneroWalletConfig config: The configuration for opening the wallet.
        :param MoneroRpcConnection rpc: The RPC connection to the Monero server.
        :returns MoneroWalletLight: an instance of MoneroWalletLight.
        """
        ...

    @staticmethod
    def create_wallet(config: MoneroWalletConfig, rpc: MoneroRpcConnection) -> MoneroWalletLight:
        """
        Create a new light wallet with the given configuration.

        :param MoneroWalletConfig config: The configuration for creating the wallet.
        :param MoneroRpcConnection rpc: The RPC connection to the Monero server.
        :returns MoneroWalletLight: an instance of MoneroWalletLight.
        """
        ...

    def get_rpc_connection(self) -> MoneroRpcConnection | None:
        """
        Get the wallet's RPC connection.

        :returns MoneroRpcConnection | None: the wallet's rpc connection.
        """
        ...
