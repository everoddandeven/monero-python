from .monero_zmq_publication import MoneroZmqPublication


class MoneroZmqSubscriber:
    """Receives the publications of a daemon's zmq publisher, can only be used by one thread at a time."""

    def is_connected(self) -> bool:
        """
        Indicates if connected to the publisher, which is updated while waiting for publications.

        :returns bool: `True` if connected.
        """
        ...

    def get_num_connections(self) -> int:
        """
        Get the number of times connected to the publisher, which is updated while waiting for publications.

        :returns int: the number of connections.
        """
        ...

    def wait_for_publication(self, timeout_ms: int) -> MoneroZmqPublication | None:
        """
        Wait for a publication.

        :param int timeout_ms: the maximum time to wait.
        :returns MoneroZmqPublication | None: the publication, or `None` if there is none before the timeout.
        """
        ...

    def discard_publications(self) -> None:
        """Discard the publications which are pending."""
        ...
