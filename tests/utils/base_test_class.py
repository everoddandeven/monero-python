import logging
import pytest

from abc import ABC

from monero import MoneroUtils

logger: logging.Logger = logging.getLogger("BaseTestClass")


class BaseTestClass(ABC):
    """Base test class with common fixtures."""

    # Setup and teardown of test class
    @pytest.fixture(scope="class", autouse=True)
    def global_setup_and_teardown(self):
        """Executed once before all tests."""
        self.before_all()
        yield
        self.after_all()

    # Setup and teardown of each test
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        """Executed before each test."""
        self.before_each(request)
        yield
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

        :param pytest.FixtureRequest: Request fixture.
        """
        msg: str = f"Before {request.node.name}" # type: ignore
        MoneroUtils.log_info(msg)
        logger.info(msg)

    # After each test
    def after_each(self, request: pytest.FixtureRequest) -> None:
        """Executed after each test.

        :param pytest.FixtureRequest: Request fixture.
        """
        msg: str = f"After {request.node.name}" # type: ignore
        MoneroUtils.log_info(msg)
        logger.info(msg)
