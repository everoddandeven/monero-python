from typing import Any, override

from .fake_rpc_server import FakeRpcHandler, FakeRpcServer


class _Handler(FakeRpcHandler):
    """Answers the json rpc requests of a daemon poller, with a new block at each request."""

    @override
    def build_result(self, height: int) -> dict[str, Any]:
        return {
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


class FakeDaemonRpcServer(FakeRpcServer):
    """A daemon rpc server for unit tests, that needs no node: every request for the last block header gets a new block,
    so the poller of a `MoneroDaemonRpc` notifies its listeners at each poll.

    Use it as a context manager.
    """

    def __init__(self, first_height: int = 100, response_delay: float = 0.0) -> None:
        """Initialize a new FakeDaemonRpcServer.

        :param int first_height: height of the first block.
        :param float response_delay: seconds that the server takes to answer a request, to have requests in flight.
        """
        super().__init__(_Handler, first_height, response_delay)
