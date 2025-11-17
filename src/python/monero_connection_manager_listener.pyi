from typing import Optional
from .monero_rpc_connection import MoneroRpcConnection


class MoneroConnectionManagerListener:
    """
    Default connection manager listener which takes no action on notifications.
    """
    def __init__(self) -> None:
        """Initialize a connection manager listener."""
        ...
    def on_connection_changed(self, connection: Optional[MoneroRpcConnection]) -> None:
        """
        Notified on connection change events.
         
        :param MoneroRpcConnection connection: the connection manager's current connection
        """
        ...