import typing

from .serializable_struct import SerializableStruct


class MoneroRpcConnection(SerializableStruct):
    """Models a connection to a daemon."""

    priority: int
    """Connection priority."""
    proxy_uri: str | None
    """Connection proxy address."""
    zmq_uri: str | None
    """ZMQ connection uri."""
    timeout: int
    """Connection timeout (milliseconds)."""
    uri: str | None
    """Connection uri."""

    @property
    def username(self) -> str | None:
        """Connection authentication username."""
        ...

    @property
    def password(self) -> str | None:
        """Connection authentication password."""
        ...

    @property
    def response_time(self) -> int | None:
        """Connection response time in milliseconds."""
        ...

    @staticmethod
    def before(c1: MoneroRpcConnection, c2: MoneroRpcConnection, current_connection: MoneroRpcConnection) -> bool:
        """
        Compare RPC connections.

        :param MoneroRpcConnection c1: connection.
        :param MoneroRpcConnection c2: other connection.
        :param MoneroRpcConnection current_connection: current connection.
        :returns bool: `True` if `c1` comes before `c2`, `False` otherwise.
        """
        ...

    @staticmethod
    def compare(p1: int, p2: int) -> bool:
        """
        Compare connection priorities.

        :param int p1: first priority to check.
        :param int p2: second priority to check.

        :returns bool: `True` if `p1` comes before `p2`, `False` otherwise.
        """
        ...

    @typing.overload
    def __init__(self, uri: str = '', username: str = '', password: str = '', proxy_uri: str = '', zmq_uri: str = '', priority: int = 0, timeout: int = 20000) -> None:
        """
        Initialize a RPC connection.

        :param str uri: URI string.
        :param str username: username used for authentication.
        :param str password: password used for authentication.
        :param str proxy_uri: proxy uri.
        :param str zmq_uri: ZMQ uri.
        :param int priority: priorioty of the connection (default `0`).
        :param int timeout: connection timeout in milliseconds (default `0`).
        """
        ...

    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        """
        Initialize a RPC connection from other connection.

        :param MoneroRpcConnection rpc: RPC connection to copy.
        """
        ...

    def check_connection(self, timeout_ms: int = 20000) -> bool:
        """
        Check the connection and update online, authentication, and response time status.

        :param int timeout_ms: the maximum response time before considered offline.
        :returns bool: `True` if there is a change in status, `False` otherwise.
        """
        ...

    def get_attribute(self, key: str) -> str:
        """
        Returns RPC connection attribute.

        :param str key: attribute key.
        :returns str: attribute value.
        """
        ...

    def is_authenticated(self) -> bool | None:
        """
        Indicates if the connection is authenticated according to the last call to `check_connection()`.

        Note: must call `check_connection()` manually.

        :returns bool | None: `True` if authenticated or no authentication required, `False` if not authenticated, or `None` if `check_connection()` has not been called.
        """
        ...

    def is_connected(self) -> bool | None:
        """
        Indicates if the connection is connected according to the last call to `check_connection()`.

        Note: must call `check_connection()` manually.

        :returns bool | None: `True` or `False` to indicate if connected, or `None` if `check_connection()` has not been called.
        """
        ...

    def is_i2p(self) -> bool:
        """
        Indicates if the connection is a I2P connection.

        :returns bool: `True` if connection is a I2P connection, `False` otherwise.
        """
        ...

    def is_onion(self) -> bool:
        """
        Indicates if the connection is a TOR connection.

        :returns bool: `True` if connection is a TOR connection, `False` otherwise.
        """
        ...

    def is_online(self) -> bool | None:
        """
        Indicates if the connection is online according to the last call to `check_connection()`.

        Note: must call `check_connection()` manually.

        :returns bool | None: `True` or `False` to indicate if online, or `None` if `check_connection()` has not been called.
        """
        ...

    def send_json_request(self, method: str, parameters: object | None = None) -> object | None:
        """
        Send a request to the JSON-RPC API.

        :param str method: is the method to request.
        :param Optional[object] parameters: are the request's input parameters (default `None`).
        :returns object | None: the RPC API response as a map.
        """
        ...

    def send_path_request(self, method: str, parameters: object | None = None) -> object | None:
        """
        Send a RPC request to the given path and with the given paramters.

        E.g. `/get_transactions` with params.

        :param str method: is the url path of the request to invoke.
        :param Optional[object] parameters: are request parameters sent in the body.
        :returns object | None: the request's deserialized response.
        """
        ...

    def send_binary_request(self, method: str, parameters: object | None = None) -> bytes | None:
        """
        Send a binary RPC request.

        :param str method: is the path of the binary RPC method to invoke.
        :param Optional[object] parameters: are the request parameters (default `None`).
        :returns bytes | None: the request's deserialized binary response.
        """
        ...

    def set_attribute(self, key: str, value: str) -> None:
        """
        Set RPC connection attribute.

        :param str key: key attribute.
        :param str value: value attribute.
        """
        ...

    def set_credentials(self, username: str, password: str) -> None:
        """
        Set RPC connection credentials.

        :param str username: username used for RPC authentication.
        :param str password: passowrd user for RPC authentication.
        """
        ...
