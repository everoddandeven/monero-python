from .serializable_struct import SerializableStruct


class MoneroKeyImage(SerializableStruct):
    """
    Models a Monero key image.
    """
    hex: str | None
    signature: str | None
    @staticmethod
    def deserialize_key_images(key_images_json: str) -> list[MoneroKeyImage]:
        ...
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroKeyImage, tgt: MoneroKeyImage) -> MoneroKeyImage:
        ...
    def merge(self, _self: MoneroKeyImage, other: MoneroKeyImage) -> None:
        ...
