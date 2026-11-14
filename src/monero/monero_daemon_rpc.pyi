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
    def __init__(self, uri: str, username: str = '', password: str = '', proxy_uri: str = '', zmq_uri: str = '', timeout_ms: int | None = None) -> None:
        """
        Initialize a Monero daemon RPC.

        :param str uri: The daemon RPC uri.
        :param str username: Authentication username for daemon RPC.
        :param str password: Authentication password for daemon RPC.
        :param str proxy_uri: Connection proxy.
        :param str zmq_uri: uri of the ZMQ publisher of the daemon (`--zmq-pub` of `monerod`), which makes the daemon poll when a block is published.
        :param int timeout_ms: Connection timeout in milliseconds (default 3 minutes).
        """
        ...

    def get_rpc_connection(self) -> MoneroRpcConnection:
        """
        Get the daemon's RPC connection.

        :returns MoneroRpcConnection: the daemon's rpc connection.
        """
        ...

    def set_poll_period_in_ms(self, period_ms: int) -> None:
        """
        Set the period between polls of the daemon for block notifications.

        With a ZMQ uri the daemon is also polled when `monerod` publishes a block, and a block that it did not publish is notified at most a period late.

        :param int period_ms: the poll period in milliseconds.
        """
        ...

    def is_connected(self) -> bool:
        """
        Indicates if the client is connected to the daemon via RPC.

        :returns bool: `True` if the client is connected to the daemon, `False` otherwise.
        """
        ...
