class MoneroRpcError(RuntimeError):
    """
    Exception when interacting with the Monero daemon or wallet RPC API.
    """

    code: int
    """JSON-RPC error code"""

    def __init__(self, message: str, code: int = -1) -> None:
        """
        Initialize a new monero rpc error

        :param str message: rpc error message
        :param int code: rpc error code
        """
        ...

