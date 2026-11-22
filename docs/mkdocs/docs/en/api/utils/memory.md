---
title: Memory
---
# Memory

The transactions, transfers and outputs that a wallet or a daemon returns are linked both ways, in cycles that the garbage collector
of Python does not see. `free` breaks the links of what an application is done with, so that it is freed
([Memory](../architecture.md#memory)).

::: monero.MoneroUtils.free

::: monero.MoneroUtils.get_blocks_from_txs

::: monero.MoneroUtils.get_blocks_from_transfers

::: monero.MoneroUtils.get_blocks_from_outputs
