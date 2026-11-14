import json
import logging
import threading

from time import sleep

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, override

logger: logging.Logger = logging.getLogger("FakeDaemonRpcServer")


class _Handler(BaseHTTPRequestHandler):
    """Answers the json rpc requests of a daemon poller, with a new block at each request."""

    server: "FakeDaemonRpcServer"  # type: ignore[assignment]

    def do_POST(self) -> None:
        """Answer a request with the last block header, a block newer than the one of the previous request."""
        try:
            length: int = int(self.headers.get("Content-Length", "0"))
            body: dict[str, Any] = json.loads(self.rfile.read(length) or b"{}")
            height: int = self.server.next_height()
            if self.server.response_delay > 0:
                sleep(self.server.response_delay)
            response: dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": body.get("id", "0"),
                "result": {
                    "status": "OK",
                    "untrusted": False,
                    "block_header": {
                        "hash": f"{height:064x}",
                        "prev_hash": f"{height - 1:064x}",
                        "miner_tx_hash": f"{height + 1:064x}",
                        "height": height,
                        "major_version": 16,
                        "minor_version": 16,
                        "timestamp": 1700000000 + height,
                        "nonce": 1,
                        "orphan_status": False,
                        "depth": 0,
                        "difficulty": 5,
                        "cumulative_difficulty": 5 * height,
                        "reward": 600000000000,
                        "block_size": 100,
                        "block_weight": 100,
                        "num_txes": 0,
                        "long_term_weight": 100,
                        "pow_hash": ""
                    }
                }
            }
            data: bytes = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            # a request that is not json (the daemon connection probes the server too)
            logger.debug(f"Request not answered: {e}")
            self.send_error(404)

    @override
    def log_message(self, format: str, *args: Any) -> None:
        pass


class FakeDaemonRpcServer(ThreadingHTTPServer):
    """A daemon rpc server for unit tests, that needs no node: every request for the last block header gets a new block,
    so the poller of a `MoneroDaemonRpc` notifies its listeners at each poll.

    Use it as a context manager.
    """

    def __init__(self, first_height: int = 100, response_delay: float = 0.0) -> None:
        """Initialize a new FakeDaemonRpcServer.

        :param int first_height: height of the first block.
        :param float response_delay: seconds that the server takes to answer a request, to have requests in flight.
        """
        super().__init__(("127.0.0.1", 0), _Handler)
        self._first_height: int = first_height
        self._height: int = first_height
        self.response_delay: float = response_delay
        self._lock: threading.Lock = threading.Lock()
        self._thread: threading.Thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def uri(self) -> str:
        """Uri of the server.

        :returns str: uri to give to a `MoneroDaemonRpc`.
        """
        return f"http://127.0.0.1:{self.server_address[1]}"

    @property
    def num_requests(self) -> int:
        """Number of requests received so far.

        :returns int: number of requests received.
        """
        return self._height - self._first_height

    def next_height(self) -> int:
        """Get the height of the block of the next response.

        :returns int: new block height.
        """
        with self._lock:
            self._height += 1
            return self._height

    def __enter__(self) -> "FakeDaemonRpcServer":
        self._thread.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.shutdown()
        self.server_close()
        self._thread.join(timeout=5)
