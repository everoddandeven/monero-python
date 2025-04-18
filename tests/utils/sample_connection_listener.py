
from typing_extensions import override
from monero import MoneroConnectionManagerListener, MoneroRpcConnection

class SampleConnectionListener(MoneroConnectionManagerListener):

  @override
  def on_connection_changed(self, connection: MoneroRpcConnection) -> None:
    print(f"Connection changed to: {connection if connection is not None else 'None'}")
    