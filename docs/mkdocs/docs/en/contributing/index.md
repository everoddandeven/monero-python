---
title: Contributing
---
# Contributing

Contributions are welcome: issues and pull requests on [GitHub](https://github.com/libmonero/monero-python), and questions and ideas in
the [#monero-python](https://matrix.to/#/%23monero-python:monero.social) workgroup on Matrix.

| Page | What it has |
| --- | --- |
| [Development Setup](development.md) | cloning, the tools, the build, the layout of the repository |
| [Making a Change](changes.md) | a binding and its stub, its tests, its docs, and the checks to run before a pull request |
| [Writing the Docs](docs.md) | a page, the docstrings of the API, the code of the examples, snippets and macros, and their checks |
| [Commits and Pull Requests](commits.md) | how a commit is written, and what CI checks on a pull request |
| [Continuous Integration](ci.md) | the workflows, Dependabot, the cache of the builds |
| [Releases](releases.md) | how a version is released, and how a download is verified |

## The way of a change

1. For a change of the API or of the behavior, open an issue first, or ask on Matrix: the discussion saves work on both sides.
2. Make the change on a branch of your fork, with its tests and its docs ([Making a Change](changes.md)).
3. Run the checks of the change on your machine: the unit tests at least ([Making a Change](changes.md#before-a-pull-request)).
4. Open a pull request to `main`. CI builds the module on Linux, macOS and Windows, runs the tests and builds the docs
   ([Commits and Pull Requests](commits.md#what-ci-checks)).
5. A maintainer reviews it and merges it. It is in the next release.

<!-- the section of SECURITY.md, the one place that has it -->
--8<-- "SECURITY.md:reporting"
