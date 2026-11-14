import json
import pytest
import logging
import threading

from time import monotonic
from typing import Any, Callable

from monero import MoneroRpcConnection, MoneroConnectionType, MoneroError, MoneroRpcError, MoneroUtils, MoneroZmqPublication, MoneroZmqSubscriber
from utils import (
    TestUtils as Utils, RpcConnectionUtils,
    StringUtils, BaseTestClass, FakeRawRpcServer
)

logger: logging.Logger = logging.getLogger("TestMoneroRpcConnection")

RAW_TYPES: dict[str, Any] = {
    "empty_object": {},
    "empty_array": [],
    "empty_string": "",
    "null": None,
    "zero": 0,
    "true": True,
    "digits": "123",
    "true_string": "true",
    "float": 1.5,
    "past_int32": 5000000000000,
    "past_2_53": 123456789012345678,
    "uint64_max": 18446744073709551615,
    "nested": {"list": [], "dict": {}, "objects": [{"a": 1}, {}]},
}
"""Values of a response that a property tree cannot tell apart or keep exactly."""

REQUESTS: dict[str, tuple[str, str, object]] = {
    "json": ("get_info", "/json_rpc", {"jsonrpc": "2.0", "id": "0", "result": {"status": "OK"}}),
    "path": ("get_info", "/get_info", {"status": "OK"}),
    "binary": ("get_blocks_by_height.bin", "/get_blocks_by_height.bin", b"binary response"),
}
"""The method, the url path and a response of each kind of request."""


def get_sender(connection: MoneroRpcConnection, kind: str) -> Callable[..., object]:
    """Get the method of a connection that sends a kind of request.

    :param MoneroRpcConnection connection: connection to send with.
    :param str kind: `json`, `path` or `binary`.
    :returns Callable[..., object]: the method that sends the request.
    """
    senders: dict[str, Callable[..., object]] = {
        "json": connection.send_json_request, "path": connection.send_path_request, "binary": connection.send_binary_request
    }
    return senders[kind]


