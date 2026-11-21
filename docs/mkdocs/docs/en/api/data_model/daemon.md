---
title: Daemon Data Model
---
# Daemon Data Model

What the methods of a [daemon](../daemon.md) take and return, by topic. The classes of a block and of a transaction are the ones that
the wallets extend ([Wallet Data Model](wallet.md)).

## Blocks and the chain

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroBlockHeader`][monero.MoneroBlockHeader] | the header of a block: height, hash, timestamp, difficulty, reward | [`get_last_block_header`][monero.MoneroDaemon.get_last_block_header], [`get_block_header_by_height`][monero.MoneroDaemon.get_block_header_by_height], [`get_block_headers_by_range`][monero.MoneroDaemon.get_block_headers_by_range] |
| [`MoneroBlock`][monero.MoneroBlock] | a header with its transactions, `txs`, and the one of its miner, `miner_tx` | [`get_block_by_height`][monero.MoneroDaemon.get_block_by_height], [`get_blocks_by_range`][monero.MoneroDaemon.get_blocks_by_range] |
| [`MoneroGetBlocksByHashResult`][monero.MoneroGetBlocksByHashResult], [`MoneroGetBlockHashesResult`][monero.MoneroGetBlockHashesResult] | the blocks, or the hashes, that follow the ones given | [`get_blocks_by_hash`][monero.MoneroDaemon.get_blocks_by_hash], [`get_block_hashes`][monero.MoneroDaemon.get_block_hashes] |
| [`MoneroAltChain`][monero.MoneroAltChain] | a chain that forks from the main one | [`get_alt_chains`][monero.MoneroDaemon.get_alt_chains] |
| [`MoneroHardForkInfo`][monero.MoneroHardForkInfo] | the version of the rules of the chain, and the vote for the next one | [`get_hard_fork_info`][monero.MoneroDaemon.get_hard_fork_info] |
| [`MoneroPruneResult`][monero.MoneroPruneResult] | whether the chain of the daemon is pruned | [`prune_blockchain`][monero.MoneroDaemon.prune_blockchain] |

## Transactions and outputs

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroTx`][monero.MoneroTx] | a transaction: its hash, its fee, its `inputs` and `outputs`, its `block` once it is in one | [`get_tx`][monero.MoneroDaemon.get_tx], [`get_txs`][monero.MoneroDaemon.get_txs], [`get_tx_pool`][monero.MoneroDaemon.get_tx_pool] |
| [`MoneroOutput`][monero.MoneroOutput] | an output of a transaction, with its `tx` | [`get_outputs`][monero.MoneroDaemon.get_outputs] |
| [`MoneroKeyImage`][monero.MoneroKeyImage], [`MoneroKeyImageSpentStatus`][monero.MoneroKeyImageSpentStatus] | the key image of a spent output, and whether it is spent, in a block or in the pool | [`get_key_image_spent_status`][monero.MoneroDaemon.get_key_image_spent_status] |
| [`MoneroSubmitTxResult`][monero.MoneroSubmitTxResult] | what the daemon said of a transaction submitted: relayed, or why not | [`submit_tx_hex`][monero.MoneroDaemon.submit_tx_hex] |
| [`MoneroTxPoolStats`][monero.MoneroTxPoolStats], [`MoneroTxBacklogEntry`][monero.MoneroTxBacklogEntry] | the transactions of the pool, in numbers | [`get_tx_pool_stats`][monero.MoneroDaemon.get_tx_pool_stats], [`get_tx_pool_backlog`][monero.MoneroDaemon.get_tx_pool_backlog] |
| [`MoneroFeeEstimate`][monero.MoneroFeeEstimate] | the fee per byte to pay, by priority | [`get_fee_estimate`][monero.MoneroDaemon.get_fee_estimate] |
| [`MoneroOutputDistributionEntry`][monero.MoneroOutputDistributionEntry], [`MoneroOutputHistogramEntry`][monero.MoneroOutputHistogramEntry] | how the outputs of the chain are distributed, by height and by amount | [`get_output_distribution`][monero.MoneroDaemon.get_output_distribution], [`get_output_histogram`][monero.MoneroDaemon.get_output_histogram] |

