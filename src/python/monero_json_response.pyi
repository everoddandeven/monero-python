import typing


class MoneroJsonResponse:
    """Models a Monero JSON-RPC response."""

    id: str | None
    """The response id."""
    jsonrpc: str | None
    """The JSON-RPC version."""

    @staticmethod
    def deserialize(response_json: str) -> MoneroJsonResponse:
        """
        Deserialize a Monero JSON-RPC response from a json string.

        :param str response_json: The JSON string.
        :returns MoneroJsonResponse: Deserialized JSON-RPC response.
        """
        ...

    @typing.overload
    def __init__(self) -> None:
        """Initialize a Monero JSON-RPC response."""
        ...

    @typing.overload
    def __init__(self, response: MoneroJsonResponse) -> None:
        """
        Initialize a Monero JSON-RPC response.

        :param MoneroJsonResponse response: A JSON-RPC response.
        """
        ...

    def get_result(self) -> typing.Any | None:
        """
        Get the deserialized result dictionary.

        :returns Any | None: The deserialized JSON-RPC response.
        """
        ...
