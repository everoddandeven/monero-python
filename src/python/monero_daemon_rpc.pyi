import typing

from .monero_daemon import MoneroDaemon
from .monero_rpc_connection import MoneroRpcConnection


class MoneroDaemonRpc(MoneroDaemon):
    """Implements a `MoneroDaemon` using `monerod-rpc`_.

    .. _monerod-rpc: https://docs.getmonero.org/rpc-library/monerod-rpc/
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
    def __init__(self, uri: str, username: str = '', password: str = '', proxy_uri: str = '', zmq_uri: str = '', timeout: int = 20000) -> None:
        """
        Initialize a Monero daemon RPC.

        :param str uri: The daemon RPC uri.
        :param str username: Authentication username for daemon RPC.
        :param str password: Authentication password for daemon RPC.
        :param str proxy_uri: Connection proxy.
        :param str zmq_uri: RPC ZMQ uri.
        :param int timeout: Connection timeout in milliseconds (default `20000`).
        """
        ...

    def get_rpc_connection(self) -> MoneroRpcConnection:
        """
        Get the daemon's RPC connection.

        :returns MoneroRpcConnection: the daemon's rpc connection.
        """
        ...

    def is_connected(self) -> bool:
        """
        Indicates if the client is connected to the daemon via RPC.

        :returns bool: `True` if the client is connected to the daemon, `False` otherwise.
        """
        ...
