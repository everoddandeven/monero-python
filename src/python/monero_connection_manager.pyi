import typing

from .monero_rpc_connection import MoneroRpcConnection
from .monero_connection_manager_listener import MoneroConnectionManagerListener
from .monero_connection_poll_type import MoneroConnectionPollType


class MoneroConnectionManager:
    """
    Manages a collection of prioritized connections to daemon or wallet RPC endpoints.
    """
    def __init__(self) -> None:
        """Initialize a Monero connection manager."""
        ...
    @typing.overload
    def add_connection(self, connection: MoneroRpcConnection) -> None:
        """
        Add a connection. The connection may have an elevated priority for this manager to use.
        
        :param MoneroRpcConnection connection: the connection to add
        """
        ...
    @typing.overload
    def add_connection(self, uri: str) -> None:
        """
        Add a connection URI.
        
        :param str uri: uri of the connection to add
        """
        ...
    def add_listener(self, listener: MoneroConnectionManagerListener) -> None:
        """
        Add a listener to receive notifications when the connection changes.
        
        :param MoneroConnectionManagerListener listener: the listener to add
        """
        ...
    def check_connection(self) -> None:
        """
        Check the current connection. If disconnected and auto switch enabled, switches to best available connection.
        """
        ...
    def check_connections(self) -> None:
        """
        Check all managed connections.
        """
        ...
    def clear(self) -> None:
        """
        Remove all connections.
        """
        ...
    def disconnect(self) -> None:
        """
        Disconnect from the current connection.
        """
        ...
    def get_auto_switch(self) -> bool:
        """
        Get if auto switch is enabled or disabled.
         
        :return bool: true if auto switch enabled, false otherwise
        """
        ...
    @typing.overload
    def get_best_available_connection(self, excluded_connections: set[MoneroRpcConnection]) -> MoneroRpcConnection:
        """
        Get the best available connection in order of priority then response time.

        :param set[MoneroRpcConnection] excluded_connections: connections to be excluded from consideration (optional)
        :return MoneroRpcConnection: the best available connection in order of priority then response time, null if no connections available
        """
        ...
    @typing.overload
    def get_best_available_connection(self, excluded_connection: MoneroRpcConnection) -> MoneroRpcConnection:
        """
        Get the best available connection in order of priority then response time.

        :param MoneroRpcConnection excluded_connection: connection to be excluded from consideration (optional)
        :return MoneroRpcConnection: the best available connection in order of priority then response time, null if no connections available
        """
        ...
    @typing.overload
    def get_best_available_connection(self) -> MoneroRpcConnection:
        """
        Get the best available connection in order of priority then response time.

        :return MoneroRpcConnection: the best available connection in order of priority then response time, null if no connections available
        """
        ...
    def get_connection(self) -> MoneroRpcConnection:
        """
        Get the current connection.
        """
        ...
    def get_connection_by_uri(self, uri: str) -> MoneroRpcConnection:
        """
        Get a connection by URI.
        
        :param str uri: URI of the connection to get
        :return MoneroRpcConnection: the connection with the URI or null if no connection with the URI exists
        """
        ...
    def get_connections(self) -> list[MoneroRpcConnection]:
        """
        Get all connections in order of current connection (if applicable), online status, priority, and name.

        :return list[MoneroRpcConnection]: List of RPC connections.
        """
        ...
    def get_listeners(self) -> list[MoneroConnectionManagerListener]:
        """
        Get all listeners.

        :return list[MoneroConnectionManagerListener]:
        """
        ...
    def get_peer_connections(self) -> list[MoneroRpcConnection]:
        """
        Collect connectable peers of the managed connections.
        
        :return list[MoneroRpcConnection]: connectable peers
        """
        ...
    def get_timeout(self) -> int:
        """
        Get the request timeout.
        
        :return int: the request timeout before a connection is considered offline
        """
        ...
    def has_connection(self, uri: str) -> bool:
        """
        Indicates if this manager has a connection with the given URI.
         
        :param str uri: URI of the connection to check
        :return bool: true if this manager has a connection with the given URI, false otherwise
        """
        ...
    def is_connected(self) -> bool:
        """
        Indicates if the connection manager is connected to a node.
         
        :return bool: true if the current connection is set, online, and not unauthenticated, null if unknown, false otherwise
        """
        ...
    def remove_connection(self, uri: str) -> None:
        """
        Remove a connection.
        
        :param str uri: uri of the connection to remove
        """
        ...
    def remove_listener(self, listener: MoneroConnectionManagerListener) -> None:
        """
        Remove a listener.
        
        :param MoneroConnectionManagerListener listener: the listener to remove
        """
        ...
    def remove_listeners(self) -> None:
        """
        Remove all listeners.
        """
        ...
    def reset(self) -> None:
        """
        Reset to default state.
        """
        ...
    def set_auto_switch(self, auto_switch: bool) -> None:
        """
        Automatically switch to the best available connection as connections are polled, based on priority, response time, and consistency.
         
        :param bool auto_switch: specifies if the connection should auto switch to a better connection
        """
        ...
    @typing.overload
    def set_connection(self, connection: MoneroRpcConnection | None) -> None:
        """
        Set the current connection.
        Replace connection if its URI was previously added. Otherwise add new connection.
        Notify if current connection changes.
        Does not check the connection.
        
        :param Optional[MoneroRpcConnection] connection: is the connection to make current
        """
        ...
    @typing.overload
    def set_connection(self, uri: str) -> None:
        """
        Set the current connection without changing the credentials.
        Add new connection if URI not previously added.
        Notify if current connection changes.
        Does not check the connection.
        
        :param str uri: identifies the connection to make current
        """
        ...
    def set_timeout(self, timeout_ms: int) -> None:
        """
        Set the maximum request time before a connection is considered offline.
         
        :param int timeout_ms: is the timeout before a connection is considered offline
        """
        ...
    def start_polling(self, period_ms: int | None = None, auto_switch: bool | None = None, timeout_ms: int | None = None, poll_type: MoneroConnectionPollType | None = None, excluded_connections: list[MoneroRpcConnection] | None = None) -> None:
        """
        Start polling connections.
         
        :param Optional[int] period_ms: poll period in milliseconds (default 20s)
        :param Optional[bool] auto_switch: specifies to automatically switch to the best connection (default true unless changed)
        :param Optional[int] timeout_ms: specifies the timeout to poll a single connection (default 5s unless changed)
        :param Optional[MoneroConnectionPollType] poll_type: one of PRIORITIZED (poll connections in order of priority until connected; default), CURRENT (poll current connection), or ALL (poll all connections)
        :param Optional[list[MoneroRpcConnection]] excluded_connections: connections excluded from being polled
        """
        ...
    def stop_polling(self) -> None:
        """
        Stop polling connections.
        """
        ...
