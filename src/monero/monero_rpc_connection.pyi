import typing

from .monero_zmq_subscriber import MoneroZmqSubscriber
from .serializable_struct import SerializableStruct


class MoneroRpcConnection(SerializableStruct):
    """Models a connection to a daemon."""

    priority: int
    """Connection priority."""
    proxy_uri: str | None
    """Connection proxy address."""
    zmq_uri: str | None
    """Uri of the ZMQ publisher of the daemon, `--zmq-pub` of `monerod`, e.g. `tcp://127.0.0.1:18083`."""
    timeout_ms: int | None
    """Connection timeout (milliseconds): `None` waits the default of 3 minutes."""
    ssl_verify: bool
    """Verify the TLS certificate and the hostname of https connections (default true)."""
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

    @typing.override
    def __eq__(self, other: object) -> bool:
        """
        Compare this connection to another like monero-java: by uri, username, password, proxy uri, zmq uri and ssl verify.
        The priority, the timeout and the state of the connections, like the response time, are not compared.

        :param object other: connection to compare against.

        :returns bool: `True` if `other` is a connection with the same config.
        """
        ...

    @typing.override
    def __repr__(self) -> str:
        """
        Represent this connection as its json, with the password hidden.

        :returns str: e.g. `MoneroRpcConnection({"uri":"http://localhost:28081","username":"rpc_user","password":"***",...})`.
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

    @staticmethod
    def deserialize(json: str) -> MoneroRpcConnection:
        """
        Deserialize a MoneroRpcConnection from a JSON string.

        :param str json: MoneroRpcConnection in JSON format.
        :returns MoneroRpcConnection: deserialized instance.
        """
        ...

    @typing.overload
    def __init__(
        self,
        uri: str = '',
        username: str = '',
        password: str = '',
        proxy_uri: str = '',
        zmq_uri: str = '',
        priority: int = 0,
        timeout_ms: int | None = None,
    ) -> None:
        """
        Initialize a RPC connection.

        :param str uri: URI string.
        :param str username: username used for authentication.
        :param str password: password used for authentication.
        :param str proxy_uri: proxy uri.
        :param str zmq_uri: uri of the ZMQ publisher of the daemon (`--zmq-pub` of `monerod`).
        :param int priority: priorioty of the connection.
        :param int|None timeout_ms: connection timeout in milliseconds.
        """
        ...

    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        """
        Initialize a RPC connection from other connection.

        :param MoneroRpcConnection rpc: RPC connection to copy.
        """
        ...

    def check_connection(self, timeout_ms: int | None = None) -> bool:
        """
        Check the connection and update online, authentication, and response time status.

        :param int|None timeout_ms: the maximum response time before considered offline.
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

        :returns bool | None: `True` if authenticated or no authentication required, `False` if not
            authenticated, or `None` if `check_connection()` has not been called.
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

    def send_json_request(self, method: str, parameters: object | None = None, timeout_ms: int | None = None) -> object | None:
        """
        Send a request to the JSON-RPC API.

        The request runs without the GIL, so the other threads run meanwhile: the requests of different connections run at once, the
        ones of a connection one at a time. The response is parsed as Python's `json` module parses it, so an object is a `dict`, an
        array a `list`, `null` is `None`, and an integer keeps its exact value.

        :param str method: is the method to request.
        :param Optional[object] parameters: are the request's input parameters, anything that `json.dumps()` serializes (default `None`).
        :param Optional[int] timeout_ms: request timeout in milliseconds.
        :returns object | None: the result of the response, `None` if it has none.
        :raises MoneroRpcError: if the response is an error, with its code and message.
        :raises MoneroError: if the server does not answer, or the response is not valid JSON.
        """
        ...

    def subscribe_zmq(self, topics: list[str]) -> MoneroZmqSubscriber:
        """
        Subscribe to the publications of the connection's zmq uri.

        :param list[str] topics: topics to receive, e.g. `json-minimal-chain_main`.
        :returns MoneroZmqSubscriber: the subscriber.
        :raises MoneroError: if the connection has no zmq uri, uses a proxy (zmq would connect directly), or the subscription fails.
        """
        ...

    def send_path_request(self, method: str, parameters: object | None = None, timeout_ms: int | None = None) -> object | None:
        """
        Send a RPC request to the given path and with the given parameters.

        E.g. `/get_transactions` with params. It runs without the GIL and parses the response as `send_json_request()` does.

        :param str method: is the url path of the request to invoke.
        :param Optional[object] parameters: are request parameters sent in the body, anything that `json.dumps()` serializes.
        :param Optional[int] timeout_ms: request timeout in milliseconds.
        :returns object | None: the response, `None` if it is a JSON-RPC one.
        :raises MoneroRpcError: if the response is an error, with its code and message.
        :raises MoneroError: if the server does not answer, or the response is not valid JSON.
        """
        ...

    def send_binary_request(self, method: str, parameters: object | None = None, timeout_ms: int | None = None) -> bytes | None:
        """
        Send a binary RPC request. It runs without the GIL, as `send_json_request()` does.

        :param str method: is the path of the binary RPC method to invoke.
        :param Optional[object] parameters: are the request parameters (default `None`).
        :param Optional[int] timeout_ms: request timeout in milliseconds.
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
        :param str password: password user for RPC authentication.
        """
        ...
