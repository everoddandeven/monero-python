---
title: Installation
---
# Installation

The prebuilt packages of a release, for the system or a Python environment.

--8<-- "README.md:installation"

## Which file

| System | File | Python |
| --- | --- | --- |
| Debian 12 (bookworm) | `python3-monero_<version>-1bookworm1_<arch>.deb` | the Python 3 of the system, 3.11 |
| Debian 13 (trixie) | `python3-monero_<version>-1trixie1_<arch>.deb` | the Python 3 of the system, 3.13 |
| Ubuntu 22.04 (jammy) | `python3-monero_<version>-1jammy1_<arch>.deb` | the Python 3 of the system, 3.10 |
| Ubuntu 24.04 (noble) | `python3-monero_<version>-1noble1_<arch>.deb` | the Python 3 of the system, 3.12 |
| macOS on Apple silicon | `monero-<version>-cp<python>-cp<python>-macosx_<macos>_arm64.whl` | the one of the name: `cp314` is Python 3.14 |
| macOS on Intel | `monero-<version>-cp<python>-cp<python>-macosx_<macos>_x86_64.whl` | the one of the name |
| Windows | `monero-<version>-cp<python>-cp<python>-win_amd64.whl` | the one of the name: `cp313` is Python 3.13 |

`<arch>` is the one that `dpkg --print-architecture` prints: `amd64`, `arm64` or `armhf`.

A wheel is built for one version of Python, and `pip` refuses it on any other: *is not a supported wheel on this platform*. Install it with
the Python of its name, in a virtual environment of that Python:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
pip install monero-0.9.11-cp314-cp314-macosx_15_0_arm64.whl
```

The `<macos>` of a wheel is the oldest version of macOS that it runs on. The libraries that the module needs are in the wheel, and the
deb package depends on the ones of the system, which `apt` installs with it: install it with `apt install ./<file>`, not with
`dpkg -i`.

For a version of Python, a system or an architecture that has no package, [build it from source](build_linux_macos.md).

## Checking the download

--8<-- "SECURITY.md:provenance"

`SHA256SUMS` lists every file of the release: with only some of them downloaded, `sha256sum -c --ignore-missing SHA256SUMS` checks
those.

## Checking the installation

```bash
python3 -c "import monero; print(monero.__file__); print(monero.MoneroUtils.get_version())"
```

prints where the module is and its version.

## The other `monero` package

The package [monero](https://pypi.org/project/monero/){ target="_blank" rel="noopener" } of PyPI is another library, monero-python of
monero-ecosystem, which is imported as `monero` as well. The two can not be installed in the same environment: `pip install monero`
installs that one, not this.
