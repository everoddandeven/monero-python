import typing

from .monero_request import MoneroRequest
from .monero_json_request_params import MoneroJsonRequestParams


class MoneroJsonRequest(MoneroRequest):
    """
    Models a Monero JSON-RPC request.
    """
    id: str | None
    params: MoneroJsonRequestParams | None
    version: str | None
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, request: MoneroJsonRequest) -> None:
        ...
    @typing.overload
    def __init__(self, method: str) -> None:
        ...
    @typing.overload
    def __init__(self, method: str, params: MoneroJsonRequestParams) -> None:
        ...
