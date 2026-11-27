from __future__ import annotations

import logging

from os import devnull, environ
from os.path import splitext
from typing import TYPE_CHECKING, Generator, Optional, cast

import pytest

# pytest shows the values of a failed assert only in the modules that it rewrites, the tests and the conftest files: the asserts of the
# helpers would fail with a bare AssertionError. They are rewritten too, under both the names that they are imported with, before the
# first import of them
pytest.register_assert_rewrite("utils", "tests.utils")

from tests.utils.gen_utils import GenUtils
from tests.utils.test_utils import TestUtils
from tests.utils.wallet_calls import NOT_SUPPORTED_HINTS

if TYPE_CHECKING:
    from pluggy import Result  # runtime-optional (pluggy < 1.2), only needed for typing

logger: logging.Logger = logging.getLogger("conftest")


def _crash_message(report: pytest.TestReport) -> str:
    reprcrash: object = getattr(report.longrepr, "reprcrash", None)
    message: Optional[str] = getattr(reprcrash, "message", None)
    return str(message) if message else (report.longreprtext or "unknown")


def _outcome(report: pytest.TestReport) -> Optional[str]:
    """The word of the terminal for the result of a phase of a test, None for a setup or a teardown that passed."""
    if hasattr(report, "wasxfail"):
        return "XPASS" if report.passed else "XFAIL"
    if report.failed:
        return "FAILED" if report.when == "call" else "ERROR"
    if report.skipped:
        return "SKIPPED"
    return "PASSED" if report.when == "call" else None


def _details(report: pytest.TestReport) -> str:
    """What the terminal says about a result: why a test is an expected failure or was skipped, the traceback of a failure."""
    reason: Optional[str] = getattr(report, "wasxfail", None)
    if reason is not None:
        return f": {reason}"
    # a skip: the file, the line and the reason
    if report.skipped and isinstance(report.longrepr, tuple):
        return f": {report.longrepr[2]}"
    return f"\n{report.longreprtext}" if report.failed else ""


# the log file has what the terminal shows of the tests too: which one runs, its result and the summary. At the DEBUG level, which goes
# to the file and not to the console, where pytest writes them already

def pytest_runtest_logstart(nodeid: str) -> None:
    logger.debug(f"TEST {nodeid}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.outcome == "rerun":  # type: ignore  # set by pytest-rerunfailures
        logger.error(f"EXPECTED FAILURE: {_crash_message(report)}")
        logger.warning(f"RERUN {report.nodeid}")
        return
    outcome: Optional[str] = _outcome(report)
    if outcome is not None:
        logger.debug(f"{outcome} {report.nodeid}{_details(report)}")


def pytest_sessionfinish(session: pytest.Session) -> None:
    plugin: object = session.config.pluginmanager.getplugin("terminalreporter")
    reporter: Optional[pytest.TerminalReporter] = cast(Optional[pytest.TerminalReporter], plugin)
    if reporter is None:
        return
    reports: dict[str, list[pytest.TestReport]] = cast(dict[str, list[pytest.TestReport]], reporter.stats)
    for outcome, key in (("FAILED", "failed"), ("ERROR", "error")):
        for report in reports.get(key, []):
            logger.debug(f"SUMMARY {outcome} {report.nodeid}")
    # the counts of the last line of the terminal, as "2 failed, 886 passed"
    counts, _ = reporter.build_summary_stats_line()
    logger.debug(f"SUMMARY {', '.join(text for text, _ in counts)}")


def pytest_configure(config: pytest.Config) -> None:
    # a job re-run with "Enable debug logging" sets RUNNER_DEBUG=1, show the debug messages in the console too
    if environ.get("RUNNER_DEBUG") == "1":
        config.option.log_level = "DEBUG"
        config.option.log_cli_level = "DEBUG"

    # the Testing panel of an IDE collects the tests at every change, a log for each of them would only be noise
    if config.option.collectonly:
        config.option.log_file = devnull
        return

    # the log of monero-cpp, timestamped as the one of the tests
    TestUtils.configure_logging()
    TestUtils.initialize_test_wallet_dir()

    # timestamp the log file so each run keeps its own
    log_file: str = cast(str, config.getini("log_file"))
    if not log_file:
        return
    name, ext = splitext(log_file)
    config.option.log_file = f"{name}_{GenUtils.current_date_time_str()}{ext}"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # `not_implemented` == strict xfail: xfails while it raises, and fails once the feature is done, so that its marker goes with it
    for item in items:
        if item.get_closest_marker("not_implemented") is not None:
            item.add_marker(pytest.mark.xfail(reason="not implemented", strict=True))


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter) -> None:
    # In GitHub Actions, the xfail tests of the job in the summary of its run: the ones that still fail, and the ones that pass now, whose
    # marker has to go. An xfail does not fail the job, so the log is the only other place that has it; a strict xpass fails it, and is
    # listed apart from the other failures, to tell what it asks for.
    summary: Optional[str] = environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    reports: dict[str, list[pytest.TestReport]] = cast(dict[str, list[pytest.TestReport]], terminalreporter.stats)
    xfailed: list[str] = [f"- `{report.nodeid}`: {report.wasxfail}" for report in reports.get("xfailed", [])]
    # a strict xpass is a failure, the message of which says it
    xpassed: list[str] = [f"- `{report.nodeid}`" for report in reports.get("xpassed", [])] + [
        f"- `{report.nodeid}`" for report in reports.get("failed", []) if report.longreprtext.startswith("[XPASS(strict)]")
    ]
    sections: list[str] = []
    if xfailed:
        sections.append("### Expected failures (xfail)\n\n" + "\n".join(xfailed))
    if xpassed:
        sections.append("### Expected failures that pass now (xpass): their marker can go\n\n" + "\n".join(xpassed))
    if not sections:
        return
    try:
        with open(summary, "a", encoding="utf-8") as file:
            file.write("\n\n".join(sections) + "\n\n")
    except OSError as error:
        # the summary is for reading, it never fails the tests
        logger.warning(f"Cannot write the summary of the job: {error}")


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
        if any(hint in str(error).lower() for hint in NOT_SUPPORTED_HINTS):
            logger.debug(f"NOT SUPPORTED (as expected): {error}")
            outcome.force_result(None)
        return

    outcome.force_exception(pytest.fail.Exception("Expected a 'not supported' error"))
