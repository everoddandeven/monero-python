import pytest
import logging
import re
import time

from monero import GenUtils
from utils import BaseTestClass

logger: logging.Logger = logging.getLogger("TestGenUtils")

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


@pytest.mark.unit
class TestGenUtils(BaseTestClass):
    """Unit tests for GenUtils."""

    #region uuid / wait_for / bool_equals

    def test_get_uuid_format_and_uniqueness(self) -> None:
        uuid1: str = GenUtils.get_uuid()
        uuid2: str = GenUtils.get_uuid()
        logger.debug(f"get_uuid(): {uuid1}, {uuid2}")
        assert _UUID_RE.match(uuid1), f"not a UUID: {uuid1}"
        assert _UUID_RE.match(uuid2), f"not a UUID: {uuid2}"
        assert uuid1 != uuid2

    def test_wait_for_blocks_for_at_least_duration(self) -> None:
        start: float = time.monotonic()
        GenUtils.wait_for(50)
        elapsed_ms: float = (time.monotonic() - start) * 1000
        logger.debug(f"wait_for(50) actually took {elapsed_ms:.1f} ms")
        assert elapsed_ms >= 50

    def test_wait_for_zero_does_not_block(self) -> None:
        start: float = time.monotonic()
        GenUtils.wait_for(0)
        elapsed_ms: float = (time.monotonic() - start) * 1000
        assert elapsed_ms < 50

    def test_wait_for_negative_raises(self) -> None:
        with pytest.raises(TypeError):
            GenUtils.wait_for(-1) # type: ignore

    def test_bool_equals(self) -> None:
        assert GenUtils.bool_equals(True, True) is True
        assert GenUtils.bool_equals(False, False) is True
        assert GenUtils.bool_equals(True, False) is False
        assert GenUtils.bool_equals(False, True) is False
        # opt_val=None is documented to compare as False, even against val=False
        assert GenUtils.bool_equals(True, None) is False
        assert GenUtils.bool_equals(False, None) is False

    #endregion

    #region reconcile: equality and gap filling

    def test_reconcile_uint64_equal_returns_value(self) -> None:
        assert GenUtils.reconcile_uint64(5, 5) == 5
        assert GenUtils.reconcile_uint64(None, None) is None

    def test_reconcile_uint64_gap_fill(self) -> None:
        assert GenUtils.reconcile_uint64(None, 5) == 5
        assert GenUtils.reconcile_uint64(5, None) == 5

    def test_reconcile_uint64_resolve_defined_false_returns_none_on_gap(self) -> None:
        # resolve_defined=False overrides the default "fill the gap" behavior
        assert GenUtils.reconcile_uint64(None, 5, resolve_defined=False) is None
        assert GenUtils.reconcile_uint64(5, None, resolve_defined=False) is None

    def test_reconcile_bool_equal_and_gap_fill(self) -> None:
        assert GenUtils.reconcile_bool(True, True) is True
        assert GenUtils.reconcile_bool(None, True) is True
        assert GenUtils.reconcile_bool(False, None) is False

    def test_reconcile_string_equal_and_gap_fill(self) -> None:
        assert GenUtils.reconcile_string("x", "x") == "x"
        assert GenUtils.reconcile_string(None, "x") == "x"
        assert GenUtils.reconcile_string("x", None) == "x"

    def test_reconcile_string_list_equal_and_gap_fill(self) -> None:
        assert GenUtils.reconcile_string_list(["a", "b"], ["a", "b"]) == ["a", "b"]
        assert GenUtils.reconcile_string_list([], ["a", "b"]) == ["a", "b"]
        assert GenUtils.reconcile_string_list(["a", "b"], []) == ["a", "b"]

    #endregion

    #region reconcile: conflicts raise by design

    def test_reconcile_uint64_conflict_raises(self) -> None:
        with pytest.raises(RuntimeError, match="Cannot reconcile integrals"):
            GenUtils.reconcile_uint64(3, 7)

    def test_reconcile_bool_conflict_without_resolver_raises(self) -> None:
        with pytest.raises(RuntimeError, match="Cannot reconcile integrals"):
            GenUtils.reconcile_bool(True, False)

    def test_reconcile_string_conflict_raises(self) -> None:
        with pytest.raises(RuntimeError, match="Cannot reconcile strings"):
            GenUtils.reconcile_string("a", "b")

    def test_reconcile_string_list_conflict_raises(self) -> None:
        with pytest.raises(RuntimeError, match="Cannot reconcile vectors"):
            GenUtils.reconcile_string_list(["a"], ["b"])

    def test_reconcile_string_resolve_true_is_ignored(self) -> None:
        # unlike the bool/int overloads, the string overload accepts
        # resolve_true/resolve_max for signature symmetry but never reads them
        with pytest.raises(RuntimeError, match="Cannot reconcile strings"):
            GenUtils.reconcile_string("a", "b", resolve_true=True)

    #endregion

    #region reconcile: resolve_max picks the numeric extreme

    def test_reconcile_uint64_resolve_max_true_picks_greater(self) -> None:
        assert GenUtils.reconcile_uint64(3, 7, resolve_max=True) == 7
        assert GenUtils.reconcile_uint64(7, 3, resolve_max=True) == 7

    def test_reconcile_uint64_resolve_max_false_picks_lesser(self) -> None:
        assert GenUtils.reconcile_uint64(3, 7, resolve_max=False) == 3
        assert GenUtils.reconcile_uint64(7, 3, resolve_max=False) == 3

    #endregion

    #region reconcile values

    def test_reconcile_bool_resolve_true_prefers_the_true_operand(self) -> None:
        # val1=False, val2=True, resolve_true=True -> should prefer the
        # operand that IS true, i.e. val2
        result: bool | None = GenUtils.reconcile_bool(False, True, resolve_true=True)
        logger.debug(f"reconcile_bool(False, True, resolve_true=True) = {result}")
        assert result is True

    def test_reconcile_bool_resolve_true_false_prefers_the_false_operand(self) -> None:
        # val1=False, val2=True, resolve_true=False -> should prefer the
        # operand that IS false, i.e. val1
        result: bool | None = GenUtils.reconcile_bool(False, True, resolve_true=False)
        logger.debug(f"reconcile_bool(False, True, resolve_true=False) = {result}")
        assert result is False

    def test_reconcile_uint64_resolve_true_prefers_the_true_operand(self) -> None:
        # val1=0 (falsy), val2=1 (truthy), resolve_true=True -> should prefer
        # val2 since it's the operand whose bool cast is True
        result: int | None = GenUtils.reconcile_uint64(0, 1, resolve_true=True)
        logger.debug(f"reconcile_uint64(0, 1, resolve_true=True) = {result}")
        assert result == 1

    #endregion
