---
title: Testing Panel
---
# Testing Panel

The Testing panel (the flask in the activity bar) finds the tests of `tests/` with pytest, and runs and debugs them one by one, by
file or all of them. It finds the module in `build/` through `.vscode/.env` (`PYTHONPATH=build`), which the processes that the tests
start get too.

- The panel collects the tests at every change of a file: a collection writes no log and makes no wallet.
- **Run Test** runs the test with the options of `pytest.ini`. **Debug Test** runs it with `--reruns 0 --timeout 0 --no-cov`, so a
  breakpoint waits as long as needed, and builds the module first.
- An integration test needs the network: start it with `tests: setup docker`.
