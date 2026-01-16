import logging

from typing import Optional
from typing_extensions import override
from monero import MoneroConnectionManagerListener, MoneroRpcConnection

logger: logging.Logger = logging.getLogger("SampleConnectionListener")


class SampleConnectionListener(MoneroConnectionManagerListener):

    def __init__(self) -> None:
        MoneroConnectionManagerListener.__init__(self)

    @override
    def on_connection_changed(self, connection: Optional[MoneroRpcConnection]) -> None:
        logger.debug(f"Connection changed to: {connection.uri if connection is not None else 'None'}")