## The daemon and its network

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroNetworkType`][monero.MoneroNetworkType] | mainnet, testnet or stagenet ([Glossary](../glossary.md#networks)) | the network of a daemon, of a wallet, of an address |
| [`MoneroVersion`][monero.MoneroVersion] | the version of a daemon, or of a wallet server | [`get_version`][monero.MoneroDaemon.get_version] |
| [`MoneroDaemonInfo`][monero.MoneroDaemonInfo] | the state of the daemon: height, network, connections, size of the chain | [`get_info`][monero.MoneroDaemon.get_info] |
| [`MoneroDaemonSyncInfo`][monero.MoneroDaemonSyncInfo], [`MoneroConnectionSpan`][monero.MoneroConnectionSpan] | how far the daemon is in syncing the chain, and the blocks that it is downloading from its peers | [`get_sync_info`][monero.MoneroDaemon.get_sync_info] |
| [`MoneroPeer`][monero.MoneroPeer], [`MoneroBan`][monero.MoneroBan] | a peer of the daemon, and a peer that it bans | [`get_peers`][monero.MoneroDaemon.get_peers], [`get_peer_bans`][monero.MoneroDaemon.get_peer_bans], [`set_peer_ban`][monero.MoneroDaemon.set_peer_ban] |
| [`MoneroDaemonNetworkStats`][monero.MoneroDaemonNetworkStats] | the traffic of the daemon | [`get_network_stats`][monero.MoneroDaemon.get_network_stats] |
| [`MoneroDaemonUpdateCheckResult`][monero.MoneroDaemonUpdateCheckResult], [`MoneroDaemonUpdateDownloadResult`][monero.MoneroDaemonUpdateDownloadResult] | a new version of monero, and its download | [`check_for_update`][monero.MoneroDaemon.check_for_update], [`download_update`][monero.MoneroDaemon.download_update] |
| [`MoneroRpcPaymentInfo`][monero.MoneroRpcPaymentInfo] | the credits of a daemon that is paid for its RPC: the base of the results that report them | |

## Mining

| Class | What it is | From |
| --- | --- | --- |
| [`MoneroMiningStatus`][monero.MoneroMiningStatus] | whether the daemon mines, with how many threads, to which address | [`get_mining_status`][monero.MoneroDaemon.get_mining_status] |
| [`MoneroBlockTemplate`][monero.MoneroBlockTemplate], [`MoneroMinerData`][monero.MoneroMinerData] | what a miner needs to mine the next block | [`get_block_template`][monero.MoneroDaemon.get_block_template], [`get_miner_data`][monero.MoneroDaemon.get_miner_data] |
| [`MoneroMinerTxSum`][monero.MoneroMinerTxSum] | the coins and the fees of the blocks of a range | [`get_miner_tx_sum`][monero.MoneroDaemon.get_miner_tx_sum] |
| [`MoneroGenerateBlocksResult`][monero.MoneroGenerateBlocksResult] | the blocks mined on demand, on regtest | [`generate_blocks`][monero.MoneroDaemon.generate_blocks] |
| [`MoneroAuxiliaryPow`][monero.MoneroAuxiliaryPow], [`MoneroAddAuxiliaryPowResult`][monero.MoneroAddAuxiliaryPowResult] | merged mining: the proof of work of another chain, added to a block | [`add_auxiliary_pow`][monero.MoneroDaemon.add_auxiliary_pow] |

[`MoneroDaemonListener`][monero.MoneroDaemonListener] is told of the new blocks: [Listening to a Wallet](../../examples/basics/listening_to_a_wallet.md#a-daemon).

::: monero.MoneroNetworkType

::: monero.MoneroVersion

::: monero.MoneroRpcPaymentInfo

::: monero.MoneroBlockHeader

::: monero.MoneroBlock

::: monero.MoneroGetBlocksByHashResult

::: monero.MoneroGetBlockHashesResult

::: monero.MoneroTx

::: monero.MoneroKeyImage

::: monero.MoneroKeyImageSpentStatus

::: monero.MoneroOutput

::: monero.MoneroAltChain

::: monero.MoneroBan

::: monero.MoneroPruneResult

::: monero.MoneroMiningStatus

::: monero.MoneroMinerTxSum

::: monero.MoneroMinerData

::: monero.MoneroBlockTemplate

::: monero.MoneroGenerateBlocksResult

::: monero.MoneroConnectionSpan

::: monero.MoneroPeer

::: monero.MoneroSubmitTxResult

::: monero.MoneroAuxiliaryPow

::: monero.MoneroAddAuxiliaryPowResult

::: monero.MoneroTxBacklogEntry

::: monero.MoneroOutputDistributionEntry

::: monero.MoneroOutputHistogramEntry

::: monero.MoneroTxPoolStats

::: monero.MoneroDaemonUpdateCheckResult

::: monero.MoneroDaemonUpdateDownloadResult

::: monero.MoneroFeeEstimate

::: monero.MoneroDaemonInfo

::: monero.MoneroDaemonSyncInfo

::: monero.MoneroDaemonNetworkStats

::: monero.MoneroHardForkInfo

::: monero.MoneroDaemonListener
