---
title: Monero Utilities
---
# Monero Utilities

[`MoneroUtils`][monero.MoneroUtils] has the functions that need no wallet and no daemon, by topic:

| Page | Functions |
| --- | --- |
| [Amounts](amounts.md) | `xmr_to_atomic_units`, `atomic_units_to_xmr` |
| [Addresses and Keys](addresses.md) | `is_valid_address`, `validate_address`, `get_integrated_address`, `is_valid_private_view_key`, ... |
| [Payment URIs](payment_uris.md) | `get_payment_uri`, `parse_payment_uri` |
| [Memory](memory.md) | `free`, `get_blocks_from_txs`, `get_blocks_from_transfers`, `get_blocks_from_outputs` |
| [Logging](logging.md) | `configure_logging`, `set_log_level`, `set_log_categories`, `log_trace`, ... |
| [Binary RPC](binary.md) | `dict_to_binary`, `binary_to_dict`, `json_to_binary`, `binary_to_json`, ... |
| [Test Helpers](helpers.md) | `GenUtils` and the comparators, which the tests use |

::: monero.MoneroUtils
    options:
      members: [get_version, get_ring_size]
