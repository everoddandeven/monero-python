from __future__ import annotations

import logging

from os.path import splitext
from typing import TYPE_CHECKING, Generator, Optional, cast

import pytest

from tests.utils.gen_utils import GenUtils

if TYPE_CHECKING:
    from pluggy import Result  # runtime-optional (pluggy < 1.2), only needed for typing

logger: logging.Logger = logging.getLogger("conftest")

_NOT_SUPPORTED_HINTS: tuple[str, ...] = ("not supported", "does not support", "doesn't support")


def _crash_message(report: pytest.TestReport) -> str:
    reprcrash: object = getattr(report.longrepr, "reprcrash", None)
    message: Optional[str] = getattr(reprcrash, "message", None)
    return str(message) if message else (report.longreprtext or "unknown")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.outcome != "rerun":  # type: ignore  # set by pytest-rerunfailures
        return
    logger.error(f"EXPECTED FAILURE: {_crash_message(report)}")
    logger.warning(f"RERUN {report.nodeid}")


def pytest_configure(config: pytest.Config) -> None:
    # timestamp the log file so each run keeps its own
    log_file: str = cast(str, config.getini("log_file"))
    if not log_file:
        return
    name, ext = splitext(log_file)
    config.option.log_file = f"{name}_{GenUtils.current_date_time_str()}{ext}"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # `not_implemented` == non-strict xfail: xfails while it raises, xpasses once done
    for item in items:
        if item.get_closest_marker("not_implemented") is not None:
            item.add_marker(pytest.mark.xfail(reason="not implemented", strict=False))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, Result[None], None]:
    # `not_supported`: the inherited test must raise a "not supported" error;
    # that's a pass, anything else (or no error) is a failure.
    if item.get_closest_marker("not_supported") is None:
        yield
        return

    outcome: Result[None] = yield

    try:
        outcome.get_result()
    except Exception as error:
        if any(hint in str(error).lower() for hint in _NOT_SUPPORTED_HINTS):
            logger.debug(f"NOT SUPPORTED (as expected): {error}")
            outcome.force_result(None)
        return

    outcome.force_exception(pytest.fail.Exception("Expected a 'not supported' error"))
