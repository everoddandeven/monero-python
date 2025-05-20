import typing

from .monero_daemon_default import MoneroDaemonDefault
from .monero_rpc_connection import MoneroRpcConnection


class MoneroDaemonRpc(MoneroDaemonDefault):
    """
    Implements a Monero daemon using monerod.
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        ...
    @typing.overload
    def __init__(self, uri: str, username: str = '', password: str = '') -> None:
        ...
    def get_rpc_connection(self) -> MoneroRpcConnection:
        """
        Get the daemon's RPC connection.
        
        :return: the daemon's rpc connection
        """
        ...
    def is_connected(self) -> bool:
        """
        Indicates if the client is connected to the daemon via RPC.
        
        :return: true if the client is connected to the daemon, false otherwise
        """
        ...
