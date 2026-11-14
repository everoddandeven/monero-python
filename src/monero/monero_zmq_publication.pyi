class MoneroZmqPublication:
    """Models a publication of a daemon's zmq publisher."""

    topic: str
    """Publication topic."""
    json: str
    """Publication content in JSON format."""

    def __init__(self) -> None:
        """Initialize a new publication."""
        ...
