from typing import Any, override

from .fake_rpc_server import FakeRpcHandler, FakeRpcServer


class _Handler(FakeRpcHandler):
    """Answers the json rpc requests of a wallet poller, with a new height at each request. Any method gets the same result: what
    the poller asks for and the result does not have, it takes as an error of the request and polls again."""

    @override
    def build_result(self, height: int) -> dict[str, Any]:
        return {"height": height, "balance": 0, "unlocked_balance": 0}


class FakeWalletRpcServer(FakeRpcServer):
    """A wallet rpc server for unit tests, that needs no wallet: every request gets a new height, so the poller of a `MoneroWalletRpc`
    is always asking the server.

    Use it as a context manager.
    """

    def __init__(self, first_height: int = 100, response_delay: float = 0.0) -> None:
        """Initialize a new FakeWalletRpcServer.

        :param int first_height: height of the first response.
        :param float response_delay: seconds that the server takes to answer a request, to have requests in flight.
        """
        super().__init__(_Handler, first_height, response_delay)
