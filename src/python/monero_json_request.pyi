import typing

from .monero_request import MoneroRequest
from .monero_json_request_params import MoneroJsonRequestParams


class MoneroJsonRequest(MoneroRequest):
    """
    Models a Monero JSON-RPC request.
    """
    id: str | None
    """JSON-RPC request id."""
    params: MoneroJsonRequestParams | None
    """JSON-RPC request params."""
    version: str | None
    """JSON-RPC request version"""
    @typing.overload
    def __init__(self) -> None:
        """Initialize an empty Monero JSON-RPC request."""
        ...
    @typing.overload
    def __init__(self, request: MoneroJsonRequest) -> None:
        """
        Initialize a Monero JSON-RPC request.

        :param MoneroJsonRequest request: request to copy.
        """
        ...
    @typing.overload
    def __init__(self, method: str) -> None:
        """
        Initialize a Monero JSON-RPC request.

        :param str method: JSON-RPC method to invoke.
        """
        ...
    @typing.overload
    def __init__(self, method: str, params: MoneroJsonRequestParams) -> None:
        """
        Initialize a Monero JSON-RPC request.

        :param str method: JSON-RPC method to invoke.
        :param MoneroJsonRequestParams params: JSON-RPC request params. 
        """
        ...
