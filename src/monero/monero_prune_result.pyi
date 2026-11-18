from .serializable_struct import SerializableStruct


class MoneroPruneResult(SerializableStruct):
    """Models the result of pruning the blockchain."""

    is_pruned: bool | None
    """Indicates if blockchain is pruned."""
    pruning_seed: int | None
    """Blockheight at which pruning began."""

    @staticmethod
    def deserialize(json: str) -> MoneroPruneResult:
        """
        Deserialize a MoneroPruneResult from a JSON string.

        :param str json: MoneroPruneResult in JSON format.
        :returns MoneroPruneResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero prune result."""
        ...
