from .serializable_struct import SerializableStruct


class MoneroGenerateBlocksResult(SerializableStruct):
    """Models the result of generating blocks."""

    block_hashes: list[str]
    """Generated block hashes."""
    height: int | None
    """New chain height."""

    @staticmethod
    def deserialize(json: str) -> MoneroGenerateBlocksResult:
        """
        Deserialize a MoneroGenerateBlocksResult from a JSON string.

        :param str json: MoneroGenerateBlocksResult in JSON format.
        :returns MoneroGenerateBlocksResult: deserialized instance.
        """
        ...
