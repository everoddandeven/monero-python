import logging

from typing import Optional
from typing_extensions import override
from monero import (
    MoneroConnectionManager,
    MoneroConnectionManagerListener, MoneroRpcConnection
)

from .gen_utils import GenUtils

logger: logging.Logger = logging.getLogger("ConnectionChangeCollector")


class ConnectionChangeCollector(MoneroConnectionManagerListener):
    """Collects connection changes."""

    changed_connections: list[Optional[MoneroRpcConnection]]
    """Collected changed connections."""

    @property
    def num_changed_connections(self) -> int:
        """Number of changed connections collected."""
        return len(self.changed_connections)

    def __init__(self) -> None:
        """Initialize a new connection change collector."""
        super().__init__()
        self.changed_connections = []

    @override
    def on_connection_changed(self, connection: Optional[MoneroRpcConnection]) -> None:
        conn_str: str = connection.serialize() if connection is not None else 'None'
        logger.debug(f"Collecting connection change: {conn_str}")
        self.changed_connections.append(connection)

    def wait_for_change(
            self,
            expected_num_changes: int,
            interval_ms: int = 5000,
            custom_message: str = "Waiting for connection change"
        ) -> Optional[MoneroRpcConnection]:
        """
        Wait until a connection change occurs.

        :param int expected_num_changes: expected number of connection changes to wait for.
        :param int interval_ms: custom check interval in milliseconds (default 5000).
        :param str custom_message: custom message to show in debug during wait.
        :returns MoneroRpcConnection | None: changed connection.
        """

        last_num_changes: int = self.num_changed_connections
        while expected_num_changes > last_num_changes:
            logger.debug(f"{custom_message} (changes {last_num_changes}/{expected_num_changes})...")
            GenUtils.wait_for(interval_ms)
            last_num_changes = self.num_changed_connections

        logger.debug(f"Connection changed (connections {self.num_changed_connections}).")

    def wait_for_autoswitch(self, manager: MoneroConnectionManager, interval_ms: int) -> None:
        """
        Wait for connection auto switch.

        :param MoneroConnectionManager manager: connection manager to wait for auto switch.
        :param int interval_ms: custom check interval in milliseconds.
        """
        connected: bool = False
        # wait unitl manager has autoswitched connection
        while not connected:
            logger.debug("Waiting for autoswitch...")
            GenUtils.wait_for(interval_ms)
            connected = manager.is_connected() is not None

