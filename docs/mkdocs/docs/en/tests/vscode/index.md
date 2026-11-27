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

The buttons of the status bar are of an extension of the repository, `.vscode/extensions/status-bar-buttons`:

| Button | What it shows |
| --- | --- |
| Build | runs `build: monero-python` |
| Docker | **Setup Docker** when the network of the integration tests is down and **Stop Docker** when it is up, also when `docker compose` is run from a terminal; a warning icon, with their names in the tooltip, when some of its services do not run |
| Docs | **Build Docs**, which runs `docs: serve`; a spinning icon while the site is built and **Stop Docs** once it is served |
| Lint | a menu that runs `lint: links`, `lint: spelling`, `lint: workflows` or `lint: examples` |

While a task of `.vscode/tasks.json` runs, the buttons of the other tasks are gray and do nothing, so that two of them do not work
at once; their tooltip says what they wait for. The server of the docs makes them wait only while it builds the site. A task run
from **Terminal → Run Task**, or from a launch configuration, does not wait.

It also shows as popups what a lint task finds: one for each of the first three problems, with a button that opens it, and one
for the others, which opens **Problems**. The redirects of the links are a popup of warning, and the terminal shows where each one goes
(`./bin/check_links.sh -vv`). A hint of lychee is a popup of warning too: the task keeps a copy of its output in
`.cache/lint-links.log` for them.

At the end of a build task it shows a popup with the result and the time, if the build failed or took more than 30 seconds, and
after `build: monero-python` it reads the tests of the **Testing** panel again.

VS Code does not install it on its own: run **Extensions: Show Recommended Extensions** and install it from
**Workspace Recommendations**. It needs a trusted folder.

## First setup

From **Terminal → Run Task**:

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
| `lint: examples` | the code of the docs and of the README against the stubs: the errors show in **Problems** |
| `lint: spelling` | codespell on the files of git, with the version of CI: the typos show in **Problems** |
| `docs: serve` | the docs at `http://127.0.0.1:8000`, built again at every change |
| `docs: build` | the docs, strict as in CI |

The build tasks run 3 compilers at once, at a low priority. The environment variable `MONERO_JOBS` changes their number, as 1 on a
machine with little memory, for instance in your user settings:

```json
"terminal.integrated.env.linux": { "MONERO_JOBS": "1" }
```

What the build, the tests, the docs and the lint find goes to **Problems**, and to the counter of errors and warnings of the status
bar: an error of the compiler, a test that fails, a wrong example or reference of the docs, a typo, a broken link, each one with a
link to its file.
