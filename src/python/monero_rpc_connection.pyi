import typing


class MoneroRpcConnection:
    """
    Models a connection to a daemon.
    """
    password: str | None
    """Connection authentication password."""
    priority: int
    """Connection priority."""
    proxy: str | None
    """Connection proxy address."""
    response_time: int | None
    """Connection response time."""
    timeout: int
    """Connection timeout (milliseconds)."""
    uri: str | None
    """Connection uri."""
    username: str | None
    """Connection authentication username."""
    zmq_uri: str | None
    @staticmethod
    def compare(c1: MoneroRpcConnection, c2: MoneroRpcConnection, current_connection: MoneroRpcConnection) -> int:
        """
        Compare RPC connections.

        :param MoneroRpcConnection c1: connection
        :param MoneroRpcConnection c2: other connection
        :param MoneroRpcConnection current_connection: current connection
        :return: 0, 1 or -1
        """
        ...
    @typing.overload
    def __init__(self, uri: str = '', username: str = '', password: str = '', zmq_uri: str = '', priority: int = 0, timeout: int = 0) -> None:
        """
        Initialize a RPC connection.

        :param str uri: URI string
        :param str username: username used for authentication
        :param str password: password used for authentication
        :param int priority: priorioty of the connection
        :param int timeout: connection timeout in milliseconds
        """
        ...
    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        """
        Initialize a RPC connection from other connection.

        :param MoneroRpcConnection rpc: RPC connection to copy.
        """
        ...
    def check_connection(self, timeout_ms: int = 2000) -> bool:
        """
        Check the connection and update online, authentication, and response time status.
        
        :param int timeout_ms: the maximum response time before considered offline
        :return bool: true if there is a change in status, false otherwise
        """
        ...
    def get_attribute(self, key: str) -> str:
        """
        Returns RPC connection attribute.

        :param str key: attribute key
        :return value: attribute value
        """
        ...
    def is_authenticated(self) -> bool:
        """
        Indicates if the connection is authenticated according to the last call to check_connection().

        Note: must call check_connection() manually unless using MoneroConnectionManager.
        
        :return bool: true if authenticated or no authentication, false if not authenticated, or null if check_connection() has not been called
        """
        ...
    def is_connected(self) -> bool:
        """
        Indicates if the connection is connected according to the last call to check_connection().
        
        Note: must call check_connection() manually unless using MoneroConnectionManager.

        :return bool: true or false to indicate if connected, or null if check_connection() has not been called
        """
        ...
    def is_i2p(self) -> bool:
        """
        Indicates if the connection is a I2P connection.
        """
        ...
    def is_onion(self) -> bool:
        """
        Indicates if the connection is a TOR connection.
        """
        ...
    def is_online(self) -> bool:
        """
        Indicates if the connection is online according to the last call to check_connection().
        
        Note: must call check_connection() manually unless using MoneroConnectionManager.
        
        :return bool: true or false to indicate if online, or null if check_connection() has not been called
        """
        ...
    def send_json_request(self, method: str, parameters: object | None = None) -> object:
        """
        Send a request to the JSON-RPC API.
         
        :param str method: is the method to request
        :param object parameters: are the request's input parameters
        :return response: the RPC API response as a map
        """
        ...
    def send_path_request(self, method: str, parameters: object | None = None) -> object:
        """
        Send a RPC request to the given path and with the given paramters.
        
        E.g. "/get_transactions" with params
        
        :param str path: is the url path of the request to invoke
        :param object parameters: are request parameters sent in the body
        :return response: the request's deserialized response
        """
        ...
    def send_binary_request(self, method: str, parameters: object | None = None) -> object:
        """
        Send a binary RPC request.
        
        :param str path: is the path of the binary RPC method to invoke
        :param object parameters: are the request parameters
        :return response: the request's deserialized binary response
        """
        ...
    def set_attribute(self, key: str, value: str) -> None:
        """
        Set RPC connection attribute.

        :param str key: key attribute
        :param str value: value attribute
        """
        ...
    def set_credentials(self, username: str, password: str) -> None:
        """
        Set RPC connection credentials.

        :param str username: username used for RPC authentication
        :param str password: passowrd user for RPC authentication
        """
        ...
