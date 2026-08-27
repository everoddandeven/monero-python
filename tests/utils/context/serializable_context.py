from __future__ import annotations

import json

from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T", bound="SerializableContext")


class SerializableContext(ABC):
    """Base class for test contexts that can be serialized to JSON.

    Mirrors monero-cpp's ``serializable_struct``: :meth:`serialize` emits a
    compact JSON string holding only the fields that are defined (i.e. not
    ``None``), while :meth:`deserialize` rebuilds an instance from such a string
    through the subclass' :meth:`from_dict`.
    """

    __test__ = False

    def serialize(self) -> str:
        """Serialize this context to a compact JSON string.

        :returns str: the context serialized to a JSON string.
        """
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Build the JSON object for this context, adding only defined fields.

        Analogous to monero-cpp's ``to_rapidjson_val``.

        :returns dict[str, Any]: the context as a JSON-serializable dict.
        """
        ...

    @classmethod
    def deserialize(cls: type[T], context_json: str) -> T:
        """Deserialize a context from a JSON string.

        :param str context_json: context in JSON format.
        :returns SerializableContext: deserialized instance.
        """
        ctx: T = cls()
        cls.from_dict(json.loads(context_json), ctx)
        return ctx

    @staticmethod
    @abstractmethod
    def from_dict(node: dict[str, Any], ctx: Any) -> None:
        """Populate ``ctx`` from a parsed JSON object.

        Analogous to monero-cpp's ``from_property_tree``.

        :param dict[str, Any] node: parsed JSON object.
        :param SerializableContext ctx: instance to populate.
        """
        ...

    @staticmethod
    def _put(root: dict[str, Any], key: str, value: Any) -> None:
        """Add ``key`` -> ``value`` to ``root`` only when ``value`` is defined.

        :param dict[str, Any] root: JSON object being built.
        :param str key: member name.
        :param Any value: member value, skipped when ``None``.
        """
        if value is not None:
            root[key] = value
