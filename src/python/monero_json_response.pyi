import typing


class MoneroJsonResponse:
    """
    Models a Monero JSON-RPC response.
    """
    id: str | None
    jsonrpc: str | None
    @staticmethod
    def deserialize(response_json: str) -> MoneroJsonResponse:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, response: MoneroJsonResponse) -> None:
        ...
    def get_result(self) -> typing.Any | None:
        ...
