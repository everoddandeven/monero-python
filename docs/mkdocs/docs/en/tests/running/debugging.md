---
title: Debugging
---
# Debugging

The options of pytest to look into a test, and the ones that rerun and stop the tests.

```bash
pytest --pdb ...            # the debugger of Python at a failure
pytest --trace ...          # the debugger at the start of each test
pytest --durations=25 ...   # the 25 slowest tests, as in CI
```

A breakpoint waits as long as needed with `--reruns 0 --timeout 0`. [VS Code](../vscode/debugging.md) has launch configurations that debug a
test in Python, or in the C++ of the module with gdb.

## Reruns and timeouts

`pytest.ini` runs a test again when it fails with `Daemon is busy`, up to 5 times, 10 seconds apart (pytest-rerunfailures). The other
failures are not run again.

```bash
pytest --reruns 0 ...       # no reruns, as when debugging
pytest --timeout 600 ...    # stop a test that takes more than 10 minutes (pytest-timeout)
```
