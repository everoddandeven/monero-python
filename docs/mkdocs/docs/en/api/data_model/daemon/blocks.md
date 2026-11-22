---
title: Blocks and the Chain
---
# Blocks and the Chain

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroBlockHeader`][monero.MoneroBlockHeader] | the header of a block: height, hash, timestamp, difficulty, reward | [`get_last_block_header`][monero.MoneroDaemon.get_last_block_header], [`get_block_header_by_height`][monero.MoneroDaemon.get_block_header_by_height], [`get_block_headers_by_range`][monero.MoneroDaemon.get_block_headers_by_range] |
| [`MoneroBlock`][monero.MoneroBlock] | a header with its transactions, `txs`, and the one of its miner, `miner_tx` | [`get_block_by_height`][monero.MoneroDaemon.get_block_by_height], [`get_blocks_by_range`][monero.MoneroDaemon.get_blocks_by_range] |
| [`MoneroGetBlocksByHashResult`][monero.MoneroGetBlocksByHashResult], [`MoneroGetBlockHashesResult`][monero.MoneroGetBlockHashesResult] | the blocks, or the hashes, that follow the ones given | [`get_blocks_by_hash`][monero.MoneroDaemon.get_blocks_by_hash], [`get_block_hashes`][monero.MoneroDaemon.get_block_hashes] |
| [`MoneroAltChain`][monero.MoneroAltChain] | a chain that forks from the main one | [`get_alt_chains`][monero.MoneroDaemon.get_alt_chains] |
| [`MoneroHardForkInfo`][monero.MoneroHardForkInfo] | the version of the rules of the chain, and the vote for the next one | [`get_hard_fork_info`][monero.MoneroDaemon.get_hard_fork_info] |
| [`MoneroPruneResult`][monero.MoneroPruneResult] | whether the chain of the daemon is pruned | [`prune_blockchain`][monero.MoneroDaemon.prune_blockchain] |

::: monero.MoneroBlockHeader

::: monero.MoneroBlock

::: monero.MoneroGetBlocksByHashResult

::: monero.MoneroGetBlockHashesResult

::: monero.MoneroAltChain

::: monero.MoneroHardForkInfo

::: monero.MoneroPruneResult
