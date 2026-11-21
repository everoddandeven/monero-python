---
title: Development Setup
---
# Development Setup

What working on the library needs, on Linux. macOS and Windows have their steps in
[Build from Source](../getting_started/build_linux_macos.md).

## Set up

```bash
git clone --recurse-submodules https://github.com/libmonero/monero-python.git   # with monero-cpp and monero-project
cd monero-python
./bin/install_dependencies_linux.sh     # the packages of apt that the build needs, on Debian and Ubuntu
./bin/setup_venv.sh                     # .venv, with the tools of the build, the tests and the docs, at the versions of CI
. .venv/bin/activate
./bin/build_monero_cpp.sh               # monero-project and monero-cpp, once and after an update of the submodules
cmake -B build -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)"
cmake --build build                     # the module, in build/, after each change of the C++
export PYTHONPATH="$PWD/build"
pytest -m unit                          # the unit tests
```

`./bin/build_monero_cpp.sh` runs 3 jobs, since a compiler of monero takes up to 1.5 GB of memory: set `JOBS` for more or fewer. With
[ccache](https://ccache.dev/) installed, the builds of monero and of the module use it on their own.

After a `git pull` that moves the submodules, update them and build monero-cpp again:

```bash
./bin/update_submodules.sh
./bin/build_monero_cpp.sh
```

The repository has a configuration for VS Code, with tasks for each of these steps: [VS Code](../tests/vscode/index.md).

## The repository

| Folder | What it has |
| --- | --- |
| `src/cpp` | the bindings: the C++ that exposes monero-cpp to Python with pybind11, a folder for each part (`common`, `daemon`, `wallet`, `utils`) |
| `src/monero` | the stubs of the module (`.pyi`): the types and the docstrings of every class and function, which type checkers read and the docs are made from |
| `external/monero-cpp` | the submodule of [monero-cpp](https://github.com/woodser/monero-cpp), with monero-project in it |
| `tests` | the tests, with their configuration and their network in docker ([Tests](../tests/index.md)) |
| `docs/mkdocs` | this site |
| `bin` | the scripts of the build, of the tests, of the docs and of CI |
| `debian` | the packaging of the deb packages |
| `.github` | the workflows of CI, the configuration of Dependabot, the notes of the releases |
| `CMakeLists.txt`, `pyproject.toml` | the build of the module, and of its wheel with scikit-build-core |
