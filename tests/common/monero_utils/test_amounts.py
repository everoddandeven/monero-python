from __future__ import annotations

import logging

import pytest
from monero import MoneroUtils

from utils import BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroUtilsAmounts")


@pytest.mark.unit
class TestMoneroUtilsAmounts(BaseTestClass):
    """Monero utilities amounts unit tests."""

    # Can convert between XMR and atomic units
    def test_atomic_unit_conversion(self) -> None:
        assert 1000000000000 == MoneroUtils.xmr_to_atomic_units(1)
        assert 1 == MoneroUtils.atomic_units_to_xmr(1000000000000)
        assert 1000000000 == MoneroUtils.xmr_to_atomic_units(0.001)
        assert 0.001 == MoneroUtils.atomic_units_to_xmr(1000000000)
        assert 250000000000 == MoneroUtils.xmr_to_atomic_units(0.25)
        assert 0.25 == MoneroUtils.atomic_units_to_xmr(250000000000)
        assert 1250000000000 == MoneroUtils.xmr_to_atomic_units(1.25)
        assert 1.25 == MoneroUtils.atomic_units_to_xmr(1250000000000)
        assert 2796726190000 == MoneroUtils.xmr_to_atomic_units(2.79672619)
        assert 2.79672619 == MoneroUtils.atomic_units_to_xmr(2796726190000)
        assert 2796726190001 == MoneroUtils.xmr_to_atomic_units(2.796726190001)
        assert 2.796726190001 == MoneroUtils.atomic_units_to_xmr(2796726190001)
        assert 2796726189999 == MoneroUtils.xmr_to_atomic_units(2.796726189999)
        assert 2.796726189999 == MoneroUtils.atomic_units_to_xmr(2796726189999)
        assert 2796726180000 == MoneroUtils.xmr_to_atomic_units(2.79672618)
        assert 2.79672618 == MoneroUtils.atomic_units_to_xmr(2796726180000)

    # xmr_to_atomic_units(0.0) and negative zero are valid, not errors
    def test_xmr_to_atomic_units_zero(self) -> None:
        assert 0 == MoneroUtils.xmr_to_atomic_units(0.0)
        # -0.0 < 0 is False in IEEE 754, so it must not be rejected by the
        # "amount must be non-negative" check
        assert 0 == MoneroUtils.xmr_to_atomic_units(-0.0)

    # Amounts smaller than half an atomic unit (1e-12 XMR) round down to 0
    def test_xmr_to_atomic_units_rounds_down_to_zero(self) -> None:
        assert 0 == MoneroUtils.xmr_to_atomic_units(1e-13)
        assert 0 == MoneroUtils.xmr_to_atomic_units(4e-13)

    # xmr_to_atomic_units() rounds the underlying long double * 1e12 product to
    # the nearest atomic unit (away from zero on an exact .5). Decimal literals
    # ending in .5e-12 are not necessarily exact halves once represented as a
    # double, so which way they round depends on whether the closest double is
    # a hair above or below the nominal decimal value, and that itself can
    # depend on the platform's "long double" precision (80-bit extended on
    # x86_64 Linux/glibc, but identical to a plain 64-bit double on Apple
    # Silicon/macOS), so the same literal can round differently on different
    # platforms. This is inherent to IEEE 754, not an inconsistency in
    # xmr_to_atomic_units() itself, assert the result lands on one of the
    # two atomic units the value sits between, not a specific platform's tie-break.
    def test_xmr_to_atomic_units_half_atomic_unit_rounding(self) -> None:
        cases: list[tuple[float, int, int]] = [
            (0.5e-12, 0, 1),
            (1.5e-12, 1, 2),
            (2.5e-12, 2, 3),
            (3.5e-12, 3, 4),
        ]
        for amount_xmr, floor_atomic, ceil_atomic in cases:
            actual: int = MoneroUtils.xmr_to_atomic_units(amount_xmr)
            logger.debug(f"xmr_to_atomic_units({amount_xmr!r}) = {actual} (expected {floor_atomic} or {ceil_atomic})")
            assert actual in (floor_atomic, ceil_atomic), f"xmr_to_atomic_units({amount_xmr!r}) == {actual}, expected {floor_atomic} or {ceil_atomic}"

    # amount_xmr must be finite and non-negative
    @pytest.mark.parametrize("amount_xmr", [-1.0, -0.0000000001, float("nan"), float("inf"), float("-inf")])
    def test_xmr_to_atomic_units_invalid_amount(self, amount_xmr: float) -> None:
        with pytest.raises(RuntimeError, match="amount must be a finite, non-negative number"):
            MoneroUtils.xmr_to_atomic_units(amount_xmr)

    # amounts whose rounded atomic-unit value would overflow uint64_t are rejected
    # rather than silently wrapping or invoking undefined behavior on the cast
    def test_xmr_to_atomic_units_overflow(self) -> None:
        # UINT64_MAX atomic units is ~18446744.0737... XMR; comfortably over that
        # (with margin for float imprecision) must raise
        with pytest.raises(RuntimeError, match="amount exceeds maximum representable atomic units"):
            MoneroUtils.xmr_to_atomic_units(18446745.0)
        with pytest.raises(RuntimeError, match="amount exceeds maximum representable atomic units"):
            MoneroUtils.xmr_to_atomic_units(2e22)

    # values comfortably below the uint64_t boundary succeed
    def test_xmr_to_atomic_units_near_uint64_max_boundary(self) -> None:
        uint64_max: int = 2 ** 64 - 1
        boundary_xmr: float = uint64_max / 1e12  # ~18446744.073709551615 XMR
        margin_xmr: float = 1.0

        safely_below: float = boundary_xmr - margin_xmr
        below: int = MoneroUtils.xmr_to_atomic_units(safely_below)
        logger.debug(f"xmr_to_atomic_units({safely_below!r}) = {below} (uint64_max = {uint64_max})")
        assert below <= uint64_max

        safely_above: float = boundary_xmr + margin_xmr
        with pytest.raises(RuntimeError, match="amount exceeds maximum representable atomic units"):
            MoneroUtils.xmr_to_atomic_units(safely_above)
