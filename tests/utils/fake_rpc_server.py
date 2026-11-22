import json
import logging
import threading

from time import sleep

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from typing_extensions import override

logger: logging.Logger = logging.getLogger("FakeRpcServer")


class FakeRpcHandler(BaseHTTPRequestHandler):
    """Answers the json rpc requests of a poller. A subclass gives the result of the response."""

    server: "FakeRpcServer"  # type: ignore[assignment]

    def build_result(self, height: int, method: str) -> dict[str, Any]:
        """Build the result of a response.

        :param int height: height of the response, a new one at each request.
        :param str method: json rpc method that was called.
        :returns dict[str, Any]: result of the json rpc response.
        """
        raise NotImplementedError

    def do_POST(self) -> None:
        """Answer a request with the result of the subclass."""
        try:
            length: int = int(self.headers.get("Content-Length", "0"))
            body: dict[str, Any] = json.loads(self.rfile.read(length) or b"{}")
            method: str = str(body.get("method", ""))
            height: int = self.server.next_height(method)
            if self.server.response_delay > 0:
                sleep(self.server.response_delay)
            response: dict[str, Any] = {"jsonrpc": "2.0", "id": body.get("id", "0"), "result": self.build_result(height, method)}
            data: bytes = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            # the handler answers in HTTP/1.0 and closes the connection after the response: the http client of monero keeps a connection
            # open unless the response says "close", and the next request could go to the socket that the server closed, which ends in
            # "no response"
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            # a request that is not json (the connection probes the server too)
            logger.debug(f"Request not answered: {e}")
            self.send_error(404)

    @override
    def log_message(self, format: str, *args: Any) -> None:
        pass


class FakeRpcServer(ThreadingHTTPServer):
    """A rpc server for unit tests, that needs no node or wallet: every request gets a new height, so the poller of what is tested
    has always something to notify.

    Use it as a context manager.
    """

    def __init__(self, handler: type[FakeRpcHandler], first_height: int = 100, response_delay: float = 0.0) -> None:
        """Initialize a new FakeRpcServer.

        :param type[FakeRpcHandler] handler: handler that answers the requests.
        :param int first_height: height of the first response.
        :param float response_delay: seconds that the server takes to answer a request, to have requests in flight.
        """
        super().__init__(("127.0.0.1", 0), handler)
        self._first_height: int = first_height
        self._height: int = first_height
        self.response_delay: float = response_delay
        self._lock: threading.Lock = threading.Lock()
        self._methods: list[str] = []
        self._thread: threading.Thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def uri(self) -> str:
        """Uri of the server.

        :returns str: uri to give to the rpc client.
        """
        return f"http://127.0.0.1:{self.server_address[1]}"

    @property
    def num_requests(self) -> int:
        """Number of requests received so far.

        :returns int: number of requests received.
        """
        return self._height - self._first_height

    @property
    def methods(self) -> list[str]:
        """Json rpc methods that were called so far, in the order of the requests.

        :returns list[str]: the methods.
        """
        with self._lock:
            return list(self._methods)

    def next_height(self, method: str = "") -> int:
        """Get the height of the next response, and take note of the method that asked for it.

        :param str method: json rpc method of the request.
        :returns int: new height.
        """
        with self._lock:
            self._height += 1
            self._methods.append(method)
            return self._height

    @override
    def __enter__(self) -> "FakeRpcServer":
        self._thread.start()
        return self

    @override
    def __exit__(self, *args: Any) -> None:
        self.shutdown()
        self.server_close()
        self._thread.join(timeout=5)
