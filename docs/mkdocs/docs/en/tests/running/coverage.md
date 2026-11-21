---
title: Local Coverage
---
# Local Coverage

The coverage on your machine, as CI makes it. The reports of CI are on the [Coverage](../../coverage.md) page.

The coverage of the Python code of the tests, as in CI:

```bash
pytest -m unit --cov=tests --cov-report=html:coverage_tests_html
pytest -m unit --cov=tests --cov-report=term:skip-covered       # the files that are not fully covered, in the console
pytest -m unit --cov=tests --cov-report=xml:coverage.xml         # for the editor (Coverage Gutters)
```

The coverage of the C++ of the bindings and of monero-cpp needs both built with it:

```bash
COVERAGE=ON ./bin/build_monero_cpp.sh
cmake -B build -DENABLE_COVERAGE=ON -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)"
cmake --build build
pytest -m unit
```

Then the reports, with the commands of CI (`lcov` and `genhtml` are in the `lcov` package of apt). The bindings:

```bash
lcov --capture --directory build --output-file coverage_full.info \
    --ignore-errors mismatch,mismatch,inconsistent,source,source,gcov,gcov
lcov --remove coverage_full.info '/usr/*' '*/external/*' '*/pybind11/*' --output-file coverage.info \
    --ignore-errors unused,unused
genhtml coverage.info --output-directory coverage_bindings_html
```

monero-cpp:

```bash
lcov --capture --directory external/monero-cpp/build --directory build --output-file coverage_monero_cpp_full.info \
    --ignore-errors mismatch,mismatch,inconsistent,source,source,gcov,gcov
lcov --extract coverage_monero_cpp_full.info '*/monero-cpp/src/*' --output-file coverage_monero_cpp.info \
    --ignore-errors unused,unused
genhtml coverage_monero_cpp.info --output-directory coverage_monero_cpp_html
```

Every file and folder that starts with `coverage` is ignored by git. The reports of CI are on the [Coverage](../../coverage.md) page.
