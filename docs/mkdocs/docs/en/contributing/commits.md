---
title: Commits and Pull Requests
---
# Commits and Pull Requests

## Commits

A commit message is one line, `<scope>: <what the change does>`, in lowercase and without a period:

```
wallet: add get_incoming_transfers() and get_outgoing_transfers()
tests: stop mining in test_multisig only when it started it
build: link chrono and atomic with boost thread
```

The scope is the part of the repository that the change is about:

| Scope | For |
| --- | --- |
| `wallet`, `utils`, `bindings` | the library: the bindings of `src/cpp` |
| `pyi` | the stubs of `src/monero` |
| `tests` | the tests (older commits have `unit tests` and `integration tests`) |
| `docs` | the docs, the site, the README |
| `build` | CMake, the packaging, the build requirements |
| `ci` | the workflows of `.github` |
| `release` | the release workflow, `release.yml` |
| `bin` | the scripts of `bin/` |
| `vscode` | the configuration of `.vscode` |
| `version` | the version of `pyproject.toml`, for a release: `version: bump to v0.9.11` |

A commit has one change: a fix and a refactoring are two commits. A message says what the change does, and why when it is not
evident from what it does.

## Pull requests

- To `main`, from a branch of your fork.
- The title is written as a commit; the description says what the change is for, in a few lines.
- One topic for each pull request: two unrelated changes are two pull requests.

## What CI checks

| Workflow | On a pull request that changes | What it does |
| --- | --- | --- |
| CI (`ci.yml`) | anything but the docs, the README and the workflows that it does not run | builds the module on Linux, macOS and Windows, runs the unit tests on each and the integration tests on Linux, merges the coverage |
| Docs (`docs.yml`) | the docs, the stubs, the README, the support matrix | checks the code of the examples, builds the site with `--strict` |
| Build Debian Packages (`build-deb.yml`) | `debian/`, the build of monero-cpp, `CMakeLists.txt`, `pyproject.toml` | builds the deb packages of noble, jammy and trixie, on amd64, arm64 and armhf |
| Lint workflows (`lint-workflows.yml`) | `.github/` | actionlint and zizmor |

The checks are not required by GitHub: a maintainer merges a pull request once they pass. [Continuous Integration](ci.md) has all
the workflows.
