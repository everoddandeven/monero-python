
from typing_extensions import override
from monero import MoneroConnectionManagerListener, MoneroRpcConnection

class SampleConnectionListener(MoneroConnectionManagerListener):

  def __init__(self) -> None:
    MoneroConnectionManagerListener.__init__(self)

  @override
  def on_connection_changed(self, connection: MoneroRpcConnection) -> None:
    print(f"Connection changed to: {connection if connection is not None else 'None'}")
    