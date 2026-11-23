import json
import threading

from time import sleep

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from typing_extensions import override


class FakeRawRpcHandler(BaseHTTPRequestHandler):
    """Answers a request with the body that the test set for its path, after the delay of the server."""

    server: "FakeRawRpcServer"  # type: ignore[assignment]

    def do_POST(self) -> None:
        """Answer a request with the response of its path, 404 if it has none."""
        length: int = int(self.headers.get("Content-Length", "0"))
        self.server.add_request(self.path, self.rfile.read(length))
        status, data = self.server.get_response(self.path)
        if self.server.response_delay > 0:
            sleep(self.server.response_delay)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        # the http client of monero keeps a connection open unless the response says "close" (see FakeRpcHandler)
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    @override
    def log_message(self, format: str, *args: Any) -> None:
        pass


class FakeRawRpcServer(ThreadingHTTPServer):
    """A rpc server for unit tests, that answers each path with the raw body that the test sets: a JSON-RPC response, a path
    response, invalid JSON or binary data. It keeps the requests that it receives.

    Use it as a context manager.
    """

    def __init__(self, response_delay: float = 0.0) -> None:
        """Initialize a new FakeRawRpcServer.

        :param float response_delay: seconds that the server takes to answer a request, to have requests in flight.
        """
        super().__init__(("127.0.0.1", 0), FakeRawRpcHandler)
        self.response_delay: float = response_delay
        self._lock: threading.Lock = threading.Lock()
        self._responses: dict[str, tuple[int, bytes]] = {}
        self._requests: list[tuple[str, bytes]] = []
        self._thread: threading.Thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def uri(self) -> str:
        """Uri of the server.

        :returns str: uri to give to the rpc connection.
        """
        return f"http://127.0.0.1:{self.server_address[1]}"

    @property
    def requests(self) -> list[tuple[str, bytes]]:
        """The requests received so far, as their path and their body.

        :returns list[tuple[str, bytes]]: the requests.
        """
        with self._lock:
            return list(self._requests)

    def set_response(self, path: str, body: object, status: int = 200) -> None:
        """Set the response of a path.

        :param str path: url path of the requests to answer, e.g. `/json_rpc`.
        :param object body: body of the response: bytes as they are, anything else as its JSON.
        :param int status: http status of the response.
        """
        data: bytes = body if isinstance(body, bytes) else json.dumps(body).encode()
        with self._lock:
            self._responses[path] = (status, data)

    def get_response(self, path: str) -> tuple[int, bytes]:
        """Get the response of a path.

        :param str path: url path of the request.
        :returns tuple[int, bytes]: http status and body of the response, 404 with no body if the path has none.
        """
        with self._lock:
            return self._responses.get(path, (404, b""))

    def add_request(self, path: str, body: bytes) -> None:
        """Take note of a request.

        :param str path: url path of the request.
        :param bytes body: body of the request.
        """
        with self._lock:
            self._requests.append((path, body))

    @override
    def __enter__(self) -> "FakeRawRpcServer":
        self._thread.start()
        return self

    @override
    def __exit__(self, *args: Any) -> None:
        self.shutdown()
        self.server_close()
        self._thread.join(timeout=5)
