from typing import Optional
from typing_extensions import override
from monero import MoneroConnectionManagerListener, MoneroRpcConnection

class ConnectionList(list[MoneroRpcConnection]):

  def size(self) -> int:
    return len(self)

  def get(self, index: int) -> Optional[MoneroRpcConnection]:
    return self[index]

class ConnectionChangeCollector(MoneroConnectionManagerListener):

  changedConnections: ConnectionList

  def __init__(self) -> None:
    super().__init__()
    self.changedConnections = ConnectionList()

  @override
  def on_connection_changed(self, connection: MoneroRpcConnection) -> None:
    self.changedConnections.append(connection)
    
  
