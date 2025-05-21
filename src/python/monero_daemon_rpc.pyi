import typing

from .monero_daemon_default import MoneroDaemonDefault
from .monero_rpc_connection import MoneroRpcConnection


class MoneroDaemonRpc(MoneroDaemonDefault):
    """
    Implements a Monero daemon using monerod.
    """
    @typing.overload
    def __init__(self) -> None:
        """Initialize a Monero daemon RPC."""
        ...
    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        """
        Initialize a Monero daemon RPC.
        
        :param MoneroRpcConnection rpc: A Monero RPC connection.
        """
        ...
    @typing.overload
    def __init__(self, uri: str, username: str = '', password: str = '') -> None:
        """
        Initialize a Monero daemon RPC.

        :param str uri: The daemon RPC uri.
        :param str username: Authentication username for daemon RPC.
        :param str password: Authentication password for daemon RPC.
        """
        ...
    def get_rpc_connection(self) -> MoneroRpcConnection:
        """
        Get the daemon's RPC connection.
        
        :return MoneroRpcConnection: the daemon's rpc connection
        """
        ...
    def is_connected(self) -> bool:
        """
        Indicates if the client is connected to the daemon via RPC.
        
        :return bool: true if the client is connected to the daemon, false otherwise
        """
        ...
