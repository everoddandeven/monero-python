from .serializable_struct import SerializableStruct
from .monero_key_image import MoneroKeyImage


class MoneroKeyImageExportResult(SerializableStruct):
    """Models results from exporting key images."""

    offset: int | None
    """Offset height."""
    key_images: list[MoneroKeyImage]
    """Exported key images."""

    def __init__(self) -> None:
        """Initialize a Monero key image export result."""
        ...
