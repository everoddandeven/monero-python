class MoneroRpcError(RuntimeError):
    """
    Exception when interacting with the Monero daemon or wallet RPC API.
    """
    def __init__(self, code: int, aMessage: str) -> None:
        ...
    def get_code(self) -> int:
        """
        JSON-RPC error code.

        :return int: Error code.
        """
        ...
    def get_message(self) -> str:
        """
        JSON-RPC error message.

        :return str: Error message.
        """
        ...
