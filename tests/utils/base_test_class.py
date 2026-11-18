import logging
import pytest

from abc import ABC
from time import perf_counter
from typing import Any, Generator
from monero import MoneroUtils

logger: logging.Logger = logging.getLogger("BaseTestClass")


class BaseTestClass(ABC):
    """Base test class with common fixtures."""

    _elapsed_ms: float = 0.0
    """Milliseconds that the last test took, set when the test ends and before `after_each`."""

    # Setup and teardown of test class
    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def global_setup_and_teardown(cls) -> Generator[None, Any, None]:
        """Executed once before all tests.

        :returns Generator[None, Any, None]: yields control to the test class after setup, then
            runs teardown once all tests in the class have completed.
        """
        # the hooks are methods of an instance, which is not the one of a test: what they set on it would be seen by none
        instance: BaseTestClass = cls()
        instance.before_all()
        yield
        instance.after_all()

    # Setup and teardown of each test
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest) -> Generator[None, Any, None]:
        """Executed before each test.

        :param pytest.FixtureRequest request: the pytest request fixture for the running test.
        :returns Generator[None, Any, None]: yields control to the test after setup, then runs
            teardown once the test has completed.
        """
        self.before_each(request)
        # the time of the test itself: after what before_each does, until the test ends
        started: float = perf_counter()
        yield
        self._elapsed_ms = (perf_counter() - started) * 1000
        self.after_each(request)

    # Before all tests
    def before_all(self) -> None:
        """Executed once before all tests."""
        msg: str = f"Setup test class {type(self).__name__}"
        MoneroUtils.log_info(msg)
        logger.info(msg)

    # After all tests
    def after_all(self) -> None:
        """Executed once after all tests."""
        msg: str = f"Teardown test class {type(self).__name__}"
        MoneroUtils.log_info(msg)
        logger.info(msg)

    # Before each test
    def before_each(self, request: pytest.FixtureRequest) -> None:
        """Executed before each test.

        :param pytest.FixtureRequest request: Request fixture.
        """
        msg: str = f"Before {request.node.name}"
        MoneroUtils.log_info(msg)
        logger.info(msg)

    # After each test
    def after_each(self, request: pytest.FixtureRequest) -> None:
        """Executed after each test.

        :param pytest.FixtureRequest request: Request fixture.
        """
        msg: str = self.after_message(request)
        MoneroUtils.log_info(msg)
        logger.info(msg)

    def after_message(self, request: pytest.FixtureRequest) -> str:
        """The message that says that a test ended, with the time that it took.

        :param pytest.FixtureRequest request: Request fixture.
        :returns str: `After <test> (<milliseconds> ms)`.
        """
        return f"After {request.node.name} ({self._elapsed_ms:.1f} ms)"
