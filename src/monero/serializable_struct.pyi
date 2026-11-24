import typing

from abc import ABC


class SerializableStruct(ABC):
    """Base struct which can be serialized.

    Structs of the same type are equal if they serialize the same: the back references, like the block of a tx or the tx
    of an output, are not compared. Structs are mutable, so they are not hashable.
    """

    __hash__: typing.ClassVar[None]  # type: ignore[assignment]

    def serialize(self) -> str:
        """
        Serializes the struct to a json string.

        :returns str: the struct serialized to a json string.
        """
        ...

    @typing.override
    def __eq__(self, other: object) -> bool:
        """
        Compare this struct to another by their serialization.

        :param object other: struct to compare against.

        :returns bool: `True` if `other` has the same type and serializes the same.
        """
        ...

    @typing.override
    def __repr__(self) -> str:
        """
        Represent this struct as its type with its json.

        :returns str: e.g. `MoneroSubaddress({"accountIndex":0,"index":1})`.
        """
        ...
