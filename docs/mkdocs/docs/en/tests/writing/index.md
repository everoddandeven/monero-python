---
title: Writing Tests
---
# Writing Tests

How the tests are made, and what a new one needs.

| Page | What it has |
| --- | --- |
| [Wallet Tests](wallet.md) | the base class and the classes of the wallet types, the markers of what a type does not do, the conditions |
| [A New Wallet Method](new_wallet_method.md) | the call and the row of the support matrix that a new method of `MoneroWallet` needs |
| [Helpers](helpers.md) | the helpers of `tests/utils` |

## Where a test goes

| What it tests | Where |
| --- | --- |
| a model of the wallet (a query, a transfer, a config...) | `tests/wallet/model/`, in the file of that kind of model |
| a model of the daemon | `tests/daemon/model/` |
| what a wallet does | `tests/wallet/test_<topic>.py`, in the base class if every wallet type has to pass it |
| what the rpc daemon does | `tests/daemon/rpc/test_<topic>.py` |
| `MoneroUtils` | `tests/common/monero_utils/test_<topic>.py` |
| the rpc connection, the errors, what is not about a wallet or a daemon | `tests/common/` |
| a new method of `MoneroWallet` | a call in `tests/utils/wallet_calls.py` and a row in `tests/wallet/wallet_support.yml` ([A New Wallet Method](new_wallet_method.md)) |

## A test class

Every test class extends `BaseTestClass` (`tests/utils/base_test_class.py`) and has a marker, `unit` or `integration`:

```python
from __future__ import annotations

import logging

import pytest
from monero import MoneroUtils

from utils import BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroUtilsAmounts")


@pytest.mark.unit
class TestMoneroUtilsAmounts(BaseTestClass):
    """Monero utilities amounts unit tests."""

    # Can convert between XMR and atomic units
    def test_atomic_unit_conversion(self) -> None:
        assert 1000000000000 == MoneroUtils.xmr_to_atomic_units(1)
        assert 1 == MoneroUtils.atomic_units_to_xmr(1000000000000)
```

CI runs `pytest -m unit` and `pytest -m integration`, so a class with neither marker never runs in CI.

`BaseTestClass` gives each test class four hooks, which a class overrides to prepare and clean up what its tests need, and logs the
start and the end of each test with the time that it took, in the log of the tests and in the one of monero-cpp:

| Hook | When |
| --- | --- |
| `before_all(self)` | once, before the first test of the class |
| `after_all(self)` | once, after the last one |
| `before_each(self, request)` | before each test |
| `after_each(self, request)` | after each test |

An override calls the one of the base class (`super().before_all()`), and is marked with `@override`.

## Conventions

- **Types.** The tests are checked with Pylance in strict mode (`.vscode/settings.json`): every parameter, return value and
  variable has a type, and an override is marked with `@override` from `typing_extensions`.
- **Names.** `test_<what it does>`, as the method of the library that it tests when there is one: `test_get_height_by_date`.
- **A comment** above each test says what it checks, as `# Can start and stop mining`.
- **A logger** for each file, named as its class: `logging.getLogger("TestMoneroWalletMining")`.
