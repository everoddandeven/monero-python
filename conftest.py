import pytest

from monero import MoneroError

def pytest_runtest_call(item: pytest.Item):
    # get not_supported marked
    marker = item.get_closest_marker("not_supported")
    not_implemented = False
    if marker is None:
        marker = item.get_closest_marker("not_implemented")
        not_implemented = True

    if marker is None:
        # marked not found
        return

    try:
        # run test
        item.runtest()
    except MoneroError as e:
        e_str = str(e).lower()
        if "not supported" in e_str or "does not support" in e_str:
            # Ok
            pytest.xfail(str(e))
        if not_implemented and "not implemented" in e_str:
            pytest.xfail(str(e))
        raise
    else:
        # fail test
        pytest.fail("Expected test to fail")
