import typing

from .serializable_struct import SerializableStruct


class MoneroAuxiliaryPow(SerializableStruct):
    """Identifies an auxiliary chain's block by id and proof-of-work hash for merge mining."""

    id: str | None
    """The auxiliary chain id."""
    hash: str | None
    """The auxiliary block's proof-of-work hash."""

    @staticmethod
    def deserialize(json: str) -> MoneroAuxiliaryPow:
        """
        Deserialize a MoneroAuxiliaryPow from a JSON string.

        :param str json: MoneroAuxiliaryPow in JSON format.
        :returns MoneroAuxiliaryPow: deserialized instance.
        """
        ...

    @typing.overload
    def __init__(self) -> None:
        """Initialize an empty Monero auxiliary proof-of-work."""
        ...

    @typing.overload
    def __init__(self, id: str, hash: str) -> None:
        """
        Initialize a Monero auxiliary proof-of-work.

        :param str id: the auxiliary chain id.
        :param str hash: the auxiliary block's proof-of-work hash.
        """
        ...
