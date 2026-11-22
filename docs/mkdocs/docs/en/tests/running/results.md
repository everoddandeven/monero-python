---
title: Results and Logs
---
# Results and Logs

What pytest prints, what it writes, and how to stop and resume a run.

## Reading the results

`pytest.ini` runs pytest with `-s -v`: one line for each test, and what the tests print, as it comes. The outcomes:

| Outcome | Meaning |
| --- | --- |
| `PASSED` | the test passed; a `not_supported` test passes when the call raises "not supported" |
| `FAILED` | the test failed |
| `SKIPPED` | a condition of the test is off: a flag of `config.ini` (`test_relays`, `lite_mode`...), or what it needs is not there |
| `XFAIL` | a `not_implemented` test, that still fails as expected |
| `FAILED ... [XPASS(strict)]` | a `not_implemented` test that passes: the feature is done, and its marker has to go |
| `RERUN` | the test failed with `Daemon is busy` and runs again |

At the end, `-rA` adds a summary of every outcome, `-rfE` of the failures and the errors only. `--tb=short` or `--tb=line` makes the
tracebacks shorter.

```bash
pytest -m unit -q -rfE --tb=short
```

## Logs

| Where | What |
| --- | --- |
| the console | the `INFO` messages of the tests, as they run (`log_cli` in `pytest.ini`) |
| `test_logs/monero_tests_python_<date>.log` | the `DEBUG` messages of the tests, one file for each run |
| `test_logs/monero_tests_cpp_<date>.log` | the log of monero-cpp, at the `log_level` of `config.ini` |

```bash
pytest --log-cli-level=DEBUG tests/wallet/test_sync.py      # the DEBUG messages in the console too
pytest -o log_file=my_run.log -m unit                      # the log of the tests in a file of your choice
```

A run in which pytest only collects the tests, as the Testing panel of an IDE does at every change, writes no log. In CI, a job run
again with **Enable debug logging** shows the `DEBUG` messages in the console. The logs of the jobs of CI are artifacts of the run,
with the logs of the containers for the integration tests.

## Stopping, repeating, resuming

```bash
pytest -x                   # stop at the first failure
pytest --maxfail=3          # stop at the third
pytest --lf                 # only the tests that failed in the last run
pytest --ff                 # the ones that failed first, then the others
pytest --sw                 # stepwise: stop at a failure, and start from it the next time
```

`--lf`, `--ff` and `--sw` read `.pytest_cache`, which `./bin/cleanup_test_environment.sh` removes.
