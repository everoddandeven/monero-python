---
title: Running the Tests
---
# Running the Tests

The commands are run from the root of the repository: the tests read `tests/config/config.ini` from there, and write their wallets
and logs there. The integration tests also need the network of [Test Environment](../environment/index.md).

| Page | What it has |
| --- | --- |
| [Choosing the Tests](selecting.md) | by marker, file, class, test or name, and the order of the wallet tests |
| [Results and Logs](results.md) | what each outcome means, the summaries, the logs, stopping and resuming |
| [Debugging](debugging.md) | the debugger, the slowest tests, the reruns and the timeouts |
| [Local Coverage](coverage.md) | the coverage of the tests and of the C++, on your machine |

## Set up

1. Build monero-cpp and the module, as in [Build on Linux and macOS](../../getting_started/build_linux_macos.md):
    ```bash
    ./bin/build_monero_cpp.sh
    cmake -B build -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)"
    cmake --build build
    ```
2. Make the virtual environment, with the versions of the tools that CI uses, and activate it:
    ```bash
    ./bin/setup_venv.sh
    . .venv/bin/activate
    ```
    `setup_venv.sh` installs the tools of the build, of the tests and of the docs. For the tests only:
    `pip install -r tests/requirements.txt`.
3. Make the module importable:
    ```bash
    export PYTHONPATH="$PWD/build"
    ```
    Or install it in the environment with `pip install .`, which builds it again. After a change of the C++ of the module, build it
    again with `cmake --build build`: the tests run the module that is in `build/`.
4. For the integration tests, start the network:
    ```bash
    ./bin/setup_test_environment.sh
    ```

Run `pytest` from the environment, or as `python -m pytest`. The `/usr/bin/pytest` of the `python3-pytest` package of apt calls
`pytest.console_main()`, which pytest 9 deprecates: with the pytest of the environment it prints a `PytestRemovedIn10Warning`.

## The whole suite

```bash
pytest                      # every test: the network has to be up
pytest -m unit              # the unit tests, no server needed, half a minute
pytest -m integration       # the integration tests, about 45 minutes
```

## Clean up

```bash
./bin/cleanup_test_environment.sh
```

It removes the containers with their volumes, the wallets of `test_wallets/`, the logs, `.pytest_cache` and the `__pycache__`
folders of the project.
