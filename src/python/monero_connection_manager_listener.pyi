from .monero_rpc_connection import MoneroRpcConnection


class MoneroConnectionManagerListener:
    """
    Default connection manager listener which takes no action on notifications.
    """
    def __init__(self) -> None:
        ...
    def on_connection_changed(self, connection: MoneroRpcConnection) -> None:
        """
        Notified on connection change events.
         
        :param connection: the connection manager's current connection
        """
        ...