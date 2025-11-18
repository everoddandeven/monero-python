from typing import Optional
from typing_extensions import override
from monero import MoneroConnectionManagerListener, MoneroRpcConnection


class ConnectionList(list[Optional[MoneroRpcConnection]]):

    def size(self) -> int:
        return len(self)

    def get(self, index: int) -> Optional[MoneroRpcConnection]:
        return self[index]


class ConnectionChangeCollector(MoneroConnectionManagerListener):

    changed_connections: ConnectionList

    def __init__(self) -> None:
        super().__init__()
        self.changed_connections = ConnectionList()

    @override
    def on_connection_changed(self, connection: Optional[MoneroRpcConnection]) -> None:
        self.changed_connections.append(connection)
