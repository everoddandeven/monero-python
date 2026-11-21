---
title: Continuous Integration
---
# Continuous Integration

The workflows of CI are in [.github/workflows](https://github.com/libmonero/monero-python/tree/main/.github/workflows). Each one says,
in its comments, what it does and why.

## The workflows

| Workflow | Runs on | What it does |
| --- | --- | --- |
| CI (`ci.yml`) | every push to `main`, the pull requests that change the code | calls the three builds, runs the unit tests on each platform and the integration tests on Linux, merges the coverage; on `main`, publishes the docs |
| Build Linux, Build macOS, Build Windows | called by CI | the module of each platform: on Linux with the coverage, and the lint of the bindings; on macOS and Windows, the wheels |
| Docs (`docs.yml`) | the pull requests that change the docs, the stubs or the README; called by CI on `main` | checks the code of the examples, builds the site with `--strict`; on `main`, publishes it with the coverage reports |
| Build Debian Packages (`build-deb.yml`) | every push to `main`, the pull requests that change the packaging; called by Release | the deb packages, in a container of each release of Debian and Ubuntu, on amd64, arm64 and armhf |
| Lint workflows (`lint-workflows.yml`) | the pushes and pull requests that change `.github` | actionlint and zizmor on the workflows |
| Codacy Coverage Reporter (`codacy.yml`) | the end of each run of CI | sends the coverage of the run to Codacy |
| Release (`release.yml`) | a tag `v*` | the draft of a release, with its packages ([Releases](releases.md)) |

A pull request that only changes the docs or the README does not run CI: the Docs workflow checks it.

## Dependabot

Dependabot proposes the updates once a week, a week after they are published. Each file of versions has its own pull request:

| What | File | Commit prefix |
| --- | --- | --- |
| the actions of the workflows | `.github/workflows/*.yml`, pinned to a commit | `ci` |
| the tools of the build | `requirements-build.txt` (pybind11 stays at 2.x) | `build` |
| the tools of the tests | `tests/requirements.txt` | `test` |
| the tools of the docs | `docs/mkdocs/requirements.in`, mkdocstrings and its parts in a pull request of their own | `docs` |

Its pull requests run the checks of the files that they change, as any other: an update that breaks the build, the tests or the docs
fails there.

<!-- the notes of the cache of the builds, docs/ci-ccache.md, the one place that has them -->
--8<-- "docs/ci-ccache.md"
