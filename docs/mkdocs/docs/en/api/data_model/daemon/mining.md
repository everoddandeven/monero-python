---
title: Mining
---
# Mining

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroMiningStatus`][monero.MoneroMiningStatus] | whether the daemon mines, with how many threads, to which address | [`get_mining_status`][monero.MoneroDaemon.get_mining_status] |
| [`MoneroBlockTemplate`][monero.MoneroBlockTemplate], [`MoneroMinerData`][monero.MoneroMinerData] | what a miner needs to mine the next block | [`get_block_template`][monero.MoneroDaemon.get_block_template], [`get_miner_data`][monero.MoneroDaemon.get_miner_data] |
| [`MoneroMinerTxSum`][monero.MoneroMinerTxSum] | the coins and the fees of the blocks of a range | [`get_miner_tx_sum`][monero.MoneroDaemon.get_miner_tx_sum] |
| [`MoneroGenerateBlocksResult`][monero.MoneroGenerateBlocksResult] | the blocks mined on demand, on regtest | [`generate_blocks`][monero.MoneroDaemon.generate_blocks] |
| [`MoneroAuxiliaryPow`][monero.MoneroAuxiliaryPow], [`MoneroAddAuxiliaryPowResult`][monero.MoneroAddAuxiliaryPowResult] | merged mining: the proof of work of another chain, added to a block | [`add_auxiliary_pow`][monero.MoneroDaemon.add_auxiliary_pow] |

::: monero.MoneroMiningStatus

::: monero.MoneroBlockTemplate

::: monero.MoneroMinerData

::: monero.MoneroMinerTxSum

::: monero.MoneroGenerateBlocksResult

::: monero.MoneroAuxiliaryPow

::: monero.MoneroAddAuxiliaryPowResult
