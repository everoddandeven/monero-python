import typing

from .monero_wallet import MoneroWallet
from .monero_wallet_config import MoneroWalletConfig
from .monero_rpc_connection import MoneroRpcConnection
from .monero_account import MoneroAccount


class MoneroWalletRpc(MoneroWallet):
    """
    Implements a Monero wallet using monero-wallet-rpc.
    """
    @typing.overload
    def __init__(self, rpc_connection: MoneroRpcConnection) -> None:
        """
        Initialize a Monero wallet RPC.

        :param MoneroRpcConnection rpc_connection: Monero RPC connection.
        """
        ...
    @typing.overload
    def __init__(self, uri: str = '', username: str = '', password: str = '') -> None:
        """
        Initialize a Monero wallet RPC.

        :param str uri: Connection uri.
        :param str username: Authentication connection username.
        :param str password: Authentication connection password.
        """
        ...
    def create_wallet(self, config: MoneroWalletConfig) -> MoneroWalletRpc:
        """
        Create and open a wallet on the monero-wallet-rpc server.

        :param config: configures the wallet to create.
        :return MoneroWalletConfig: this wallet client.
        """
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool, tag: str, skip_balances: bool) -> list[MoneroAccount]: # type: ignore
        """
        Get all accounts.

        :param include_subaddresses: specifies if subaddresses should be included
        :param skip_balances: skip balance check

        :return list[MoneroAccount]: all accounts within the wallet
        """
        ...
    def get_rpc_connection(self) -> MoneroRpcConnection | None:
        """
        Get the wallet's RPC connection.
        
        :return MoneroRpcConnection | None: the wallet's rpc connection
        """
        ...
    @typing.overload
    def open_wallet(self, config: MoneroWalletConfig) -> MoneroWalletRpc:
        """
        Open an existing wallet on the monero-wallet-rpc server.
        
        :param MoneroWalletConfig config: configures the wallet to open
        :return MoneroWalletRpc: this wallet client
        """
        ...
    @typing.overload
    def open_wallet(self, name: str, password: str) -> MoneroWalletRpc:
        """
        Open an existing wallet on the monero-wallet-rpc server.
         
        :param str name: is the name of the wallet file to open
        :param str password: is the wallet's password
        :return MoneroWalletRpc: this wallet client
        """
        ...
    def stop(self) -> None:
        """
        Save and close the current wallet and stop the RPC server.
        """
        ...
