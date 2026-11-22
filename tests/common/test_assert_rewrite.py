import pytest

from utils import BaseTestClass
# the modules, not their classes: a class imported here with a name that starts with Test would be collected as a test
import utils.gen_utils as helpers_of_the_tests
import tests.utils.gen_utils as helpers_of_conftest


@pytest.mark.unit
class TestAssertRewrite(BaseTestClass):
    """The asserts of the helpers of tests/utils show their values when they fail, as the ones of the tests: conftest.py has pytest
    rewrite them. Without it, a failed assert of a helper is a bare AssertionError, with only its message if it has one."""

    #region Tests

    # A helper imported as the tests import it, from utils
    def test_helpers_of_the_tests_show_the_values_of_a_failed_assert(self) -> None:
        with pytest.raises(AssertionError) as exc_info:
            helpers_of_the_tests.GenUtils.test_unsigned_big_integer(-5)
        # its message, and the comparison with the value that failed it, which only a rewritten assert has
        assert "Value cannot be negative" in str(exc_info.value)
        assert "assert -5 >= 0" in str(exc_info.value)

    # The same helper imported as conftest.py imports it, from tests.utils
    def test_helpers_of_conftest_show_the_values_of_a_failed_assert(self) -> None:
        with pytest.raises(AssertionError) as exc_info:
            helpers_of_conftest.GenUtils.test_unsigned_big_integer(-5)
        assert "assert -5 >= 0" in str(exc_info.value)

    #endregion
