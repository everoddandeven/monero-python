from .monero_zmq_publication import MoneroZmqPublication


class MoneroZmqSubscriber:
    """
    Receives the publications of a daemon's zmq publisher, can only be used by one thread at a time.

    Made by `MoneroRpcConnection.subscribe_zmq()`. It connects in the background and again if it loses the daemon, and a publication
    that is made while it is not connected is lost.
    """

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
