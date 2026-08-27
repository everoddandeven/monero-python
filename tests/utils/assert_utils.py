import logging

from abc import ABC
from typing import Any
from monero import SerializableStruct, MoneroRpcConnection

logger: logging.Logger = logging.getLogger("AssertUtils")


class AssertUtils(ABC):
    """Assert utilities."""

    @classmethod
    def assert_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed") -> None:
        """Check for objects equality.

        :param Any expr1: first object.
        :param Any expr2: second object.
        :param str message: failure message.
        """
        if isinstance(expr1, MoneroRpcConnection) and isinstance(expr2, MoneroRpcConnection):
            assert expr1.uri == expr2.uri
            assert expr1.username == expr2.username
            assert expr1.password == expr2.password
            assert expr1.proxy_uri == expr2.proxy_uri
            assert expr1.priority == expr2.priority
            assert expr1.timeout_ms == expr2.timeout_ms
        elif isinstance(expr1, SerializableStruct) and isinstance(expr2, SerializableStruct):
            str1: str = expr1.serialize()
            str2: str = expr2.serialize()
            assert str1 == str2, f"{message}: {str1} == {str2}"
        else:
            assert expr1 == expr2, f"{message}: {expr1} == {expr2}"

    @classmethod
    def assert_list_equals[T](cls, list_1: list[T] | None, list_2: list[T] | None, message: str = "lists doesn't equal") -> None:
        """Check for lists equality.

        :param list[T] | None list_1: first list to assert equality with `list_2`.
        :param list[T] | None list_2: second list to assert equality with `list_1`.
        :param str message: failure message.
        :raises AssertionError: raises if `list_1` is not equal to `list_2`.
        """
        if list_1 == list_2:
            return
        elif list_1 is None and list_2 is None:
            # TODO raise AssertError?
            return

        assert list_1 is not None, "list_1 is None"
        assert list_2 is not None, "list_2 is None"
        size1: int = len(list_1)
        size2: int = len(list_2)
        assert size1 == size2, f"Lists size mismatch: (list_1) {size1} != (list_2) {size2}"
        for i, elem1 in enumerate(list_1):
            elem2: T = list_2[i]
            cls.assert_equals(elem1, elem2, message)

    @classmethod
    def assert_serialization_integrity[T: SerializableStruct](cls, obj: T) -> T:
        """Serialize obj, deserialize it back through the model's own from_property_tree
        binding, and assert the result matches the original field for field.

        :param T obj: object to verity serialization integrity.
        :return T: new deserialized object.
        """
        cls = type(obj) # type: ignore
        json_str: str = obj.serialize()
        logger.debug(f"Serialized {cls.__name__}: {json_str}")
        restored: Any = cls.deserialize(json_str) # type: ignore
        AssertUtils.assert_equals(obj, restored)
        return restored # type: ignore

