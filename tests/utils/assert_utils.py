import logging

from abc import ABC
from os import getenv
from typing import Any, Optional
from monero import (
    SerializableStruct, MoneroRpcConnection,
    MoneroSubaddress
)

logger: logging.Logger = logging.getLogger("AssertUtils")
var = getenv("IN_CONTAINER", "true").lower()
IN_CONTAINER: bool = var == "true" or var == "1"


class AssertUtils(ABC):

    @classmethod
    def assert_false(cls, expr: Any, message: str = "assertion failed"):
        assert expr is False, message

    @classmethod
    def assert_true(cls, expr: Any, message: str = "assertion failed"):
        assert expr is True, message

    @classmethod
    def assert_not_none(cls, expr: Any, message: str = "assertion failed"):
        assert expr is not None, message

    @classmethod
    def assert_is_none(cls, expr: Any, message: str = "assertion failed"):
        assert expr is None, message

    @classmethod
    def assert_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed"):
        if isinstance(expr1, SerializableStruct) and isinstance(expr2, SerializableStruct):
            str1 = expr1.serialize()
            str2 = expr2.serialize()
            assert str1 == str2, f"{message}: {str1} == {str2}"
        elif isinstance(expr1, MoneroRpcConnection) and isinstance(expr2, MoneroRpcConnection):
            cls.assert_connection_equals(expr1, expr2)
        else:
            assert expr1 == expr2, f"{message}: {expr1} == {expr2}"

    @classmethod
    def equals(cls, expr1: Any, expr2: Any) -> bool:
        try:
            cls.assert_equals(expr1, expr2)
            return True
        except Exception as e:
            logger.debug(str(e))
            return False

    @classmethod
    def assert_not_equals(cls, expr1: Any, expr2: Any, message: str = "assertion failed"):
        assert expr1 != expr2, f"{message}: {expr1} != {expr2}"

    @classmethod
    def assert_is(cls, expr: Any, what: Any, message: str = "assertion failed"):
        assert expr is what, f"{message}: {expr} is {what}"

    @classmethod
    def assert_not_supported(cls, error: Any) -> None:
        assert "not supported" in str(error), f"Expected not supported method: {error}"

    @classmethod
    def assert_connection_equals(cls, c1: Optional[MoneroRpcConnection], c2: Optional[MoneroRpcConnection]) -> None:
        if c1 is None and c2 is None:
            return

        assert c1 is not None
        assert c2 is not None
        if not IN_CONTAINER: # TODO
            assert c1.uri == c2.uri
        assert c1.username == c2.username
        assert c1.password == c2.password

    @classmethod
    def assert_subaddress_equal(cls, subaddress: Optional[MoneroSubaddress], other: Optional[MoneroSubaddress]):
        if subaddress is None and other is None:
            return
        assert not (subaddress is None or other is None)
        assert subaddress.address == other.address
        assert subaddress.account_index == other.account_index
        assert subaddress.balance == other.balance
        assert subaddress.index == other.index
        assert subaddress.is_used == other.is_used
        assert subaddress.label == other.label
        assert subaddress.num_blocks_to_unlock == other.num_blocks_to_unlock
        assert subaddress.num_unspent_outputs == other.num_unspent_outputs
        assert subaddress.unlocked_balance == other.unlocked_balance

    @classmethod
    def assert_subaddresses_equal(cls, subaddresses1: list[MoneroSubaddress], subaddresses2: list[MoneroSubaddress]):
        size1 = len(subaddresses1)
        size2 = len(subaddresses2)
        if size1 != size2:
            raise Exception("Number of subaddresses doesn't match")

        i = 0

        while i < size1:
            cls.assert_subaddress_equal(subaddresses1[i], subaddresses2[i])
            i += 1