@pytest.mark.integration
class TestMoneroRpcConnection(BaseTestClass):
    """Rpc connection integration tests."""

    TIMEOUT_MS: int = Utils.AUTO_CONNECT_TIMEOUT_MS * 5
    """Rpc connection timeout in milliseconds."""

    # region Fixtures

    # Node rpc connection fixture
    @pytest.fixture(scope="class")
    @classmethod
    def node_connection(cls) -> MoneroRpcConnection:
        """Rpc connection test instance."""
        return MoneroRpcConnection(Utils.DAEMON_RPC_URI, Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD, timeout_ms=cls.TIMEOUT_MS)

    # Wallet rpc connection fixture
    @pytest.fixture(scope="class")
    @classmethod
    def wallet_connection(cls) -> MoneroRpcConnection:
        """Rpc connection test instance."""
        return MoneroRpcConnection(Utils.WALLET_RPC_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_RPC_PASSWORD, timeout_ms=cls.TIMEOUT_MS)

    #endregion

    #region Tests

    # Validate uri type
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_validate_uri(self) -> None:
        # test daemon uri
        connection: MoneroRpcConnection = MoneroRpcConnection(Utils.DAEMON_RPC_URI)
        assert not connection.is_onion()
        assert not connection.is_i2p()

        # test onion uri
        connection.uri = "http://moneronkvv2hu2anvcc5b4qd5y7strnc2ob6khqsrtikmhocyvjpdjyd.onion:18089"
        assert connection.is_onion()
        assert not connection.is_i2p()

        # test i2p uri
        connection.uri = "http://2rcznulrxqlygrk2qumpwkbonnh72fujukk5nmrcuuzrkl5rn5ta.b32.i2p:18081"
        assert not connection.is_onion()
        assert connection.is_i2p()

        # test empty uri
        connection.uri = ""
        assert not connection.is_onion()
        assert not connection.is_i2p()

        # test None uri
        connection.uri = None
        assert not connection.is_onion()
        assert not connection.is_i2p()

    # Test rpc connection json serialization
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_rpc_connection_serialization(self, node_connection: MoneroRpcConnection, wallet_connection: MoneroRpcConnection) -> None:
        # test node connection serialization
        connection_str: str = node_connection.serialize()
        assert '{"uri":"http://127.0.0.1:18081","username":"rpc_daemon_user","password":"abc123","priority":0,"timeoutMs":15000,"sslVerify":true}' == connection_str

        # node wallet connection serialization
        connection_str = wallet_connection.serialize()
        assert '{"uri":"http://127.0.0.1:18082","username":"rpc_user","password":"abc123","priority":0,"timeoutMs":15000,"sslVerify":true}' == connection_str

        # test empty connection
        connection: MoneroRpcConnection = MoneroRpcConnection()
        connection_str = connection.serialize()
        assert '{"priority":0,"sslVerify":true}' == connection.serialize()

        # test connection
        connection = MoneroRpcConnection("test_node:18081", "user", "abc123", "127.0.0.1:9050", "test_node:18084", 1, 1000)
        connection_str = connection.serialize()
        assert '{"uri":"test_node:18081","username":"user","password":"abc123","proxyUri":"127.0.0.1:9050","zmqUri":"test_node:18084","priority":1,"timeoutMs":1000,"sslVerify":true}' == connection_str

    # Can disable the verification of the TLS certificate
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_ssl_verify(self) -> None:
        # verified by default
        connection: MoneroRpcConnection = MoneroRpcConnection("https://node.example:18081")
        assert connection.ssl_verify is True

        # can be disabled, the setting is serialized and copied
        connection.ssl_verify = False
        assert connection.ssl_verify is False
        assert '"sslVerify":false' in connection.serialize()
        assert MoneroRpcConnection(connection).ssl_verify is False
        assert MoneroRpcConnection.deserialize(connection.serialize()).ssl_verify is False

        # connections that don't mention it stay verified
        assert MoneroRpcConnection.deserialize('{"uri":"https://node.example:18081"}').ssl_verify is True

    # Can copy a rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_connection_copy(self, node_connection: MoneroRpcConnection) -> None:
        # test copy
        copy: MoneroRpcConnection = MoneroRpcConnection(node_connection)
        assert copy.serialize() == node_connection.serialize()

    # Test monerod rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_node_rpc_connection(self, node_connection: MoneroRpcConnection) -> None:
        RpcConnectionUtils.test_rpc_connection(node_connection, Utils.DAEMON_RPC_URI, True, MoneroConnectionType.IPV4)

    # Test wallet rpc connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_wallet_rpc_connection(self, wallet_connection: MoneroRpcConnection) -> None:
        RpcConnectionUtils.test_rpc_connection(wallet_connection, Utils.WALLET_RPC_URI, True, MoneroConnectionType.IPV4)

    # Can subscribe to the zmq publisher of the daemon
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skipif(not Utils.DAEMON_RPC_ZMQ_PUB_URI, reason="daemon ZMQ publisher is not configured")
    def test_subscribe_zmq(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection(
            Utils.DAEMON_RPC_URI,
            Utils.DAEMON_RPC_USERNAME,
            Utils.DAEMON_RPC_PASSWORD,
            zmq_uri=Utils.DAEMON_RPC_ZMQ_PUB_URI
        )
        subscriber: MoneroZmqSubscriber = connection.subscribe_zmq(["json-minimal-chain_main"])

        # a publication is only there when a block was added meanwhile, and it is of the topic that was subscribed to
        publication: MoneroZmqPublication | None = subscriber.wait_for_publication(100)
        if publication is not None:
            assert publication.topic == "json-minimal-chain_main"
            assert publication.json

        subscriber.discard_publications()

    # Cannot subscribe to zmq without a zmq uri
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_subscribe_zmq_without_zmq_uri(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection("http://127.0.0.1:18081")
        with pytest.raises(MoneroError, match="no zmq uri"):
            connection.subscribe_zmq(["json-minimal-chain_main"])

    # Cannot subscribe to zmq through a proxy, zmq would connect directly
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_subscribe_zmq_through_proxy(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection(
            "http://127.0.0.1:18081", proxy_uri="127.0.0.1:9050", zmq_uri="tcp://127.0.0.1:18086"
        )
        with pytest.raises(MoneroError, match="proxy"):
            connection.subscribe_zmq(["json-minimal-chain_main"])

    # Test invalid connection
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_invalid_connection(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)
        RpcConnectionUtils.test_rpc_connection(connection, Utils.OFFLINE_SERVER_URI, False, MoneroConnectionType.INVALID)

    # Can set credentials
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_credentials(self) -> None:
        # create connection
        connection: MoneroRpcConnection = MoneroRpcConnection(Utils.DAEMON_RPC_URI)

        # test connection without credentials
        assert connection.username is None
        assert connection.password is None

        # test set credentials
        connection.set_credentials(Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)

        assert not connection.is_online(), "Expected not online"
        assert not connection.is_authenticated(), "Expected not authenticated"
        assert not connection.is_connected(), "Expected not connected"

        # test connection
        assert connection.username == Utils.DAEMON_RPC_USERNAME
        assert connection.password == Utils.DAEMON_RPC_PASSWORD

        assert connection.check_connection(), "Could not check connection"

        assert connection.is_online(), "Expected online after check"
        assert connection.is_authenticated(), "Not authenticated"
        assert connection.is_connected(), "Expected connected after check"

        # test empty credentials
        connection.set_credentials("", "")

        assert not connection.is_online(), "Expected not online"
        assert not connection.is_authenticated(), "Expected not authenticated"
        assert not connection.is_connected(), "Expected not connected"

        assert connection.username is None
        assert connection.password is None

    # Test invalid credentials
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_invalid_credentials(self) -> None:
        # create test connection
        connection: MoneroRpcConnection = MoneroRpcConnection(Utils.DAEMON_RPC_URI, Utils.DAEMON_RPC_USERNAME, Utils.DAEMON_RPC_PASSWORD)

        # username / password are read-only properties (set via set_credentials())
        with pytest.raises(AttributeError, match="object has no setter"):
            connection.username = "user" # type: ignore

        with pytest.raises(AttributeError, match="object has no setter"):
            connection.password = "abc123" # type: ignore

        # set invalid username
        with pytest.raises(RuntimeError, match="username cannot be empty because password is not empty"):
            connection.set_credentials("", "abc123")

        # set invalid password
        with pytest.raises(RuntimeError, match="password cannot be empty because username is not empty"):
            connection.set_credentials("user", "")

        # test connection
        assert connection.username == Utils.DAEMON_RPC_USERNAME
        assert connection.password == Utils.DAEMON_RPC_PASSWORD

        connection.set_credentials("user", "abc123")

        # test connection
        assert connection.username == "user"
        assert connection.password == "abc123"

        assert connection.check_connection()
        assert connection.is_online()
        assert connection.is_authenticated() is False
        assert connection.is_connected() is False

    # Can get and set arbitrary key/value attributes
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_attributes(self, node_connection: MoneroRpcConnection) -> None:
        # set attributes
        attr_range: range = range(100)

        for i in attr_range:
            assert node_connection.get_attribute(f"attr{i}") == ""

        attrs: dict[str, str] = {}
        for i in attr_range:
            key: str = f"attr{i}"
            val: str = StringUtils.get_random_string()
            attrs[key] = val
            node_connection.set_attribute(key, val)

        # test attributes
        for key in attrs:
            val = attrs[key]
            assert val == node_connection.get_attribute(key)

    # Test connection priorities
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_priority(self) -> None:
        for i in range(100):
            for j in range(100):
                expected: bool = (i == 0 and j != 0) or (i != 0 and j != 0 and i > j)
                assert MoneroRpcConnection.compare(i, j) is expected

    # Can send json request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_json_request(self, node_connection: MoneroRpcConnection) -> None:
        RpcConnectionUtils.setup_rpc_connection(node_connection)
        result: object = node_connection.send_json_request("get_version")
        assert result is not None
        logger.debug(f"JSON-RPC response {result}")

        # test invalid json rpc method
        with pytest.raises(MoneroRpcError) as exc_info:
            node_connection.send_json_request("invalid_method")
        assert str(exc_info.value) == "Method not found"
        assert exc_info.value.code == -32601

    # Can send binary request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_binary_request(self, node_connection: MoneroRpcConnection) -> None:
        RpcConnectionUtils.setup_rpc_connection(node_connection)
        parameters: dict[str, list[int]] = { "heights": list(range(100)) }
        bin_result: bytes | None = node_connection.send_binary_request("get_blocks_by_height.bin", parameters)
        assert bin_result is not None
        logger.debug(f"Binary response: {bin_result}")
        json_result: str = MoneroUtils.binary_blocks_to_json(bin_result)
        logger.debug(f"Deserialized binary response: {StringUtils.prettify(json_result)}")

        # test invalid binary method
        with pytest.raises(MoneroRpcError) as exc_info:
            node_connection.send_binary_request("invalid_method")
        assert exc_info.value.code == 404

    # Can send path request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_send_path_request(self, node_connection: MoneroRpcConnection) -> None:
        RpcConnectionUtils.setup_rpc_connection(node_connection)
        result: object = node_connection.send_path_request("get_height")
        assert result is not None
        logger.debug(f"Path response {result}")

        # test invalid path method
        with pytest.raises(MoneroRpcError) as exc_info:
            node_connection.send_path_request("invalid_method")
        assert exc_info.value.code == 404

    #endregion


@pytest.mark.unit
class TestMoneroRpcConnectionRequests(BaseTestClass):
    """Rpc connection request unit tests, on a local rpc server that answers with the raw bodies that the tests set."""

    # Can keep the types of the result of a JSON-RPC response
    def test_send_json_request_keeps_the_types(self) -> None:
        with FakeRawRpcServer() as server:
            server.set_response("/json_rpc", {"jsonrpc": "2.0", "id": "0", "result": RAW_TYPES})
            result: object = MoneroRpcConnection(server.uri).send_json_request("get_info")
        # json.dumps tells apart what == does not, as True and 1
        assert json.dumps(result, sort_keys=True) == json.dumps(RAW_TYPES, sort_keys=True)

    # Can keep the types of a path response
    def test_send_path_request_keeps_the_types(self) -> None:
        with FakeRawRpcServer() as server:
            server.set_response("/get_info", RAW_TYPES)
            result: object = MoneroRpcConnection(server.uri).send_path_request("get_info")
        assert json.dumps(result, sort_keys=True) == json.dumps(RAW_TYPES, sort_keys=True)

    # Can return no result for a JSON-RPC response without one
    def test_send_json_request_without_result(self) -> None:
        with FakeRawRpcServer() as server:
            server.set_response("/json_rpc", {"jsonrpc": "2.0", "id": "0"})
            assert MoneroRpcConnection(server.uri).send_json_request("get_info") is None

    # Can send the parameters of a request
    @pytest.mark.parametrize("kind", ["json", "path"])
    def test_send_request_parameters(self, kind: str) -> None:
        method, path, response = REQUESTS[kind]
        parameters: dict[str, Any] = {"heights": [1, 2, 3], "prune": True, "name": "", "none": None, "big": 18446744073709551615}
        with FakeRawRpcServer() as server:
            server.set_response(path, response)
            get_sender(MoneroRpcConnection(server.uri), kind)(method, parameters)
            request_path, body = server.requests[-1]
        assert request_path == path
        request: object = json.loads(body)
        if kind == "json":
            assert request == {"jsonrpc": "2.0", "id": "0", "method": method, "params": parameters}
        else:
            assert request == parameters

    # Can raise the error of a response with its code and message
    @pytest.mark.parametrize("kind", ["json", "path"])
    def test_send_request_raises_the_error_response(self, kind: str) -> None:
        method, path, _ = REQUESTS[kind]
        with FakeRawRpcServer() as server:
            server.set_response(path, {"jsonrpc": "2.0", "id": "0", "error": {"code": -32601, "message": "Method not found"}})
            with pytest.raises(MoneroRpcError) as exc_info:
                get_sender(MoneroRpcConnection(server.uri), kind)(method)
        assert str(exc_info.value) == "Method not found"
        assert exc_info.value.code == -32601

    # Can raise an error response without a message as monero-cpp does
    def test_send_json_request_raises_an_error_without_message(self) -> None:
        with FakeRawRpcServer() as server:
            connection: MoneroRpcConnection = MoneroRpcConnection(server.uri)

            # an empty message names the request
            server.set_response("/json_rpc", {"jsonrpc": "2.0", "id": "0", "error": {"code": -2, "message": ""}})
            with pytest.raises(MoneroRpcError) as exc_info:
                connection.send_json_request("get_info")
            assert str(exc_info.value) == "Received error response from RPC request with method 'get_info' to /json_rpc"
            assert exc_info.value.code == -2

            # no message at all is unknown
            server.set_response("/json_rpc", {"jsonrpc": "2.0", "id": "0", "error": {"code": -2}})
            with pytest.raises(MoneroRpcError) as exc_info:
                connection.send_json_request("get_info")
            assert str(exc_info.value) == "Unknown error"
            assert exc_info.value.code == -2

    # Can raise an error for a response that is not JSON
    @pytest.mark.parametrize("kind", ["json", "path"])
    def test_send_request_raises_on_invalid_json(self, kind: str) -> None:
        method, path, _ = REQUESTS[kind]
        with FakeRawRpcServer() as server:
            server.set_response(path, b'{"result": ')
            with pytest.raises(MoneroError) as exc_info:
                get_sender(MoneroRpcConnection(server.uri), kind)(method)
        assert str(exc_info.value) == "Invalid JSON"
        assert not isinstance(exc_info.value, MoneroRpcError)

    # Can apply the timeout of a request to the request
    @pytest.mark.parametrize("kind", ["json", "path", "binary"])
    def test_send_request_timeout(self, kind: str) -> None:
        method, path, response = REQUESTS[kind]
        with FakeRawRpcServer(response_delay=0.5) as server:
            server.set_response(path, response)
            send: Callable[..., object] = get_sender(MoneroRpcConnection(server.uri), kind)

            # a request that outlives its timeout raises the network error
            with pytest.raises(MoneroError, match=r"Network error: no response from .* \(timeout: 100ms\)"):
                send(method, timeout_ms=100)

            # the same request completes under a longer timeout: it waits without the gil, so the server in this process answers
            assert send(method, timeout_ms=5000) is not None

    # Can send requests from several threads at once, each with its own connection
    @pytest.mark.parametrize("kind", ["json", "path", "binary"])
    def test_send_requests_concurrently(self, kind: str) -> None:
        method, path, response = REQUESTS[kind]
        delay: float = 0.5
        num_threads: int = 3
        results: list[object] = []
        errors: list[Exception] = []

        def send(connection: MoneroRpcConnection) -> None:
            try:
                results.append(get_sender(connection, kind)(method))
            except Exception as e:
                errors.append(e)

        with FakeRawRpcServer(response_delay=delay) as server:
            server.set_response(path, response)
            threads: list[threading.Thread] = [
                threading.Thread(target=send, args=(MoneroRpcConnection(server.uri),)) for _ in range(num_threads)
            ]
            start: float = monotonic()
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            elapsed: float = monotonic() - start

        assert errors == []
        assert len(results) == num_threads
        # one at a time, they would take num_threads * delay
        assert elapsed < delay * (num_threads - 1), f"{num_threads} requests of {delay} s took {elapsed:.2f} s"
