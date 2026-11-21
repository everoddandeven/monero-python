---
title: Monero Utilities
---
# Monero Utilities

[`MoneroUtils`][monero.MoneroUtils] has the functions that need no wallet and no daemon:

| Topic | Functions |
| --- | --- |
| amounts | `xmr_to_atomic_units`, `atomic_units_to_xmr` ([Glossary](glossary.md#amounts)) |
| addresses and keys | `is_valid_address` and `validate_address`, which raises, and the same for the keys, the seed and the payment IDs; `get_integrated_address` |
| payment URIs | `get_payment_uri`, `parse_payment_uri` |
| memory | `free`, which frees the transactions, transfers and outputs that an application is done with ([Memory](architecture.md#memory)) |
| logging | `configure_logging`, `set_log_level`, `set_log_categories`, `log_info` and the other levels |
| binary RPC | `binary_to_json`, `json_to_binary` and the others, for the binary interface of the daemon |

## Logging

monero-cpp and the wallet of monero log what they do, and nothing is written until the logging is configured. The log is the first
place to look when a wallet does not do what it should:

```python
from monero import MoneroUtils

MoneroUtils.configure_logging("monero.log", False)      # to a file, and not to the console
MoneroUtils.set_log_level(1)                            # 0 is the least, 4 the most
MoneroUtils.set_log_categories("*:WARNING,wallet.wallet2:INFO")
```

The categories are the ones of monero: a list of `category:level`, where `*` is every category. The `log_*` functions write to the
same log, for the messages of the application next to the ones of the wallet.

[`GenUtils`][monero.GenUtils] and the comparators are helpers of the tests, which the library exposes as well.

## The classes

::: monero.MoneroUtils

::: monero.GenUtils

## Comparators

::: monero.TxHeightComparator

::: monero.IncomingTransferComparator

::: monero.OutputComparator
