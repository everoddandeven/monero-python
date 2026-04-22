from abc import ABC


class SerializableStruct(ABC):
    """Base struct which can be serialized."""

    def serialize(self) -> str:
        """
        Serializes the struct to a json string.

        :returns str: the struct serialized to a json string.
        """
        ...
