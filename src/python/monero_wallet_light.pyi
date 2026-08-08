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

        :param primary_address: The primary address of the wallet.
        :param private_view_key: The private view key of the wallet.
        :param rpc: The RPC connection to the Monero server.
        :return: True if the wallet exists, False otherwise.
        """
        ...

    @staticmethod
    @overload
    def wallet_exists(config: MoneroWalletConfig, rpc: MoneroRpcConnection) -> bool:
        """
        Check if a wallet exists on the server.

        :param config: The wallet configuration.
        :param rpc: The RPC connection to the Monero server.
        :return: True if the wallet exists, False otherwise.
        """
        ...

    @staticmethod
    def open_wallet(config: MoneroWalletConfig, rpc: MoneroRpcConnection) -> MoneroWalletLight:
        """
        Open an existing light wallet with the given configuration.

        :param config: The configuration for opening the wallet.
        :param rpc: The RPC connection to the Monero server.
        :return: An instance of MoneroWalletLight.
        """
        ...

    @staticmethod
    def create_wallet(config: MoneroWalletConfig, rpc: MoneroRpcConnection) -> MoneroWalletLight:
        """
        Create a new light wallet with the given configuration.

        :param config: The configuration for creating the wallet.
        :param rpc: The RPC connection to the Monero server.
        :return: An instance of MoneroWalletLight.
        """
        ...

    def get_rpc_connection(self) -> MoneroRpcConnection | None:
        """
        Get the wallet's RPC connection.

        :returns MoneroRpcConnection | None: the wallet's rpc connection.
        """
        ...
