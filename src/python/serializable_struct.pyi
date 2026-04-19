class SerializableStruct:
    """Base struct which can be serialized."""

    def __init__(self) -> None:
        """Initialize a new base struct."""
        ...

    def serialize(self) -> str:
        """
        Serializes the struct to a json string.

        :returns str: the struct serialized to a json string.
        """
        ...
