from .serializable_struct import SerializableStruct
from .monero_key_image import MoneroKeyImage


class MoneroKeyImageExportResult(SerializableStruct):
    """Models results from exporting key images."""

    offset: int | None
    """
    Index of the first exported key image within the wallet's list of owned outputs.

    On an incremental export (`all=False`) the wallet skips outputs whose key
    images were already exported, so this offset tells the importing wallet where
    in its own output list the returned key images begin. Pass it back as the
    `offset` argument of `MoneroWallet.import_key_images()`.
    """
    key_images: list[MoneroKeyImage]
    """The exported key images, one per owned output starting at `offset`."""

    def __init__(self) -> None:
        """Initialize a Monero key image export result."""
        ...
