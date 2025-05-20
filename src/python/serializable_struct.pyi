class SerializableStruct:
    """
    Base struct which can be serialized.
    """
    def __init__(self) -> None:
        ...
    def serialize(self) -> str:
        """
        Serializes the struct to a json string.

        :return: the struct serialized to a json string
        """
        ...
