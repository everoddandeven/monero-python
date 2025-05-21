from .monero_request import MoneroRequest


class MoneroPathRequest(MoneroRequest):
    """
    Models a Monero RPC request.
    """
    def __init__(self) -> None:
        """Initialize a Monero RPC path request."""
        ...
