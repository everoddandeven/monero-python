---
title: VS Code
---
# VS Code

The repository has a configuration for VS Code in [.vscode/](https://github.com/libmonero/monero-python/tree/main/.vscode): tasks
that build and test, a Testing panel that finds the tests and the module, launch configurations that debug the tests in Python and
in the C++ of the module, and the type checking of the tests.

| Page | What it has |
| --- | --- |
| [Testing Panel](testing_panel.md) | running and debugging the tests one by one |
| [Debugging](debugging.md) | the launch configurations, in Python and in the C++ of the module |
| [Type Checking and Coverage](checks.md) | the type checking of the tests, and their coverage in the editor |

## Extensions

VS Code proposes the extensions of `.vscode/extensions.json` when the folder is opened:

| Extension | For |
| --- | --- |
| Python, Python Debugger, Pylance | the tests, their debugging, the type checking |
| C/C++, CMake Tools | the C++ of the bindings, its build and its debugging |
| Container Tools | the containers of the test environment |
| GitHub Actions | the workflows of CI |
| ShellCheck | the scripts of `bin/` |
| Coverage Gutters | the coverage of the tests, in the editor |
| Tasks | the most used tasks as buttons of the status bar, and the others from its `...` button |

## First setup

From **Terminal → Run Task**, or the `...` button of the status bar:

1. `setup: system dependencies`: the packages of apt that the build needs (`bin/install_dependencies_linux.sh`).
2. `setup: venv`: the virtual environment `.venv`, with the tools of the build, of the tests and of the docs
   (`bin/setup_venv.sh`). VS Code uses it as the interpreter of the folder on its own.
3. `build: monero-cpp`: monero-project and monero-cpp, once and after an update of the submodules.
4. `build: monero-python`: the module in `build/`, the default build task (**Ctrl+Shift+B**).

## Tasks

| Task | What it does |
| --- | --- |
| `build: monero-python` | builds the module in `build/` |
| `build: monero-python module (debug)` | builds it with the symbols and no optimization, in `build-debug/`, for the debugger of C++ |
| `build: monero-cpp with debug info` | monero-cpp with its symbols, to step into it |
| `tests: setup docker` | starts the network of the integration tests |
| `tests: build and setup docker` | builds the module, then starts the network |
| `tests: integration` | builds the module, starts the network, then runs `pytest -m integration` |
| `tests: stop docker` | stops the network and removes its volumes |
| `tests: unit` | `pytest -m unit` |
| `tests: unit (coverage)` | `pytest -m unit` with the coverage of the tests in `coverage.xml`, as in CI |
| `lint: workflows` | actionlint and zizmor on the workflows, with the versions of CI |
| `lint: links` | lychee on the links to the web of the docs, the stubs and the README, with the version of CI |
| `lint: spelling` | codespell on the files of git, with the version of CI: the typos show in **Problems** |
| `docs: serve` | the docs at `http://127.0.0.1:8000`, built again at every change |
| `docs: build` | the docs, strict as in CI |

What the build, the tests and the lint find goes to **Problems**, and to the counter of errors and warnings of the status bar: an error
of the compiler, a test that fails, a typo, a broken link, each one with a link to its file.
