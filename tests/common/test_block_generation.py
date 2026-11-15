from __future__ import annotations

from typing import Any

import pytest
from monero import MoneroDaemonInfo

from utils import BaseTestClass
from utils.block_generation import MAX_GENERATE_DIFFICULTY, is_generation_fast


class _Daemon:
    """Daemon that answers get_info with a given difficulty."""

    def __init__(self, difficulty: int, is_regtest: bool | None = True, fails: bool = False) -> None:
        self._difficulty: int = difficulty
        self._is_regtest: bool | None = is_regtest
        self._fails: bool = fails

    def get_info(self) -> MoneroDaemonInfo:
        if self._fails:
            raise RuntimeError("no node")
        info: MoneroDaemonInfo = MoneroDaemonInfo()
        info.difficulty_low = self._difficulty & ((1 << 64) - 1)
        info.difficulty_high = self._difficulty >> 64
        info.is_regtest = self._is_regtest
        return info


@pytest.mark.unit
class TestBlockGeneration(BaseTestClass):
    """Choice between generating and mining blocks, unit tests."""

    # Blocks are generated at a low difficulty, where the miner makes too many
    @pytest.mark.parametrize("difficulty", [1, 5, MAX_GENERATE_DIFFICULTY])
    def test_generates_at_low_difficulty(self, difficulty: int) -> None:
        assert is_generation_fast(_Daemon(difficulty)) is True  # type: ignore[arg-type]

    # Blocks are mined at a high difficulty, where the miner is faster than generating
    @pytest.mark.parametrize("difficulty", [MAX_GENERATE_DIFFICULTY + 1, 500, 1 << 70])
    def test_mines_at_high_difficulty(self, difficulty: int) -> None:
        assert is_generation_fast(_Daemon(difficulty)) is False  # type: ignore[arg-type]

    # Blocks are not generated outside regtest, or when the daemon does not answer
    @pytest.mark.parametrize("daemon", [_Daemon(5, is_regtest=False), _Daemon(5, fails=True), _Daemon(0)])
    def test_does_not_generate_otherwise(self, daemon: Any) -> None:
        assert is_generation_fast(daemon) is False
