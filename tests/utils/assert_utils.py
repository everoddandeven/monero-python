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
            str1 = expr1.serialize()
            str2 = expr2.serialize()
            assert str1 == str2, f"{message}: {str1} == {str2}"
        else:
            assert expr1 == expr2, f"{message}: {expr1} == {expr2}"

    @classmethod
    def assert_list_equals(cls, expr1: list[Any], expr2: list[Any], message: str = "lists doesn't equal") -> None:
        size1: int = len(expr1)
        size2: int = len(expr2)
        assert size1 == size2, f"{size1} = {size2}"
        for i, elem1 in enumerate(expr1):
            elem2: Any = expr2[i]
            cls.assert_equals(elem1, elem2, message)
