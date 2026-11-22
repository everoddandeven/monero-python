---
title: Transactions and Outputs
---
# Transactions and Outputs

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroTx`][monero.MoneroTx] | a transaction: its hash, its fee, its `inputs` and `outputs`, its `block` once it is in one | [`get_tx`][monero.MoneroDaemon.get_tx], [`get_txs`][monero.MoneroDaemon.get_txs], [`get_tx_pool`][monero.MoneroDaemon.get_tx_pool] |
| [`MoneroOutput`][monero.MoneroOutput] | an output of a transaction, with its `tx` | [`get_outputs`][monero.MoneroDaemon.get_outputs] |
| [`MoneroKeyImage`][monero.MoneroKeyImage], [`MoneroKeyImageSpentStatus`][monero.MoneroKeyImageSpentStatus] | the key image of a spent output, and whether it is spent, in a block or in the pool | [`get_key_image_spent_status`][monero.MoneroDaemon.get_key_image_spent_status] |
| [`MoneroSubmitTxResult`][monero.MoneroSubmitTxResult] | what the daemon said of a transaction submitted: relayed, or why not | [`submit_tx_hex`][monero.MoneroDaemon.submit_tx_hex] |
| [`MoneroTxPoolStats`][monero.MoneroTxPoolStats], [`MoneroTxBacklogEntry`][monero.MoneroTxBacklogEntry] | the transactions of the pool, in numbers | [`get_tx_pool_stats`][monero.MoneroDaemon.get_tx_pool_stats], [`get_tx_pool_backlog`][monero.MoneroDaemon.get_tx_pool_backlog] |
| [`MoneroFeeEstimate`][monero.MoneroFeeEstimate] | the fee per byte to pay, by priority | [`get_fee_estimate`][monero.MoneroDaemon.get_fee_estimate] |
| [`MoneroOutputDistributionEntry`][monero.MoneroOutputDistributionEntry], [`MoneroOutputHistogramEntry`][monero.MoneroOutputHistogramEntry] | how the outputs of the chain are distributed, by height and by amount | [`get_output_distribution`][monero.MoneroDaemon.get_output_distribution], [`get_output_histogram`][monero.MoneroDaemon.get_output_histogram] |

::: monero.MoneroTx

::: monero.MoneroOutput

::: monero.MoneroKeyImage

::: monero.MoneroKeyImageSpentStatus

::: monero.MoneroSubmitTxResult

::: monero.MoneroTxPoolStats

::: monero.MoneroTxBacklogEntry

::: monero.MoneroFeeEstimate

::: monero.MoneroOutputDistributionEntry

::: monero.MoneroOutputHistogramEntry
