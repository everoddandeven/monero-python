---
title: Making a Change
---
# Making a Change

A change of the library has its parts in more than one place: the C++ of the binding, the stub that describes it, the tests, the docs.

## A binding

1. **The C++**, in `src/cpp`: the binding of the function or of the class, with a `py::arg` for each parameter, so that it can be called
   with keywords and has names in its signature.
2. **The stub**, in `src/monero/<module>.pyi`: its signature with the types, and its docstring in the Sphinx style
   (`:param type name: ...`, `:returns type: ...`). A function with overloads has a `@typing.overload` definition for each of them, each
   with its docstring. The stubs are what type checkers and editors see of the module, and what the [API Reference](../api/wallet.md)
   is made from.
3. **The lint**: `python3 bin/lint_bindings.py` turns the bindings of the built module into stubs with pybind11-stubgen, and fails on
   what it can not make sense of: a C++ type that is not registered, a default value that is only a repr, a parameter with no name.
   CI runs it on the Linux build.

## Its tests

- A test for what it does, in the file of its topic: [Writing Tests](../tests/writing/index.md) has where each kind of test goes.
- A new method of `MoneroWallet` needs a call in `tests/utils/wallet_calls.py` and a row in the support matrix, or a test fails:
  [A New Wallet Method](../tests/writing/new_wallet_method.md).
- A test of a wallet type that does not do it yet is marked `not_implemented`; one of a type that can not do it, `not_supported`.

## Its docs

- The docstrings of the stub are its documentation in the [API Reference](../api/wallet.md).
- A page of the site is a Markdown file in `docs/mkdocs/docs/en`, and an entry in the `nav` of `docs/mkdocs/mkdocs.yml`.
- The code of the examples and of `README.md` is checked against the stubs: a renamed method fails the check until the examples
  follow.

## Before a pull request

| Command | What it checks | When |
| --- | --- | --- |
| `pytest -m unit` | the unit tests | always |
| `pytest -m integration` | the integration tests, on the network of `tests/docker-compose.yml` | a change of what talks to a daemon or a wallet ([Running the Tests](../tests/running/index.md)) |
| the **Problems** of VS Code | the types of the tests and of the scripts, with Pylance in strict mode | a change of Python |
| `python3 bin/lint_bindings.py` | the bindings, against what stubgen makes of them | a change of `src/cpp` |
| `python3 bin/check_examples.py` | the code of the docs and of `README.md`, against the stubs | a change of a stub or of an example |
| `./bin/docs.sh build` | the site, strict as in CI: a reference or a link that does not resolve fails it | a change of the docs or of a stub |
| `./bin/lint_workflows.sh` | the workflows, with the actionlint and zizmor of CI | a change of `.github` |
| `./bin/check_spelling.sh` | the spelling of the docs, the docstrings, the comments and the messages, with the codespell of CI; `-w` fixes the typos with one correction | always |

CI runs them all on the pull request, but on your machine they take a fraction of the time.
