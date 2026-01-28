from .serializable_struct import SerializableStruct


class MoneroKeyImage(SerializableStruct):
    """
    Models a Monero key image.
    """
    hex: str | None
    """The key image in hexadecimal format."""
    signature: str | None
    """The key image signature. Empty if not known."""
    @staticmethod
    def deserialize_key_images(key_images_json: str) -> list[MoneroKeyImage]:
        """
        Deserialize key images from a JSON string.

        :param str key_images_json: JSON string.
        :return list[MoneroKeyImage]: Deserialized key images.
        """
        ...
    def __init__(self) -> None:
        """Initialize a Monero key image."""
        ...
    def copy(self) -> MoneroKeyImage:
        ...
    def merge(self, other: MoneroKeyImage) -> None:
        ...
