---
title: Type Checking and Coverage
---
# Type Checking and Coverage

What the editor shows of the tests, besides running them.

## Type checking

Pylance checks the tests in strict mode, with more rules than strict (`.vscode/settings.json`), and shows the errors of every file in
**Problems**, not only of the open ones. It reads the types of the module from its stubs in `src/monero`, and the helpers of the tests
from `tests/`. An error in Problems is one that the change brings: the code of the repository has none.

## Coverage in the editor

The task `tests: unit with coverage` writes `coverage.xml`. With Coverage Gutters, **Coverage Gutters: Display Coverage** (or
**Watch**) colors the lines of the tests that the run covered.
