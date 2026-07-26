from .serializable_struct import SerializableStruct


class MoneroGenerateBlocksResult(SerializableStruct):
    """Models the result of generating blocks."""

    block_hashes: list[str]
    """Generated block hashes."""
    height: int | None
    """New chain height."""
