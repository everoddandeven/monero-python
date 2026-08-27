import logging
import pytest

from os.path import splitext
from tests.utils.gen_utils import GenUtils

logger: logging.Logger = logging.getLogger("conftest")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.outcome != "rerun": # type: ignore - pytest-rerunfailures sets this outcome
        return

    message: str

    try:
        crash_msg = report.longrepr.reprcrash.message # type: ignore
        message = str(crash_msg) if crash_msg is not None else "" # type: ignore
    except AttributeError:
        message = report.longreprtext
    except Exception as e:
        message = str(e)

    if len(message) == 0:
        message = "Unknwon"

    logger.error(f"EXPECTED FAILURE: {message}")
    logger.warning(f"RERUN {report.nodeid}")


def pytest_configure(config: pytest.Config) -> None:
    # inject current date/time into the configured log file name
    log_file: str = config.getini("log_file") # type: ignore

    if not log_file:
        return

    name, ext = splitext(log_file)
    config.option.log_file = f"{name}_{GenUtils.current_date_time_str()}{ext}"


def pytest_runtest_call(item: pytest.Item):
    # get not_supported marker
    marker: pytest.Mark | None = item.get_closest_marker("not_supported")
    not_implemented: bool = False

    if marker is None:
        # get not_implemented marker
        marker = item.get_closest_marker("not_implemented")
        not_implemented = True

    if marker is None:
        # marker not found
        return

    try:
        # run test
        item.runtest()
    except Exception as e:
        e_str = str(e).lower()
        if "not supported" in e_str or "does not support" in e_str or "doesn't support" in e_str:
            # Ok
            pytest.xfail(str(e))
        if not_implemented and "not implemented" in e_str:
            pytest.xfail(str(e))
        raise
    else:
        # fail test
        pytest.fail("Expected test to fail")
