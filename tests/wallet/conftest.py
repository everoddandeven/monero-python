from __future__ import annotations

from typing import Any, Generator

import pytest

from utils import TestUtils


@pytest.fixture(scope="session", autouse=True)
def close_test_wallets() -> Generator[None, Any, None]:
    """The wallet of each type is open for all the tests of its type, in all the files, and is closed at the end."""
    yield
    TestUtils.close_wallets()
